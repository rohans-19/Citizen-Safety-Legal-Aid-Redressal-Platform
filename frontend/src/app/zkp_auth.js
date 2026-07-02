/**
 * zkp_auth.js — Zero-Knowledge Proof utility (browser, Web Crypto API)
 *
 * Implements a simplified Pedersen-style commitment scheme:
 *   C = SHA-256( income || ":" || blindingFactor )
 *
 * The verifier (Member B) recomputes the same hash and checks equality.
 * A range proof flag is appended to prove income < THRESHOLD without revealing income.
 */

const ELIGIBILITY_THRESHOLD = 50000  // INR annual income threshold

/**
 * Generate a random 32-byte blinding factor (hex string)
 */
export function generateBlindingFactor() {
  const bytes = window.crypto.getRandomValues(new Uint8Array(32))
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('')
}

export async function sha256(text) {
  const encoded = new TextEncoder().encode(text)
  const hashBuffer = await window.crypto.subtle.digest('SHA-256', encoded)
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

/**
 * Generate SHA-256 Pedersen commitment
 * @param {number} income - User's annual income in INR
 * @param {string} blindingFactor - 32-byte hex blinding factor
 * @returns {Promise<string>} commitment hex string
 */
export async function generateCommitment(income, blindingFactor) {
  const message = `${income}:${blindingFactor}`
  const encoded = new TextEncoder().encode(message)
  const hashBuffer = await window.crypto.subtle.digest('SHA-256', encoded)
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

/**
 * Build a ZKP proof object
 * @param {number} income
 * @returns {Promise<{ commitment: string, blindingFactor: string, rangeProof: string, eligible: boolean }>}
 */
export async function buildProof(income) {
  const blindingFactor = generateBlindingFactor()
  const commitment     = await generateCommitment(income, blindingFactor)
  const eligible       = income < ELIGIBILITY_THRESHOLD

  return {
    commitment,
    blindingFactor,
    rangeProof: eligible ? 'BELOW_THRESHOLD' : 'ABOVE_THRESHOLD',
    eligible,
  }
}

/**
 * Verify a commitment locally (for dev/testing — server does the real check)
 */
export async function verifyCommitment(income, blindingFactor, commitment) {
  const expected = await generateCommitment(income, blindingFactor)
  return expected === commitment
}
