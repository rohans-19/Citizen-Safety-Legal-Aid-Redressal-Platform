import { useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { buildProof } from './zkp_auth.js'
import { api } from './api.js'

/**
 * ZKPWallet
 * Allows the user to input their income, generate a Pedersen commitment,
 * display it as a QR code, and verify it against Member B's backend.
 */
export default function ZKPWallet() {
  const [income, setIncome]           = useState('')
  const [proof, setProof]             = useState(null)    // { commitment, blindingFactor, rangeProof, eligible }
  const [verifyResult, setVerifyResult] = useState(null)  // { valid, message }
  const [loading, setLoading]         = useState(false)
  const [verifying, setVerifying]     = useState(false)
  const [copied, setCopied]           = useState(false)
  const [error, setError]             = useState('')

  const handleGenerate = async () => {
    const num = parseInt(income, 10)
    if (!income || isNaN(num) || num < 0) {
      setError('Please enter a valid annual income (in INR).')
      return
    }
    setError('')
    setLoading(true)
    setVerifyResult(null)

    try {
      const result = await buildProof(num)
      setProof(result)
      // Persist blinding factor in sessionStorage (wiped on shake)
      sessionStorage.setItem('zkp_bf', result.blindingFactor)
      sessionStorage.setItem('zkp_commitment', result.commitment)
    } catch {
      setError('Failed to generate proof. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    if (!proof) return
    setVerifying(true)
    try {
      const result = await api.verifyZkp(proof.commitment, proof.blindingFactor)
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
    setProof(null)
    setVerifyResult(null)
    setIncome('')
    setError('')
    sessionStorage.removeItem('zkp_bf')
    sessionStorage.removeItem('zkp_commitment')
  }

  // QR code data — JSON payload that Member B's verifier reads
  const qrData = proof
    ? JSON.stringify({ commitment: proof.commitment, range: proof.rangeProof })
    : ''

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-base font-semibold text-gray-800">Identity Proof Wallet</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Generate an eligibility proof without sharing your Aadhaar or personal documents.
        </p>
      </div>

      {!proof ? (
        /* ── Input form ── */
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded px-3 py-2.5">
            <p className="text-xs text-blue-700 font-medium">How this works</p>
            <p className="text-xs text-blue-600 mt-0.5">
              Enter your annual income. We generate a cryptographic commitment (SHA-256 hash)
              that proves you meet the income threshold without revealing the actual amount.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Annual Income (INR)
            </label>
            <div className="flex gap-2">
              <input
                id="income-input"
                type="number"
                value={income}
                onChange={e => setIncome(e.target.value)}
                placeholder="e.g. 42000"
                min="0"
                className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
              <button
                id="btn-generate-proof"
                onClick={handleGenerate}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-medium px-4 py-2 rounded border border-blue-700"
              >
                {loading ? 'Generating…' : 'Generate Proof'}
              </button>
            </div>
            {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
          </div>

          <p className="text-xs text-gray-400">
            Eligibility threshold: ₹50,000 / year (Below Poverty Line criterion)
          </p>
        </div>
      ) : (
        /* ── Proof generated view ── */
        <div className="space-y-4 screen-fade">
          {/* Eligibility badge */}
          <div className={`border rounded px-3 py-2 flex items-center gap-2 ${
            proof.eligible
              ? 'border-green-300 bg-green-50'
              : 'border-red-300 bg-red-50'
          }`}>
            <span className="text-lg">{proof.eligible ? '✅' : '❌'}</span>
            <div>
              <p className={`text-sm font-semibold ${proof.eligible ? 'text-green-700' : 'text-red-700'}`}>
                {proof.eligible ? 'Eligible for Legal Aid' : 'Above Income Threshold'}
              </p>
              <p className="text-xs text-gray-500">
                Income eligibility proven offline. No Aadhaar data shared.
              </p>
            </div>
          </div>

          {/* QR Code */}
          <div className="border border-gray-200 rounded p-4 flex flex-col items-center gap-3">
            <QRCodeSVG
              id="zkp-qr-code"
              value={qrData}
              size={180}
              level="M"
              includeMargin={false}
            />
            <p className="text-xs text-gray-500 text-center">
              Scan this QR to verify eligibility at an authority office
            </p>
          </div>

          {/* Commitment hash */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Commitment Hash (SHA-256)
            </label>
            <div className="flex items-center gap-2">
              <code className="flex-1 border border-gray-200 rounded bg-gray-50 px-2 py-1.5 text-xs text-gray-600 break-all font-mono">
                {proof.commitment}
              </code>
              <button
                onClick={handleCopy}
                className="text-xs text-blue-600 hover:text-blue-800 border border-blue-200 rounded px-2 py-1.5 whitespace-nowrap"
              >
                {copied ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Verify with backend */}
          <div className="flex items-center gap-3">
            <button
              id="btn-verify-zkp"
              onClick={handleVerify}
              disabled={verifying}
              className="border border-gray-300 hover:border-blue-400 text-gray-700 hover:text-blue-600 text-sm px-3 py-1.5 rounded"
            >
              {verifying ? 'Verifying…' : 'Verify with Server'}
            </button>
            <button
              onClick={handleReset}
              className="text-xs text-gray-400 hover:text-gray-600 underline"
            >
              Reset
            </button>
          </div>

          {/* Verification result */}
          {verifyResult && (
            <div className={`border rounded px-3 py-2 text-sm ${
              verifyResult.valid
                ? 'border-green-300 bg-green-50 text-green-700'
                : 'border-red-300 bg-red-50 text-red-700'
            }`}>
              {verifyResult.valid ? '✓ ' : '✗ '}
              {verifyResult.message}
              {verifyResult._mock && (
                <span className="text-xs text-gray-400 ml-1">(mock)</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
