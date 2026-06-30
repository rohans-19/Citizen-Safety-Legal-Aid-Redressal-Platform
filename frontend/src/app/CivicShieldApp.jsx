import { useState, useEffect } from 'react'
import ThreatMonitor from './ThreatMonitor.jsx'
import ReportScreen from './ReportScreen.jsx'
import ZKPWallet from './ZKPWallet.jsx'
import { api } from './api.js'

// Navigation tabs
const TABS = [
  { key: 'home',   label: 'Home',   icon: '🏠' },
  { key: 'report', label: 'Report', icon: '📋' },
  { key: 'wallet', label: 'Wallet', icon: '🔑' },
]

/**
 * CivicShieldApp — secure mode root
 * Rendered by ShadowWrapper after 3-finger unlock.
 *
 * Props:
 *   onWipe() — called to return to decoy mode (e.g. manual logout)
 */
export default function CivicShieldApp({ onWipe }) {
  const [activeTab, setActiveTab] = useState('home')
  const [backendOnline, setBackendOnline] = useState(null) // null=checking, true, false

  // Check backend connectivity once on mount
  useEffect(() => {
    api.healthCheck().then(setBackendOnline)
  }, [])

  return (
    <div className="min-h-screen bg-white flex flex-col max-w-md mx-auto">
      {/* ThreatMonitor — always active, renders its own banner if needed */}
      <ThreatMonitor />

      {/* Top navbar */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-blue-600 text-lg">🛡️</span>
            <span className="font-semibold text-gray-800 text-base">CIVIC-SHIELD</span>
          </div>
          <div className="flex items-center gap-2">
            {/* Backend connectivity indicator */}
            {backendOnline !== null && (
              <span className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded border ${
                backendOnline
                  ? 'text-green-600 border-green-200 bg-green-50'
                  : 'text-yellow-600 border-yellow-200 bg-yellow-50'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full inline-block ${
                  backendOnline ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                {backendOnline ? 'Connected' : 'Offline'}
              </span>
            )}
            {/* Manual wipe button */}
            <button
              id="btn-wipe-secure"
              onClick={onWipe}
              className="text-xs text-gray-400 hover:text-red-500 border border-gray-200 hover:border-red-300 rounded px-2 py-1"
              title="Exit secure mode"
            >
              ✕ Exit
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {activeTab === 'home'   && <HomeTab />}
        {activeTab === 'report' && <ReportScreen />}
        {activeTab === 'wallet' && <div className="p-4"><ZKPWallet /></div>}
      </main>

      {/* Bottom tab bar */}
      <nav className="border-t border-gray-200 bg-white sticky bottom-0 z-10">
        <div className="flex">
          {TABS.map(tab => (
            <button
              key={tab.key}
              id={`tab-${tab.key}`}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 flex flex-col items-center gap-0.5 py-2.5 text-xs font-medium transition-colors ${
                activeTab === tab.key
                  ? 'text-blue-600 border-t-2 border-blue-600'
                  : 'text-gray-400 border-t-2 border-transparent hover:text-gray-600'
              }`}
            >
              <span className="text-base">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}

// ── Home Tab ──────────────────────────────────────────────────────────────────
function HomeTab() {
  return (
    <div className="p-4 space-y-4 screen-fade">
      {/* Welcome banner */}
      <div className="border border-blue-200 bg-blue-50 rounded px-4 py-3">
        <p className="text-sm font-semibold text-blue-800">You are in Secure Mode</p>
        <p className="text-xs text-blue-600 mt-0.5">
          Shake the device at any time to immediately exit and wipe this session. If you are in immediate danger, call 112 first.
        </p>
      </div>

      {/* How to use — step-by-step */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">How to Use CIVIC-SHIELD</h2>
        <div className="space-y-2">
          {[
            { step: 1, icon: '🎙️', title: 'Record Your Statement', desc: 'Go to the Report tab. Record your voice note in Kannada, Hindi, or English.' },
            { step: 2, icon: '⚖️', title: 'AI Identifies the Law', desc: 'Our system matches your complaint to the correct legal provision (SC/ST Act, PWDV Act, etc.).' },
            { step: 3, icon: '📄', title: 'Download PDF Complaint', desc: 'A formatted legal complaint is generated and can be submitted to authorities.' },
            { step: 4, icon: '🔑', title: 'Prove Eligibility Offline', desc: 'Use the Wallet tab to generate a ZKP proof of income without sharing your Aadhaar.' },
          ].map(item => (
            <div key={item.step} className="flex gap-3 border border-gray-200 rounded px-3 py-2.5">
              <div className="flex flex-col items-center">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold flex-shrink-0">
                  {item.step}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800 flex items-center gap-1.5">
                  <span>{item.icon}</span>{item.title}
                </p>
                <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Supported laws */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-2">Supported Legal Provisions</h2>
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'SC/ST Act, 1989',    desc: 'Caste discrimination & atrocities' },
            { label: 'PWDV Act, 2005',     desc: 'Domestic violence & protection' },
            { label: 'POSH Act, 2013',     desc: 'Workplace sexual harassment' },
            { label: 'MNREGA',             desc: 'Wage rights & employment guarantee' },
            { label: 'RPwD Act, 2016',     desc: 'Disability rights & inclusion' },
            { label: 'IPC Sec. 498A',      desc: 'Cruelty by husband or relatives' },
          ].map(law => (
            <div key={law.label} className="border border-gray-200 rounded px-2.5 py-2">
              <p className="text-xs font-semibold text-gray-800">{law.label}</p>
              <p className="text-xs text-gray-500 mt-0.5">{law.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Emergency contacts */}
      <div className="border border-gray-200 rounded">
        <div className="px-3 py-2 bg-gray-50 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Emergency Contacts</p>
        </div>
        <div className="divide-y divide-gray-100">
          {[
            { name: 'Emergency Response', number: '112' },
            { name: 'Police',            number: '100' },
            { name: 'Women Helpline',    number: '1091' },
            { name: 'SC/ST Helpline',    number: '14566' },
            { name: 'Disability Helpline', number: '1800-111-009' },
          ].map(contact => (
            <div key={contact.name} className="flex justify-between items-center px-3 py-2">
              <span className="text-sm text-gray-700">{contact.name}</span>
              <a
                href={`tel:${contact.number}`}
                className="text-sm font-mono font-medium text-blue-600 hover:underline"
              >
                {contact.number}
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
