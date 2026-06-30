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

// Local state for threat detection status to bridge polling and upload
let localThreatStatus = {
  is_threat:  false,
  labels:     [],
  confidence: 0.0,
  _mock:      true,
}

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
   * Sends JSON payload with transcript to the backend agent swarm
   */
  async processVoice(audioBlob, transcript, language = 'kn', district = '') {
    const data = await callApi(
      `${BACKEND_URL}/process-voice`,
      {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          transcript: transcript,
          district:   district || 'Unknown',
          language:   language,
        })
      },
      MOCK.processVoice
    )

    if (data && !data._mock) {
      let formattedLaw = ''
      if (data.law_matched) {
        if (typeof data.law_matched === 'object') {
          const act = data.law_matched.act || ''
          const sections = (data.law_matched.sections || []).join(', ')
          formattedLaw = sections ? `${act} — ${sections}` : act
        } else {
          formattedLaw = String(data.law_matched)
        }
      }

      // Map backend response keys to frontend keys expected by ConfirmationScreen.jsx
      return {
        incident_type: data.incident_type || '',
        law_matched:   formattedLaw,
        district:      district || 'Unknown',
        taluk:         '',
        routed_to:     data.routing || '',
        authority:     data.authority || '',
        pdf_url:       data.pdf_path ? `${BACKEND_URL}/generated_pdfs/${data.pdf_path.split(/[\\/]/).pop()}` : null,
        complaint_id:  data.pseudonym || 'CS-' + Math.floor(Math.random() * 90000 + 10000),
        timestamp:     new Date().toISOString(),
        _mock:         false
      }
    }

    return data
  },

  /**
   * GET/POST /detect-threat
   * If audioBlob is provided, runs POST to detect threat.
   * If not, returns the current threat status.
   */
  async detectThreat(audioBlob) {
    if (!audioBlob) {
      return localThreatStatus
    }

    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')

    const result = await callApi(
      `${BACKEND_URL}/detect-threat`,
      {
        method: 'POST',
        body:   formData
      },
      MOCK.detectThreat
    )

    if (result && !result._mock) {
      localThreatStatus = {
        is_threat:  result.is_threat || false,
        labels:     result.label ? [result.label] : [],
        confidence: result.probability || 0.0,
        _mock:      false
      }
    } else if (result && result._mock) {
      localThreatStatus = {
        is_threat:  result.is_threat || false,
        labels:     result.labels || [],
        confidence: result.confidence || 0.0,
        _mock:      true
      }
    }

    return localThreatStatus
  },

  /**
   * POST /verify-zkp
   * Verifies a Pedersen commitment from the ZKP wallet
   */
  async verifyZkp(commitment, blindingFactor) {
    const data = await callApi(
      `${BACKEND_URL}/verify-zkp`,
      {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          commitment,
          proof: {
            value_hash: blindingFactor, // Mock 64-char hex string
            blinding_hash: blindingFactor, // Mock 64-char hex string
          }
        }),
      },
      MOCK.verifyZkp
    )

    if (data && typeof data.verified !== 'undefined') {
      return {
        valid:   data.verified,
        message: data.verified ? 'Commitment verified successfully' : 'Verification failed'
      }
    }
    return data
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
