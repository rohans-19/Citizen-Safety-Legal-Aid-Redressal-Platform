import { useState, useEffect, useRef } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { generateBlindingFactor, sha256 } from './zkp_auth.js'
import { api } from './api.js'

/**
 * ZKPWallet
 * Implements the Tehsildar Verification Flow (ZKP Issuance).
 * Citizens request verification of their income/identity via the Tehsildar.
 * Once approved, they pull the cryptographically signed credential to generate ZKP.
 */
export default function ZKPWallet() {
  const [aadhaar, setAadhaar]           = useState('')
  const [income, setIncome]             = useState('')
  const [pseudonym, setPseudonym]       = useState('')
  const [status, setStatus]             = useState('idle')     // idle | polling | approved
  const [proof, setProof]               = useState(null)       // { commitment, eligible, aadhaarHash, blindingFactor, token }
  const [verifyResult, setVerifyResult] = useState(null)    // { valid, message }
  const [loading, setLoading]           = useState(false)
  const [verifying, setVerifying]       = useState(false)
  const [copied, setCopied]             = useState(false)
  const [error, setError]               = useState('')

  const pollingRef = useRef(null)

  // Initialize pseudonym and restore previous verification session
  useEffect(() => {
    let p = sessionStorage.getItem('citizen_pseudonym')
    if (!p) {
      p = 'Citizen-' + Math.random().toString(36).substring(2, 6).toUpperCase()
      sessionStorage.setItem('citizen_pseudonym', p)
    }
    setPseudonym(p)

    // Check if there is an existing approved ZKP credential in session storage
    const storedCommitment = sessionStorage.getItem('zkp_commitment')
    if (storedCommitment) {
      setStatus('approved')
      setProof({
        commitment:     storedCommitment,
        eligible:       sessionStorage.getItem('zkp_eligible') === 'true',
        aadhaarHash:    sessionStorage.getItem('zkp_aadhaar_hash') || '',
        blindingFactor: sessionStorage.getItem('zkp_bf') || '',
        token:          sessionStorage.getItem('zkp_token') || ''
      })
    }
  }, [])

  // Clear polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  const handleRequestVerification = async () => {
    setError('')
    if (!aadhaar || aadhaar.length < 12) {
      setError('Please enter a valid 12-digit Aadhaar Card Number.')
      return
    }
    const incomeNum = parseInt(income, 10)
    if (!income || isNaN(incomeNum) || incomeNum < 0) {
      setError('Please enter a valid annual income (in INR).')
      return
    }

    setLoading(true)
    try {
      const aadhaarHash = await sha256(aadhaar)
      const res = await api.requestVerification(pseudonym, aadhaarHash, incomeNum, aadhaar)
      
      if (res && res.success) {
        setStatus('polling')
        startPolling(aadhaarHash)
      } else {
        setError(res?.message || 'Failed to submit verification request.')
      }
    } catch (err) {
      setError('Error dispatching request. Please verify backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const startPolling = (aadhaarHash) => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    
    pollingRef.current = setInterval(async () => {
      try {
        const res = await api.checkVerificationStatus(pseudonym)
        if (res && res.status === 'approved' && res.credential_token) {
          clearInterval(pollingRef.current)
          pollingRef.current = null
          await processApprovedCredential(res.credential_token, aadhaarHash)
        }
      } catch (err) {
        console.error('Error polling verification status:', err)
      }
    }, 4000)
  }

  const processApprovedCredential = async (token, aadhaarHash) => {
    try {
      // Decode credential payload from the token
      const tokenBytes = atob(token.replace(/-/g, '+').replace(/_/g, '/'))
      const tokenData = JSON.parse(tokenBytes)
      const payload = tokenData.payload

      // Generate blinding factor and build commitment
      const blindingFactor = generateBlindingFactor()
      // Commitment C = SHA256(aadhaar_hash + ":" + blindingFactor)
      const commitmentMsg = `${payload.aadhaar_hash}:${blindingFactor}`
      const commitment = await sha256(commitmentMsg)

      // Calculate SHA256 preimages for the server proof verification check
      const valueHash = await sha256(payload.aadhaar_hash)
      const blindingHash = await sha256(blindingFactor)

      // Persist to session storage so process-voice can read it automatically
      sessionStorage.setItem('zkp_commitment', commitment)
      sessionStorage.setItem('zkp_bf', blindingFactor)
      sessionStorage.setItem('zkp_eligible', String(payload.eligible))
      sessionStorage.setItem('zkp_aadhaar_hash', payload.aadhaar_hash)
      sessionStorage.setItem('zkp_value_hash', valueHash)
      sessionStorage.setItem('zkp_blinding_hash', blindingHash)
      sessionStorage.setItem('zkp_token', token)

      setProof({
        commitment,
        eligible: payload.eligible,
        aadhaarHash: payload.aadhaar_hash,
        blindingFactor,
        token
      })
      setStatus('approved')
    } catch (err) {
      setError('Failed to process approved credential.')
      setStatus('idle')
    }
  }

  const handleVerify = async () => {
    if (!proof) return
    setVerifying(true)
    setVerifyResult(null)
    try {
      const valueHash = sessionStorage.getItem('zkp_value_hash')
      const blindingHash = sessionStorage.getItem('zkp_blinding_hash')
      const result = await api.verifyZkp(proof.commitment, valueHash, blindingHash)
      setVerifyResult(result)
    } catch {
      setVerifyResult({ valid: false, message: 'Verification request failed.' })
    } finally {
      setVerifying(false)
    }
  }

  const handleCopy = () => {
    if (proof?.commitment) {
      navigator.clipboard.writeText(proof.commitment)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleReset = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    setProof(null)
    setVerifyResult(null)
    setAadhaar('')
    setIncome('')
    setError('')
    setStatus('idle')
    sessionStorage.removeItem('zkp_bf')
    sessionStorage.removeItem('zkp_commitment')
    sessionStorage.removeItem('zkp_eligible')
    sessionStorage.removeItem('zkp_aadhaar_hash')
    sessionStorage.removeItem('zkp_value_hash')
    sessionStorage.removeItem('zkp_blinding_hash')
    sessionStorage.removeItem('zkp_token')
  }

  const qrData = proof
    ? JSON.stringify({ commitment: proof.commitment, token: proof.token })
    : ''

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-base font-semibold text-gray-800">Identity & Eligibility Wallet</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Your Pseudonym: <span className="font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">{pseudonym}</span>
        </p>
      </div>

      {status === 'idle' && (
        /* ── Input form ── */
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-100 rounded px-3 py-2.5">
            <p className="text-xs text-blue-800 font-semibold">Tehsildar Verification Flow</p>
            <p className="text-xs text-blue-600 mt-1 leading-relaxed">
              To verify eligibility for free legal aid, submit your details below. This will email a secure approval request to the respective Tehsildar's office. Once approved, the Tehsildar signs an official credential token that your wallet imports to generate a Zero-Knowledge Proof.
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Aadhaar Card Number
              </label>
              <input
                type="text"
                maxLength="12"
                value={aadhaar}
                onChange={e => setAadhaar(e.target.value.replace(/\D/g, ''))}
                placeholder="e.g. 548912047783"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Annual Income (INR)
              </label>
              <input
                type="number"
                value={income}
                onChange={e => setIncome(e.target.value)}
                placeholder="e.g. 45000"
                min="0"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>



            <button
              onClick={handleRequestVerification}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-semibold py-2 rounded shadow transition-all"
            >
              {loading ? 'Dispatched Request…' : 'Request Tehsildar Verification'}
            </button>

            {error && <p className="text-xs text-red-500 font-medium mt-1">{error}</p>}
          </div>

          <p className="text-xs text-gray-400">
            Eligibility Threshold: INR 50,000 / year.
          </p>
        </div>
      )}

      {status === 'polling' && (
        /* ── Polling / Waiting for Tehsildar view ── */
        <div className="border border-blue-100 bg-blue-50 rounded p-6 flex flex-col items-center gap-4 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
          <div>
            <p className="text-sm font-semibold text-blue-900">Awaiting Tehsildar Approval</p>
            <p className="text-xs text-blue-700 mt-1 leading-relaxed max-w-sm">
              We have dispatched a secure verification request to the Tehsildar's office. 
              Once the Tehsildar reviews and approves the request, your wallet will automatically fetch the issued credential token.
            </p>
          </div>
          <button
            onClick={handleReset}
            className="text-xs text-gray-500 hover:text-gray-700 underline mt-2"
          >
            Cancel Request
          </button>
        </div>
      )}

      {status === 'approved' && proof && (
        /* ── Credential Approved & Proof Active view ── */
        <div className="space-y-4 screen-fade">
          <div className={`border rounded p-3 flex items-center gap-2.5 ${
            proof.eligible
              ? 'border-green-300 bg-green-50'
              : 'border-red-300 bg-red-50'
          }`}>
            <span className="text-lg">{proof.eligible ? '✅' : '❌'}</span>
            <div>
              <p className={`text-sm font-bold ${proof.eligible ? 'text-green-800' : 'text-red-800'}`}>
                {proof.eligible ? 'ZKP Credential Active' : 'Ineligible: Above Income Threshold'}
              </p>
              <p className="text-xs text-gray-600 leading-normal">
                {proof.eligible 
                  ? 'Your income has been verified by the Tehsildar. Zero-Knowledge Proofs are enabled for your reports.' 
                  : 'You do not satisfy the criteria for free legal aid. Verification is revoked.'}
              </p>
            </div>
          </div>

          {proof.eligible && (
            <>
              {/* QR Code */}
              <div className="border border-gray-200 rounded p-4 flex flex-col items-center gap-3 bg-white shadow-sm">
                <QRCodeSVG
                  value={qrData}
                  size={160}
                  level="M"
                  includeMargin={false}
                />
                <p className="text-xs text-gray-500 text-center leading-normal max-w-xs">
                  Scan this QR code at any legal aid office to prove your verified credential offline.
                </p>
              </div>

              {/* Commitment hash */}
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-gray-600">
                  Your ZKP Commitment
                </label>
                <div className="flex items-center gap-2">
                  <code className="flex-1 border border-gray-200 rounded bg-gray-50 px-2 py-1.5 text-xs text-gray-600 break-all font-mono">
                    {proof.commitment}
                  </code>
                  <button
                    onClick={handleCopy}
                    className="text-xs text-blue-600 hover:text-blue-800 border border-blue-200 bg-blue-50 px-2.5 py-1.5 rounded font-semibold whitespace-nowrap"
                  >
                    {copied ? '✓ Copied' : 'Copy'}
                  </button>
                </div>
              </div>

              {/* Verify with backend */}
              <div className="flex items-center gap-3">
                <button
                  onClick={handleVerify}
                  disabled={verifying}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold text-xs px-3 py-2 rounded border border-gray-300 transition-colors"
                >
                  {verifying ? 'Verifying with Server…' : 'Test Verification'}
                </button>
                <button
                  onClick={handleReset}
                  className="text-xs text-red-500 hover:text-red-700 font-semibold"
                >
                  Reset Wallet
                </button>
              </div>

              {/* Verification result */}
              {verifyResult && (
                <div className={`border rounded px-3 py-2.5 text-xs font-medium ${
                  verifyResult.valid
                    ? 'border-green-300 bg-green-50 text-green-800'
                    : 'border-red-300 bg-red-50 text-red-800'
                }`}>
                  {verifyResult.valid ? '✔ ' : '✗ '}
                  {verifyResult.message}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
