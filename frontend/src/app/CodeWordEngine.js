/**
 * CodeWordEngine.js
 *
 * On-device code word detection using Levenshtein distance fuzzy matching.
 * No ML model needed in browser — we match against a pre-defined list of
 * trigger phrases across English, Kannada, and Hindi.
 *
 * Usage:
 *   import { checkCodeWords } from './CodeWordEngine.jsx'
 *   const result = checkCodeWords("help me please")
 *   // → { triggered: true, matchedWord: "help me", score: 1.0 }
 */

import codewords from './codewords.json'

const SIMILARITY_THRESHOLD = 0.70  // 0–1, minimum score to trigger

// Flatten all code words from all languages into one list
const ALL_CODEWORDS = [
  ...codewords.english,
  ...codewords.kannada,
  ...codewords.hindi,
]

/**
 * Compute Levenshtein distance between two strings
 */
function levenshtein(a, b) {
  const m = a.length, n = b.length
  const dp = Array.from({ length: m + 1 }, (_, i) =>
    Array.from({ length: n + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
  )
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = a[i - 1] === b[j - 1]
        ? dp[i - 1][j - 1]
        : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    }
  }
  return dp[m][n]
}

/**
 * Similarity score: 1 = identical, 0 = completely different
 */
function similarity(a, b) {
  const maxLen = Math.max(a.length, b.length)
  if (maxLen === 0) return 1
  return 1 - levenshtein(a.toLowerCase(), b.toLowerCase()) / maxLen
}

/**
 * Check if transcript contains any code word
 * @param {string} transcript — live transcription text
 * @returns {{ triggered: boolean, matchedWord: string | null, score: number }}
 */
export function checkCodeWords(transcript) {
  if (!transcript || transcript.trim().length === 0) {
    return { triggered: false, matchedWord: null, score: 0 }
  }

  const normalised = transcript.toLowerCase().trim()
  let bestScore = 0
  let bestWord  = null

  for (const word of ALL_CODEWORDS) {
    // Check full phrase similarity
    const score = similarity(normalised, word.toLowerCase())
    if (score > bestScore) {
      bestScore = score
      bestWord  = word
    }
    // Also check if the transcript contains the code word as a substring
    if (normalised.includes(word.toLowerCase())) {
      return { triggered: true, matchedWord: word, score: 1.0 }
    }
  }

  if (bestScore >= SIMILARITY_THRESHOLD) {
    return { triggered: true, matchedWord: bestWord, score: bestScore }
  }

  return { triggered: false, matchedWord: null, score: bestScore }
}
