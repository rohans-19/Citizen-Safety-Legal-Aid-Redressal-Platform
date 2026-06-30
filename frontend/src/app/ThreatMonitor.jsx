import { useState, useEffect, useRef } from 'react'
import { api } from './api.js'

const POLL_INTERVAL_MS = 5000   // poll every 5 seconds
const BANNER_DURATION_MS = 8000 // auto-dismiss banner after 8s

/**
 * ThreatMonitor — invisible background component
 *
 * Polls /detect-threat every 5 seconds while in secure mode.
 * Renders a red alert banner at the top of the screen if a threat is detected.
 * Banner auto-dismisses after 8 seconds.
 */
export default function ThreatMonitor() {
  const [threatActive, setThreatActive] = useState(false)
  const [threatLabel,  setThreatLabel]  = useState('')
  const dismissTimerRef = useRef(null)

  useEffect(() => {
    let isMounted = true

    const poll = async () => {
      if (!isMounted) return
      try {
        const data = await api.detectThreat()
        if (!isMounted) return

        if (data.is_threat) {
          const label = data.labels?.[0] || 'Threat'
          setThreatLabel(label)
          setThreatActive(true)

          // Auto-dismiss after BANNER_DURATION_MS
          if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current)
          dismissTimerRef.current = setTimeout(() => {
            if (isMounted) setThreatActive(false)
          }, BANNER_DURATION_MS)
        }
      } catch {
        // Silent failure — don't alarm user if polling fails
      }
    }

    poll() // immediate first poll
    const intervalId = setInterval(poll, POLL_INTERVAL_MS)

    return () => {
      isMounted = false
      clearInterval(intervalId)
      if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current)
    }
  }, [])

  if (!threatActive) return null

  return (
    <div
      role="alert"
      className="fixed top-0 left-0 right-0 z-50 threat-banner"
    >
      <div className="bg-red-600 text-white px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-base">⚠️</span>
          <div>
            <p className="text-sm font-semibold">Threat Detected</p>
            {threatLabel && (
              <p className="text-xs text-red-200">{threatLabel} detected nearby</p>
            )}
          </div>
        </div>
        <button
          onClick={() => setThreatActive(false)}
          className="text-red-200 hover:text-white text-lg font-bold ml-4"
          aria-label="Dismiss threat alert"
        >
          ×
        </button>
      </div>
    </div>
  )
}
