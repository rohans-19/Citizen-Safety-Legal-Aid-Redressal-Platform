/**
 * ConfirmationScreen
 * Shown after VoiceRecorder submits and /process-voice responds.
 *
 * Props:
 *   data    — API response object from api.processVoice()
 *   onReset — callback to file another report
 */
export default function ConfirmationScreen({ data, onReset }) {
  if (!data) return null

  const {
    law_matched,
    incident_type,
    district,
    taluk,
    routed_to,
    authority,
    pdf_url,
    complaint_id,
    timestamp,
    evidence_list,
    next_action,
    empathy_message,
    severity,
    _mock,
  } = data

  const formattedDate = timestamp
    ? new Date(timestamp).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
    : null

  return (
    <div className="space-y-4 screen-fade">
      {/* Success header */}
      <div className="border border-green-300 bg-green-50 rounded px-4 py-3">
        <div className="flex items-start gap-3">
          <span className="text-2xl mt-0.5">✅</span>
          <div>
            <p className="font-semibold text-green-800 text-sm">Complaint Processed</p>
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

      {/* Complaint ID */}
      {complaint_id && (
        <div>
          <p className="text-xs text-gray-500 mb-0.5">Reference Number</p>
          <code className="text-sm font-mono text-gray-800 bg-gray-100 px-2 py-1 rounded border border-gray-200">
            {complaint_id}
          </code>
        </div>
      )}

      {/* Law matched */}
      {law_matched && (
        <div className="border border-gray-200 rounded divide-y divide-gray-100">
          <div className="px-3 py-2 bg-gray-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Law Identified</p>
          </div>
          <div className="px-3 py-2.5">
            <p className="text-sm font-medium text-gray-800">{law_matched}</p>
            {incident_type && (
              <p className="text-xs text-gray-500 mt-0.5 capitalize">
                Incident type: {incident_type.replace(/_/g, ' ')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Location & routing */}
      {(district || routed_to) && (
        <div className="border border-gray-200 rounded divide-y divide-gray-100">
          <div className="px-3 py-2 bg-gray-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Routing Information</p>
          </div>
          <div className="px-3 py-2.5 space-y-1.5">
            {district && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">District</span>
                <span className="text-gray-800 font-medium">{district}{taluk ? `, ${taluk}` : ''}</span>
              </div>
            )}
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
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Evidence to Collect</p>
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
        <div className="border border-blue-200 bg-blue-50 rounded px-4 py-3">
          <p className="text-xs font-semibold text-blue-800 uppercase tracking-wide mb-1">What To Do Next</p>
          <p className="text-sm text-blue-900">{next_action}</p>
        </div>
      )}

      {/* Empathy Message */}
      {empathy_message && (
        <div className="border border-green-200 bg-green-50 rounded px-4 py-3">
          <p className="text-sm text-green-800 italic">"{empathy_message}"</p>
        </div>
      )}

      {/* Timestamp */}
      {formattedDate && (
        <p className="text-xs text-gray-400">Filed at: {formattedDate}</p>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 pt-1">
        {pdf_url && pdf_url !== '#mock-pdf' ? (
          <a
            href={pdf_url}
            download={`complaint_${complaint_id || 'report'}.pdf`}
            className="flex items-center gap-1.5 border border-blue-600 text-blue-600 hover:bg-blue-50 text-sm font-medium px-4 py-2 rounded"
          >
            <span>📄</span> Download PDF
          </a>
        ) : (
          <button
            disabled
            className="flex items-center gap-1.5 border border-gray-200 text-gray-400 text-sm px-4 py-2 rounded cursor-not-allowed"
            title="PDF available after backend integration"
          >
            <span>📄</span> PDF (backend required)
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
