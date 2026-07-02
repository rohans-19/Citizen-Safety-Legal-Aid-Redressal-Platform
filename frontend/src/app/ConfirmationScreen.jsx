import { useState, useEffect } from 'react'

const KARNATAKA_DISTRICTS = [
  'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
  'Bidar', 'Chamarajanagara', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga',
  'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
  'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
  'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
  'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir', 'Vijayanagara',
]

const INCIDENT_TYPES = [
  { value: 'caste_discrimination',          label: 'Caste Discrimination / Atrocity' },
  { value: 'domestic_violence',             label: 'Domestic Violence' },
  { value: 'sexual_harassment_workplace',   label: 'Workplace Sexual Harassment (POSH)' },
  { value: 'wage_theft',                    label: 'Wage Theft / Non-Payment of Wages' },
  { value: 'mnrega_denial',                 label: 'MGNREGA Work / Wage Denial' },
  { value: 'disability_discrimination',     label: 'Disability Rights & Discrimination' },
  { value: 'pension_denial',                label: 'Pension / Social Security Denial' },
  { value: 'ration_denial',                 label: 'Ration / PDS Entitlement Denial' },
  { value: 'healthcare_denial',             label: 'Healthcare Denial / Ayushman Bharat' },
  { value: 'child_labour',                  label: 'Child Labour' },
  { value: 'bonded_labour',                 label: 'Bonded Labour' },
  { value: 'land_encroachment',             label: 'Land Encroachment / Eviction' },
  { value: 'other',                         label: 'Other General Grievance' },
]

const DISTRICT_HELPLINES = {
  'Bagalkote': '08354-235122', 'Ballari': '08392-278077', 'Belagavi': '0831-2405022',
  'Bengaluru Rural': '080-22262272', 'Bengaluru Urban': '080-22262272', 'Bidar': '08482-225302',
  'Chamarajanagara': '08226-224402', 'Chikkaballapur': '08156-277022', 'Chikkamagaluru': '08262-238022',
  'Chitradurga': '08194-222633', 'Dakshina Kannada': '0824-2440022', 'Davanagere': '08192-233633',
  'Dharwad': '0836-2448222', 'Gadag': '08372-238822', 'Hassan': '08172-265622',
  'Haveri': '08375-249022', 'Kalaburagi': '08472-263322', 'Kodagu': '08272-220022',
  'Kolar': '08152-222233', 'Koppal': '08539-220022', 'Mandya': '08232-229233',
  'Mysuru': '0821-2418022', 'Raichur': '08532-228722', 'Ramanagara': '080-27273322',
  'Shivamogga': '08182-222033', 'Tumakuru': '0816-2255022', 'Udupi': '0820-2520022',
  'Uttara Kannada': '08382-226622', 'Vijayapura': '08352-250022', 'Yadgir': '08473-250022',
  'Vijayanagara': '08394-223322',
}

/**
 * ConfirmationScreen
 * Shown after VoiceRecorder submits and /process-voice responds.
 * Incident type and district are AUTO-PREDICTED — correction is hidden by default.
 */
export default function ConfirmationScreen({ data, onReset, onUpdateDetails }) {
  if (!data) return null

  const {
    law_matched, incident_type, district, taluk, routed_to, authority,
    pdf_url, complaint_id, timestamp, evidence_list, next_action,
    empathy_message, severity, db_logged, _mock,
  } = data

  const [showEdit, setShowEdit] = useState(false)
  const [selectedDistrict, setSelectedDistrict] = useState(district || '')
  const [selectedType, setSelectedType] = useState(incident_type || '')
  const [updating, setUpdating] = useState(false)
  const [updateError, setUpdateError] = useState('')

  useEffect(() => {
    setSelectedDistrict(district || '')
    setSelectedType(incident_type || '')
    setUpdateError('')
    setShowEdit(false)
  }, [data, district, incident_type])

  const handleUpdate = async () => {
    if (!onUpdateDetails) return
    setUpdating(true)
    setUpdateError('')
    try {
      await onUpdateDetails(selectedDistrict, selectedType)
    } catch (err) {
      setUpdateError('Update failed. Check connection.')
    } finally {
      setUpdating(false)
    }
  }

  // PDF download handler — works with blob URLs from base64
  const handleDownloadPdf = () => {
    if (!pdf_url || pdf_url === '#mock-pdf') return
    const link = document.createElement('a')
    link.href = pdf_url
    link.download = `complaint_${complaint_id || 'report'}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const formattedDate = timestamp
    ? new Date(timestamp).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
    : null

  const incidentLabel = INCIDENT_TYPES.find(t => t.value === incident_type)?.label
    || (incident_type ? incident_type.replace(/_/g, ' ') : 'Under Review')

  return (
    <div className="space-y-4 screen-fade">
      {/* Success header */}
      <div className="border border-green-300 bg-green-50 rounded px-4 py-3">
        <div className="flex items-start gap-3">
          <span className="text-2xl mt-0.5">✅</span>
          <div>
            <p className="font-semibold text-green-800 text-sm">Complaint Processed Successfully</p>
            <p className="text-xs text-green-700 mt-0.5">
              Your report has been documented and routed to the appropriate authority.
            </p>
            {_mock && (
              <span className="inline-block mt-1 text-xs bg-yellow-100 text-yellow-700 border border-yellow-200 rounded px-1.5 py-0.5">
                Demo mode — mock response
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Auto-detected summary — read-only, with tiny edit link */}
      <div className="border border-gray-200 rounded divide-y divide-gray-100">
        <div className="px-3 py-2 bg-gray-50 flex items-center justify-between">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">AI-Detected Details</p>
          <button
            onClick={() => setShowEdit(!showEdit)}
            className="text-xs text-blue-600 hover:underline focus:outline-none"
          >
            {showEdit ? 'Close' : 'Wrong? Edit'}
          </button>
        </div>
        <div className="px-3 py-2.5 space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Incident Type</span>
            <span className="text-gray-800 font-medium capitalize">{incidentLabel}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">District</span>
            <span className="text-gray-800 font-medium">{district || 'Unknown'}{taluk ? `, ${taluk}` : ''}</span>
          </div>
          {severity > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Severity</span>
              <span className={`font-medium ${severity >= 0.8 ? 'text-red-600' : severity >= 0.5 ? 'text-yellow-600' : 'text-green-600'}`}>
                {severity >= 0.8 ? '🔴 High' : severity >= 0.5 ? '🟡 Medium' : '🟢 Low'} ({(severity * 100).toFixed(0)}%)
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Collapsed correction panel — only shown when user clicks "Wrong? Edit" */}
      {showEdit && (
        <div className="border border-blue-200 bg-blue-50/50 rounded p-3 space-y-3 screen-fade">
          <p className="text-xs text-gray-600">
            Correct the category or location below to re-generate your legal PDF.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Incident Type</label>
              <select
                value={selectedType}
                onChange={e => setSelectedType(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-xs text-gray-700 bg-white"
              >
                <option value="unknown">Under Review / Unknown</option>
                {INCIDENT_TYPES.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">District</label>
              <select
                value={selectedDistrict}
                onChange={e => setSelectedDistrict(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-xs text-gray-700 bg-white"
              >
                <option value="Unknown">Unknown District</option>
                {KARNATAKA_DISTRICTS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          </div>
          {updateError && <p className="text-xs text-red-600">{updateError}</p>}
          <div className="flex justify-end">
            <button
              onClick={handleUpdate}
              disabled={updating || (selectedDistrict === district && selectedType === incident_type)}
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updating ? 'Updating...' : 'Update & Re-generate'}
            </button>
          </div>
        </div>
      )}

      {/* Complaint Reference & ZKP Status Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 border border-gray-100 rounded">
        {complaint_id && (
          <div>
            <p className="text-xs text-gray-500 mb-0.5 font-medium">Reference Number</p>
            <code className="text-sm font-mono text-gray-800 bg-gray-100 px-2 py-1 rounded border border-gray-200">
              {complaint_id}
            </code>
          </div>
        )}

        <div className="flex gap-2">
          {data.zkp_verified && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold px-2.5 py-1.5 rounded flex items-center gap-1 shadow-sm">
              <span>🛡️</span>
              <span>ZKP Verified</span>
            </div>
          )}

          {data.email_sent && (
            <div className="bg-blue-50 border border-blue-200 text-blue-800 text-xs font-bold px-2.5 py-1.5 rounded flex items-center gap-1 shadow-sm" title={data.officer_email}>
              <span>✉️</span>
              <span>Escalated</span>
            </div>
          )}
        </div>
      </div>

      {/* Law matched */}
      {law_matched && (
        <div className="border border-gray-200 rounded divide-y divide-gray-100">
          <div className="px-3 py-2 bg-gray-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Applicable Law</p>
          </div>
          <div className="px-3 py-2.5">
            <p className="text-sm font-medium text-gray-800">{law_matched}</p>
          </div>
        </div>
      )}

      {/* Routing info */}
      {(routed_to || authority) && (
        <div className="border border-gray-200 rounded divide-y divide-gray-100">
          <div className="px-3 py-2 bg-gray-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Routing</p>
          </div>
          <div className="px-3 py-2.5 space-y-1.5">
            {routed_to && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Routed to</span>
                <span className="text-gray-800 font-medium text-right">{routed_to}</span>
              </div>
            )}
            {authority && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Authority</span>
                <span className="text-gray-800 font-medium text-right">{authority}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Evidence Checklist */}
      {evidence_list && evidence_list.length > 0 && (
        <div className="border border-gray-200 rounded divide-y divide-gray-100">
          <div className="px-3 py-2 bg-gray-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">📋 Evidence to Collect</p>
          </div>
          <div className="px-3 py-2.5 space-y-2">
            {evidence_list.map((item, i) => (
              <label key={i} className="flex items-start gap-2 text-sm text-gray-700 cursor-pointer">
                <input type="checkbox" className="mt-0.5 accent-blue-600" />
                <span>{item}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Next Action */}
      {next_action && (
        <div className="border border-blue-200 bg-blue-50 rounded px-4 py-3 space-y-2">
          <p className="text-xs font-semibold text-blue-800 uppercase tracking-wide mb-1">🚶 What To Do Next</p>
          <p className="text-sm text-blue-900">{next_action}</p>
          {district && DISTRICT_HELPLINES[district] && (
            <div className="border-t border-blue-200 pt-2 flex items-center justify-between text-xs text-blue-800 font-medium">
              <span>📞 DLSA Helpline ({district}):</span>
              <a href={`tel:${DISTRICT_HELPLINES[district]}`} className="font-mono font-bold hover:underline">
                {DISTRICT_HELPLINES[district]}
              </a>
            </div>
          )}
        </div>
      )}

      {/* Email Escalation Notification */}
      {data.email_sent && (
        <div className="border border-blue-200 bg-blue-50/50 rounded px-4 py-3 text-xs text-blue-900 flex items-start gap-2 shadow-xs">
          <span className="text-base">✉️</span>
          <div>
            <p className="font-semibold text-blue-950">Departmental Escalation Complete</p>
            <p className="mt-0.5 text-blue-800 leading-relaxed">
              A comprehensive legal complaint report and signed PDF have been officially escalated to the designated authority: <span className="font-bold text-blue-950">{authority || routed_to || 'Concerned Welfare Officer'}</span>.
            </p>
          </div>
        </div>
      )}

      {/* DB status warning */}
      {db_logged === false && (
        <div className="border border-yellow-200 bg-yellow-50 rounded px-4 py-2.5 text-xs text-yellow-800 flex items-start gap-2">
          <span className="text-base mt-0.5">⚠️</span>
          <div>
            <p className="font-semibold">Analytics Sync Offline</p>
            <p className="mt-0.5 text-gray-600">Your complaint PDF is ready. Database sync will retry automatically.</p>
          </div>
        </div>
      )}

      {/* Empathy Message */}
      {empathy_message && (
        <div className="border border-green-200 bg-green-50 rounded px-4 py-3">
          <p className="text-sm text-green-800 italic">"{empathy_message}"</p>
        </div>
      )}

      {formattedDate && <p className="text-xs text-gray-400">Filed at: {formattedDate}</p>}

      {/* Action buttons — PDF download + File Another */}
      <div className="flex gap-3 pt-1">
        {pdf_url && pdf_url !== '#mock-pdf' ? (
          <button
            onClick={handleDownloadPdf}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded focus:outline-none"
          >
            <span>📄</span> Download Complaint PDF
          </button>
        ) : (
          <button
            disabled
            className="flex items-center gap-1.5 border border-gray-200 text-gray-400 text-sm px-4 py-2 rounded cursor-not-allowed"
            title="PDF available after backend processes your complaint"
          >
            <span>📄</span> PDF (processing…)
          </button>
        )}

        <button
          id="btn-file-another"
          onClick={onReset}
          className="border border-gray-300 hover:border-gray-400 text-gray-700 text-sm px-4 py-2 rounded"
        >
          File Another Report
        </button>
      </div>
    </div>
  )
}
