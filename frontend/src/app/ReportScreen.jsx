import { useCallback, useEffect, useState } from 'react'
import VoiceRecorder from './VoiceRecorder.jsx'
import ConfirmationScreen from './ConfirmationScreen.jsx'
import { api } from './api.js'

// 31 Karnataka districts
const KARNATAKA_DISTRICTS = [
  'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
  'Bidar', 'Chamarajanagara', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga',
  'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
  'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
  'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
  'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir', 'Vijayanagara',
]

const DISTRICT_CENTROIDS = {
  'Bagalkote': [16.18, 75.69],
  'Ballari': [15.14, 76.92],
  'Belagavi': [15.85, 74.50],
  'Bengaluru Rural': [13.22, 77.65],
  'Bengaluru Urban': [12.97, 77.59],
  'Bidar': [17.91, 77.52],
  'Chamarajanagara': [11.92, 76.95],
  'Chikkaballapur': [13.43, 77.72],
  'Chikkamagaluru': [13.32, 75.77],
  'Chitradurga': [14.23, 76.40],
  'Dakshina Kannada': [12.91, 74.86],
  'Davanagere': [14.46, 75.92],
  'Dharwad': [15.46, 75.01],
  'Gadag': [15.43, 75.63],
  'Hassan': [13.00, 76.10],
  'Haveri': [14.79, 75.40],
  'Kalaburagi': [17.33, 76.83],
  'Kodagu': [12.42, 75.74],
  'Kolar': [13.14, 78.13],
  'Koppal': [15.35, 76.15],
  'Mandya': [12.52, 76.90],
  'Mysuru': [12.30, 76.65],
  'Raichur': [16.21, 77.35],
  'Ramanagara': [12.72, 77.28],
  'Shivamogga': [13.93, 75.57],
  'Tumakuru': [13.34, 77.10],
  'Udupi': [13.34, 74.74],
  'Uttara Kannada': [14.80, 74.13],
  'Vijayapura': [16.83, 75.71],
  'Yadgir': [16.77, 77.14],
  'Vijayanagara': [15.27, 76.39],
}

const KARNATAKA_BOUNDS = { minLat: 11.4, maxLat: 18.6, minLon: 74.0, maxLon: 78.8 }

function distanceKm([lat1, lon1], [lat2, lon2]) {
  const toRad = (deg) => deg * Math.PI / 180
  const radius = 6371
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * radius * Math.asin(Math.sqrt(a))
}

function nearestDistrict(latitude, longitude) {
  if (
    latitude < KARNATAKA_BOUNDS.minLat || latitude > KARNATAKA_BOUNDS.maxLat ||
    longitude < KARNATAKA_BOUNDS.minLon || longitude > KARNATAKA_BOUNDS.maxLon
  ) {
    return null
  }

  return Object.entries(DISTRICT_CENTROIDS)
    .map(([name, coords]) => ({ name, distance: distanceKm([latitude, longitude], coords) }))
    .sort((a, b) => a.distance - b.distance)[0]?.name || null
}

/**
 * ReportScreen — main complaint filing screen
 * Contains VoiceRecorder + optional metadata form.
 * After submission, switches to ConfirmationScreen.
 */
export default function ReportScreen() {
  const [result,      setResult]      = useState(null)   // API response → show confirmation
  const [incidentType, setIncidentType] = useState('')
  const [district,    setDistrict]    = useState('')
  const [lastSubmission, setLastSubmission] = useState(null)
  const [locationStatus, setLocationStatus] = useState('Detecting district from mobile GPS…')
  const [geolocating, setGeolocating] = useState(false)

  const detectDistrictOnDevice = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationStatus('Location unavailable in this browser. Select district manually.')
      return
    }
    setGeolocating(true)
    setLocationStatus('Detecting district from mobile GPS…')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords
        const matched = nearestDistrict(latitude, longitude)
        if (matched) {
          setDistrict(matched)
          setLocationStatus(`Approximate district detected on-device: ${matched}`)
        } else {
          setLocationStatus('Could not match to Karnataka. Select district manually.')
        }
        setGeolocating(false)
      },
      () => {
        setLocationStatus('Location permission denied. Select district manually.')
        setGeolocating(false)
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 600000 }
    )
  }, [])

  useEffect(() => {
    detectDistrictOnDevice()
  }, [detectDistrictOnDevice])

  const handleResult = (data, info) => {
    setResult(data)
    if (info) setLastSubmission(info)
  }

  const handleUpdateDetails = async (newDistrict, newIncidentType) => {
    if (!lastSubmission) return
    const { audioBlob, transcript, language } = lastSubmission
    const updated = await api.processVoice(audioBlob, transcript, language, newDistrict, newIncidentType)
    setResult(updated)
    setDistrict(newDistrict)
    setIncidentType(newIncidentType)
  }

  const handleReset = () => {
    setResult(null)
    setIncidentType('')
    setDistrict('')
    setLastSubmission(null)
    setLocationStatus('Detecting district from mobile GPS…')
    detectDistrictOnDevice()
  }

  // Show confirmation if we have a result
  if (result) {
    return (
      <div className="p-4 screen-fade">
        <ConfirmationScreen 
          data={result} 
          onReset={handleReset} 
          onUpdateDetails={handleUpdateDetails}
        />
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4 screen-fade">
      {/* Section header */}
      <div>
        <h2 className="text-base font-semibold text-gray-800">File a Complaint</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Record or type your statement in your preferred language. CIVIC-SHIELD helps
          prepare a legal complaint; it is not a substitute for emergency help.
        </p>
      </div>

      <div className="border border-red-200 bg-red-50 rounded px-3 py-2.5">
        <div className="flex items-start gap-2">
          <span className="text-base mt-0.5">🚨</span>
          <div className="flex-1">
            <p className="text-sm font-semibold text-red-800">In immediate danger?</p>
            <p className="text-xs text-red-700 mt-0.5">
              Call emergency services now. Use this app after you are physically safe.
            </p>
          </div>
          <a
            href="tel:112"
            className="bg-red-600 hover:bg-red-700 text-white text-xs font-semibold px-3 py-1.5 rounded"
          >
            Call 112
          </a>
        </div>
      </div>

      <div className="border border-gray-200 rounded">
        <div className="px-3 py-2.5 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-semibold">1</span>
          <span className="text-sm font-medium text-gray-700">Auto Location</span>
        </div>
        <div className="p-4 space-y-3">
          <div className="border border-blue-100 bg-blue-50 rounded px-3 py-2 text-xs text-blue-800">
            District is detected from mobile GPS. Incident type is predicted from your statement after you submit.
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">District</label>
            <div className="flex gap-2">
              <select
                value={district}
                onChange={e => {
                  setDistrict(e.target.value)
                  setLocationStatus(e.target.value ? `Selected manually: ${e.target.value}` : 'Select manually, or retry GPS.')
                }}
                className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:border-blue-500"
              >
                <option value="">Unknown / not listed</option>
                {KARNATAKA_DISTRICTS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={detectDistrictOnDevice}
                disabled={geolocating}
                className="border border-blue-200 text-blue-700 hover:bg-blue-50 disabled:opacity-50 text-xs font-medium px-3 py-2 rounded whitespace-nowrap"
              >
                {geolocating ? 'Detecting…' : 'Retry GPS'}
              </button>
            </div>
            <p className={`text-xs mt-1 ${district ? 'text-green-700' : 'text-gray-500'}`}>
              {locationStatus}
            </p>
          </div>
        </div>
      </div>

      {/* Main Action — Voice Recorder */}
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
          <strong>Privacy note:</strong> Location detection runs locally and does not send coordinates
          to a map/IP service. The backend receives your transcript, selected district, and incident
          category predicted from your statement to generate the complaint PDF; analytics stores only anonymized metadata.
        </p>
      </div>
    </div>
  )
}
