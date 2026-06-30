import { useState, useEffect } from 'react'
import VoiceRecorder from './VoiceRecorder.jsx'
import ConfirmationScreen from './ConfirmationScreen.jsx'

// 31 Karnataka districts
const KARNATAKA_DISTRICTS = [
  'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
  'Bidar', 'Chamarajanagara', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga',
  'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
  'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
  'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
  'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir', 'Vijayanagara',
]

const INCIDENT_TYPES = [
  { value: '',                      label: 'Select incident type…' },
  { value: 'caste_discrimination',  label: 'Caste Discrimination' },
  { value: 'domestic_violence',     label: 'Domestic Violence' },
  { value: 'workplace_harassment',  label: 'Workplace Harassment' },
  { value: 'disability_denial',     label: 'Disability Rights Denial' },
  { value: 'wage_theft',            label: 'Wage Theft / MNREGA Fraud' },
  { value: 'other',                 label: 'Other' },
]

/**
 * ReportScreen — main complaint filing screen
 * Contains VoiceRecorder + optional metadata form.
 * After submission, switches to ConfirmationScreen.
 */
export default function ReportScreen() {
  const [result,      setResult]      = useState(null)   // API response → show confirmation
  const [incidentType, setIncidentType] = useState('')
  const [district,    setDistrict]    = useState('')

  // Auto-detect district via geolocation
  useEffect(() => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=en`)
          const data = await res.json()
          const state_district = data.address?.state_district || data.address?.county || ''
          // Try to match against Karnataka districts
          const matched = KARNATAKA_DISTRICTS.find(d => 
            state_district.toLowerCase().includes(d.toLowerCase()) ||
            d.toLowerCase().includes(state_district.toLowerCase().replace(' district', ''))
          )
          if (matched) setDistrict(matched)
        } catch { /* silent */ }
      },
      () => { /* permission denied — silent */ },
      { timeout: 5000 }
    )
  }, [])

  const handleResult = (data) => {
    setResult(data)
  }

  const handleReset = () => {
    setResult(null)
    setIncidentType('')
    setDistrict('')
  }

  // Show confirmation if we have a result
  if (result) {
    return (
      <div className="p-4 screen-fade">
        <ConfirmationScreen data={result} onReset={handleReset} />
      </div>
    )
  }

  return (
    <div className="p-4 space-y-5 screen-fade">
      {/* Section header */}
      <div>
        <h2 className="text-base font-semibold text-gray-800">File a Complaint</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Record your statement in your preferred language. Your voice note will be
          processed by the legal AI system.
        </p>
      </div>

      {/* Step 1 — Select Details */}
      <div className="border border-gray-200 rounded">
        <div className="px-3 py-2.5 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-semibold">1</span>
          <span className="text-sm font-medium text-gray-700">Select Details</span>
        </div>
        <div className="p-4 grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Incident Type
            </label>
            <select
              id="incident-type-select"
              value={incidentType}
              onChange={e => setIncidentType(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm text-gray-700 focus:outline-none focus:border-blue-500"
            >
              {INCIDENT_TYPES.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              District
            </label>
            <select
              id="district-select"
              value={district}
              onChange={e => setDistrict(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm text-gray-700 focus:outline-none focus:border-blue-500"
            >
              <option value="">Select district…</option>
              {KARNATAKA_DISTRICTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Step 2 — Voice */}
      <div className="border border-gray-200 rounded">
        <div className="px-3 py-2.5 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-semibold">2</span>
          <span className="text-sm font-medium text-gray-700">Record Your Statement</span>
        </div>
        <div className="p-4">
          <VoiceRecorder onResult={handleResult} district={district} incidentType={incidentType} />
        </div>
      </div>

      {/* Info note */}
      <div className="border border-gray-200 rounded px-3 py-2.5 bg-gray-50">
        <p className="text-xs text-gray-500">
          <strong>Privacy note:</strong> Only anonymized metadata (district, incident type, timestamp)
          is stored. Your voice and identity are never persisted on the server.
        </p>
      </div>
    </div>
  )
}
