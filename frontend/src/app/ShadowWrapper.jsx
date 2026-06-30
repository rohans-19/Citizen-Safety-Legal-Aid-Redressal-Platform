import { useState, useEffect, useRef, useCallback } from 'react'
import DecoyApp from './DecoyApp.jsx'
import CivicShieldApp from './CivicShieldApp.jsx'

const HOLD_DURATION_MS = 2500  // 3-finger hold duration
const SHAKE_THRESHOLD  = 16.5  // m/s² magnitude to trigger wipe
const MIN_TOUCH_COUNT  = 3     // number of simultaneous fingers

export default function ShadowWrapper() {
  const [isSecureMode, setIsSecureMode]     = useState(false)
  const [gestureProgress, setGestureProgress] = useState(0) // 0–1

  const holdStartRef   = useRef(null)
  const animFrameRef   = useRef(null)
  const activeTouchRef = useRef(0)

  // ── Shake-to-wipe: subscribe to devicemotion ──────────────────────────────
  useEffect(() => {
    const handleMotion = (e) => {
      const accel = e.accelerationIncludingGravity
      if (!accel || !isSecureMode) return
      const { x = 0, y = 0, z = 0 } = accel
      const magnitude = Math.sqrt(x * x + y * y + z * z)
      if (magnitude > SHAKE_THRESHOLD) {
        // Wipe secure mode and clear any session data
        setIsSecureMode(false)
        setGestureProgress(0)
        sessionStorage.clear()
      }
    }

    window.addEventListener('devicemotion', handleMotion)
    return () => window.removeEventListener('devicemotion', handleMotion)
  }, [isSecureMode])

  // ── Desktop Keyboard Shortcut for Demo (Ctrl+Shift+S) ──────────────────
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 's') {
        e.preventDefault()
        setIsSecureMode(prev => !prev)
        if (isSecureMode) {
          sessionStorage.clear()
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isSecureMode])

  // ── Inactivity timeout to wipe session if left idle (3 minutes) ─────────────
  useEffect(() => {
    if (!isSecureMode) return

    let timer = null
    const timeoutVal = 180000 // 3 minutes

    const resetTimer = () => {
      if (timer) clearTimeout(timer)
      timer = setTimeout(() => {
        setIsSecureMode(false)
        setGestureProgress(0)
        sessionStorage.clear()
        console.log('[ShadowWrapper] Session auto-wiped due to inactivity')
      }, timeoutVal)
    }

    resetTimer()

    const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart']
    events.forEach(name => window.addEventListener(name, resetTimer))

    return () => {
      if (timer) clearTimeout(timer)
      events.forEach(name => window.removeEventListener(name, resetTimer))
    }
  }, [isSecureMode])

  // ── 3-finger hold animation loop ─────────────────────────────────────────
  const startHoldAnimation = useCallback(() => {
    holdStartRef.current = Date.now()

    const tick = () => {
      const elapsed  = Date.now() - holdStartRef.current
      const progress = Math.min(elapsed / HOLD_DURATION_MS, 1)
      setGestureProgress(progress)

      if (progress < 1 && activeTouchRef.current >= MIN_TOUCH_COUNT) {
        animFrameRef.current = requestAnimationFrame(tick)
      } else if (progress >= 1) {
        // Request DeviceMotion permission on iOS if needed
        if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
          DeviceMotionEvent.requestPermission()
            .then(state => {
              console.log('[ShadowWrapper] DeviceMotion permission:', state)
            })
            .catch(err => {
              console.warn('[ShadowWrapper] DeviceMotion permission failed:', err)
            })
        }
        // Unlock secure mode
        setIsSecureMode(true)
        setGestureProgress(0)
      }
    }

    animFrameRef.current = requestAnimationFrame(tick)
  }, [])

  const cancelHold = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current)
      animFrameRef.current = null
    }
    setGestureProgress(0)
    holdStartRef.current = null
  }, [])

  // ── Touch event handlers (on the decoy wrapper) ──────────────────────────
  const handleTouchStart = useCallback((e) => {
    if (isSecureMode) return
    activeTouchRef.current = e.touches.length

    if (e.touches.length >= MIN_TOUCH_COUNT && !holdStartRef.current) {
      startHoldAnimation()
    }
  }, [isSecureMode, startHoldAnimation])

  const handleTouchEnd = useCallback((e) => {
    activeTouchRef.current = e.touches.length

    if (e.touches.length < MIN_TOUCH_COUNT) {
      cancelHold()
    }
  }, [cancelHold])

  // Gesture progress indicator — a thin ring SVG overlay
  const ringCircumference = 2 * Math.PI * 22 // radius 22
  const strokeOffset = ringCircumference * (1 - gestureProgress)

  return (
    <div className="relative min-h-screen">

      {/* Secure mode: CivicShieldApp */}
      {isSecureMode && <CivicShieldApp onWipe={() => { setIsSecureMode(false); sessionStorage.clear() }} />}

      {/* Decoy: always mounted but hidden when secure mode is on */}
      <div
        className={isSecureMode ? 'hidden' : 'block'}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        onTouchCancel={handleTouchEnd}
      >
        <DecoyApp />
      </div>

      {/* 3-finger gesture progress ring — only shows during hold on decoy */}
      {!isSecureMode && gestureProgress > 0 && (
        <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
          <svg width="56" height="56" viewBox="0 0 56 56">
            <circle cx="28" cy="28" r="22" fill="rgba(0,0,0,0.45)" />
            <circle
              cx="28" cy="28" r="22"
              fill="none"
              stroke="#2563EB"
              strokeWidth="3"
              strokeDasharray={ringCircumference}
              strokeDashoffset={strokeOffset}
              strokeLinecap="round"
              transform="rotate(-90 28 28)"
              className="gesture-ring"
            />
            <text x="28" y="33" textAnchor="middle" fill="white" fontSize="14">🔒</text>
          </svg>
        </div>
      )}
    </div>
  )
}
