import { useState, useRef, useEffect, useCallback } from 'react'
import { checkCodeWords } from './CodeWordEngine.js'
import { api } from './api.js'

// Language options matching backend expectations
const LANGUAGES = [
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { code: 'hi', label: 'हिंदी (Hindi)'   },
  { code: 'en', label: 'English'          },
]

/**
 * VoiceRecorder
 * Props:
 *   onResult(data) — called with API response after processing
 */
export default function VoiceRecorder({ onResult, district, incidentType }) {
  const [status, setStatus]             = useState('idle')     // idle | recording | processing | error
  const [transcript, setTranscript]     = useState('')
  const [language, setLanguage]         = useState('kn')
  const [codeWordAlert, setCodeWordAlert] = useState(null)     // matched code word string
  const [errorMsg, setErrorMsg]         = useState('')

  const mediaRecorderRef = useRef(null)
  const audioChunksRef   = useRef([])
  const streamRef        = useRef(null)
  const recognitionRef   = useRef(null)
  const canvasRef        = useRef(null)
  const animFrameRef     = useRef(null)
  const analyserRef      = useRef(null)
  const audioContextRef  = useRef(null)
  const transcriptRef    = useRef('')

  const setTranscriptValue = useCallback((value) => {
    transcriptRef.current = value
    setTranscript(value)
  }, [])

  // ── Waveform canvas drawing ───────────────────────────────────────────────
  const drawWaveform = useCallback(() => {
    const canvas  = canvasRef.current
    const analyser = analyserRef.current
    if (!canvas || !analyser) return

    const ctx    = canvas.getContext('2d')
    const W      = canvas.width
    const H      = canvas.height
    const bufLen = analyser.frequencyBinCount
    const dataArr = new Uint8Array(bufLen)

    const draw = () => {
      animFrameRef.current = requestAnimationFrame(draw)
      analyser.getByteFrequencyData(dataArr)

      ctx.clearRect(0, 0, W, H)
      ctx.fillStyle = '#f8fafc'
      ctx.fillRect(0, 0, W, H)

      const barW   = (W / bufLen) * 2.5
      let   x      = 0

      for (let i = 0; i < bufLen; i++) {
        const barH = (dataArr[i] / 255) * H * 0.85
        ctx.fillStyle = '#2563EB'
        ctx.fillRect(x, H - barH, barW - 1, barH)
        x += barW
      }
    }
    draw()
  }, [])

  const stopWaveform = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current)
      animFrameRef.current = null
    }
    // Clear canvas to flat line
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = '#f8fafc'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      // Draw flat baseline
      ctx.strokeStyle = '#e2e8f0'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(0, canvas.height / 2)
      ctx.lineTo(canvas.width, canvas.height / 2)
      ctx.stroke()
    }
  }, [])

  // Draw flat line on mount
  useEffect(() => {
    stopWaveform()
  }, [stopWaveform])

  // ── Web Speech API transcription ─────────────────────────────────────────
  const startTranscription = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return null

    const recognition = new SpeechRecognition()
    recognition.continuous     = true
    recognition.interimResults = true
    recognition.lang           = language === 'kn' ? 'kn-IN'
                                : language === 'hi' ? 'hi-IN'
                                : 'en-IN'

    recognition.onresult = (e) => {
      let fullText = ''
      for (let i = 0; i < e.results.length; i++) {
        fullText += `${e.results[i][0].transcript} `
      }
      const full = fullText.trim()
      if (full) {
        setTranscriptValue(full)
        // Check code words on every update
        const match = checkCodeWords(full)
        if (match.triggered) {
          setCodeWordAlert(match.matchedWord)
          // Vibrate if supported
          if (navigator.vibrate) navigator.vibrate([200, 100, 200])
        }
      }
    }

    recognition.onerror = () => { /* silent */ }
    recognition.start()
    return recognition
  }, [language, setTranscriptValue])

  // ── Start recording ───────────────────────────────────────────────────────
  const startRecording = useCallback(async () => {
    setErrorMsg('')
    setCodeWordAlert(null)
    setTranscriptValue('')
    audioChunksRef.current = []

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setErrorMsg('Audio recording is not supported in this browser. Please type your statement below.')
        setStatus('error')
        return
      }
      if (!window.MediaRecorder) {
        setErrorMsg('MediaRecorder is not supported in this browser. Please type your statement below.')
        setStatus('error')
        return
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      // Set up Web Audio for waveform
      const AudioContextCtor = window.AudioContext || window.webkitAudioContext
      if (AudioContextCtor) {
        const audioCtx = new AudioContextCtor()
        audioContextRef.current = audioCtx
        const source   = audioCtx.createMediaStreamSource(stream)
        const analyser = audioCtx.createAnalyser()
        analyser.fftSize = 64
        source.connect(analyser)
        analyserRef.current = analyser
        drawWaveform()
      }

      // MediaRecorder for capturing audio blob
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'

      const recorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      recorder.start(200)  // collect in 200ms chunks

      // Start speech transcription
      recognitionRef.current = startTranscription()

      setStatus('recording')
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setErrorMsg('Microphone access denied. Please allow microphone and retry.')
      } else {
        setErrorMsg('Could not start recording. Please check your microphone.')
      }
    }
  }, [drawWaveform, startTranscription, setTranscriptValue])

  // ── Stop recording and submit ─────────────────────────────────────────────
  const stopRecording = useCallback(async () => {
    setStatus('processing')
    stopWaveform()

    // Stop speech recognition
    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch { /* ignore */ }
    }

    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      const stopped = new Promise(resolve => {
        mediaRecorderRef.current.onstop = resolve
      })
      mediaRecorderRef.current.stop()
      await stopped
    }

    // Stop mic stream
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null

    if (audioContextRef.current) {
      try { await audioContextRef.current.close() } catch { /* ignore */ }
      audioContextRef.current = null
      analyserRef.current = null
    }

    const finalTranscript = transcriptRef.current.trim()

    // Validate non-empty transcript
    if (!finalTranscript || finalTranscript.length < 3) {
      setErrorMsg('No speech detected. Please speak clearly and try again.')
      setStatus('error')
      return
    }

    // Submit to backend
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
      
      // Run language-agnostic threat detector in the background
      api.detectThreat(audioBlob).catch(err => {
        console.warn('Acoustic threat detection background error:', err)
      })

      const result    = await api.processVoice(audioBlob, finalTranscript, language, district, incidentType)
      setStatus('idle')
      if (onResult) onResult(result, { audioBlob, transcript: finalTranscript, language })
    } catch {
      setErrorMsg('Failed to process recording. Please try again.')
      setStatus('error')
    }
  }, [stopWaveform, language, district, incidentType, onResult])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopWaveform()
      if (recognitionRef.current) {
        try { recognitionRef.current.stop() } catch { /* ignore */ }
      }
      streamRef.current?.getTracks().forEach(t => t.stop())
      if (audioContextRef.current) {
        try { audioContextRef.current.close() } catch { /* ignore */ }
      }
    }
  }, [stopWaveform])

  const isRecording  = status === 'recording'
  const isProcessing = status === 'processing'

  return (
    <div className="space-y-4">
      {/* Language selector */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Language</label>
        <select
          value={language}
          onChange={e => setLanguage(e.target.value)}
          disabled={isRecording || isProcessing}
          className="border border-gray-300 rounded px-2 py-1.5 text-sm text-gray-700 focus:outline-none focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
        >
          {LANGUAGES.map(l => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      </div>

      {/* Waveform canvas */}
      <div className="border border-gray-200 rounded bg-gray-50 overflow-hidden">
        <canvas
          ref={canvasRef}
          width={480}
          height={80}
          className="w-full h-20"
          aria-label="Audio waveform"
        />
      </div>

      {/* Code word silent alert */}
      {codeWordAlert && (
        <div className="border border-orange-300 bg-orange-50 rounded px-3 py-2 flex items-center gap-2">
          <span className="text-orange-500 text-sm">🔔</span>
          <span className="text-xs text-orange-700">
            Code word detected: <strong>"{codeWordAlert}"</strong> — safety mode activated on this device.
          </span>
        </div>
      )}

      {/* Record / Stop button */}
      <div className="flex items-center gap-4">
        {!isRecording && !isProcessing && (
          <button
            id="btn-start-recording"
            onClick={startRecording}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded border border-blue-700 shadow-sm transition-colors duration-150"
          >
            <span className="w-2 h-2 rounded-full bg-white inline-block" />
            Start Recording
          </button>
        )}

        {!isRecording && !isProcessing && transcript.trim() && (
          <button
            id="btn-submit-text"
            onClick={async () => {
              setStatus('processing')
              try {
                const finalTranscript = transcriptRef.current.trim()
                const result = await api.processVoice(null, finalTranscript, language, district, incidentType)
                setStatus('idle')
                if (onResult) onResult(result, { audioBlob: null, transcript: finalTranscript, language })
              } catch {
                setErrorMsg('Failed to process statement. Please try again.')
                setStatus('error')
              }
            }}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded border border-green-700 shadow-sm transition-colors duration-150"
          >
            <span>📤</span> Submit Statement
          </button>
        )}

        {isRecording && (
          <button
            id="btn-stop-recording"
            onClick={stopRecording}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-4 py-2 rounded border border-red-700 shadow-sm transition-colors duration-150"
          >
            <span className="w-2 h-2 rounded bg-white inline-block animate-pulse" />
            Stop & Submit
          </button>
        )}

        {isProcessing && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <svg className="animate-spin h-4 w-4 text-blue-600" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            Processing...
          </div>
        )}

        {isRecording && (
          <span className="text-xs text-red-500 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse inline-block" />
            Recording
          </span>
        )}
      </div>

      {/* Statement text area */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Statement / Complaint
        </label>
        <textarea
          value={transcript}
          onChange={e => {
            setTranscriptValue(e.target.value)
            const match = checkCodeWords(e.target.value)
            if (match && match.triggered) {
              setCodeWordAlert(match.matchedWord)
              if (navigator.vibrate) navigator.vibrate([200, 100, 200])
            } else {
              setCodeWordAlert(null)
            }
          }}
          disabled={isRecording || isProcessing}
          placeholder="Type your complaint here, or click 'Start Recording' to speak..."
          className="w-full border border-gray-300 rounded px-3 py-2 min-h-[100px] text-sm text-gray-700 focus:outline-none focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
        />
        {isRecording && !transcript && (
          <p className="text-xs text-gray-400 italic mt-1 animate-pulse">Listening...</p>
        )}
      </div>

      {/* Error message */}
      {errorMsg && (
        <div className="border border-red-200 bg-red-50 rounded px-3 py-2 text-sm text-red-600">
          {errorMsg}
          <button
            onClick={() => { setErrorMsg(''); setStatus('idle') }}
            className="ml-2 text-red-400 hover:text-red-600 underline text-xs"
          >
            Retry
          </button>
        </div>
      )}
    </div>
  )
}
