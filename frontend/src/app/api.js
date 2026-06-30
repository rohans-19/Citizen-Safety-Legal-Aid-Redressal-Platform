/**
 * api.js — All backend API calls with automatic mock fallback
 *
 * When VITE_BACKEND_URL is not reachable (backend offline / dev mode),
 * functions return realistic mock responses so the UI works standalone.
 *
 * Endpoints (per project_guide.md):
 *   POST /process-voice    — Main complaint processing
 *   GET  /detect-threat    — AST threat detection (polling)
 *   POST /verify-zkp       — Pedersen commitment verification
 *   GET  /health           — Backend health check
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const TIMEOUT_MS  = 5000

// Mock responses used when backend is unreachable
const MOCK = {
  processVoice: {
    incident_type: 'caste_discrimination',
    law_matched:   'SC/ST (PoA) Act, 1989 — Section 3(1)(v)',
    district:      'Bidar',
    taluk:         'Humnabad',
    severity:      0.82,
    routed_to:     'One Stop Centre, Bidar District',
    authority:     'Dist. Social Welfare Officer, Bidar',
    pdf_url:       null,   // no real PDF in mock mode
    complaint_id:  'MOCK-' + Math.floor(Math.random() * 90000 + 10000),
    timestamp:     new Date().toISOString(),
    _mock:         true,
  },
  detectThreat: {
    is_threat:  false,
    labels:     [],
    confidence: 0.0,
    _mock:      true,
  },
  verifyZkp: {
    valid:   true,
    message: 'Commitment verified successfully (mock)',
    _mock:   true,
  },
}

// Internal fetch wrapper with timeout + mock fallback
async function callApi(url, options = {}, mockResponse) {
  const controller = new AbortController()
  const timerId    = setTimeout(() => controller.abort(), TIMEOUT_MS)
  try {
    const res = await fetch(url, { ...options, signal: controller.signal })
    clearTimeout(timerId)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    clearTimeout(timerId)
    console.warn(`[API] Offline/error for ${url} — using mock.`, err.message)
    return { ...mockResponse, _mock: true }
  }
}

export const api = {
  /**
   * POST /process-voice
   * Sends audio blob + transcript to the backend agent swarm
   */
  async processVoice(audioBlob, transcript, language = 'kn') {
    const formData = new FormData()
    formData.append('audio',      audioBlob, 'recording.webm')
    formData.append('transcript', transcript)
    formData.append('language',   language)

    return callApi(
      `${BACKEND_URL}/process-voice`,
      { method: 'POST', body: formData },
      MOCK.processVoice
    )
  },

  /**
   * GET /detect-threat
   * Polled every 5s by ThreatMonitor to check for AST-detected threats
   */
  async detectThreat() {
    return callApi(
      `${BACKEND_URL}/detect-threat`,
      { method: 'GET' },
      MOCK.detectThreat
    )
  },

  /**
   * POST /verify-zkp
   * Verifies a Pedersen commitment from the ZKP wallet
   */
  async verifyZkp(commitment, blindingFactor) {
    return callApi(
      `${BACKEND_URL}/verify-zkp`,
      {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          commitment,
          blinding_factor: blindingFactor,
          claimed_range:   'BELOW_THRESHOLD',
        }),
      },
      MOCK.verifyZkp
    )
  },

  /**
   * GET /health — check if backend is reachable
   * Returns true/false, used to show connection status
   */
  async healthCheck() {
    try {
      const controller = new AbortController()
      setTimeout(() => controller.abort(), 3000)
      const res = await fetch(`${BACKEND_URL}/health`, { signal: controller.signal })
      return res.ok
    } catch {
      return false
    }
  },
}
