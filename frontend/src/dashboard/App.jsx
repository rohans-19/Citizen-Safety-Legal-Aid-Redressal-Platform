/**
 * App.jsx — Member C
 * NGO Command Center Dashboard root component.
 * Mounts LiveUpdater, renders HeatmapLayer + AnomalyAlert sidebar + stat header.
 */
import React, { useState } from "react";
import LiveUpdater     from "./LiveUpdater.js";
import HeatmapLayer    from "./HeatmapLayer.jsx";
import AnomalyAlert    from "./AnomalyAlert.jsx";
import DistrictTooltip from "./DistrictTooltip.jsx";

// ── Derived stats helpers ──────────────────────────────────────────────────────
function computeStats(scoreData) {
  if (!scoreData) return { total: 0, high: 0, medium: 0, low: 0 };
  const vals = Object.values(scoreData);
  return {
    total:  vals.reduce((s, v) => s + (v.count || 0), 0).toFixed(0),
    high:   vals.filter((v) => v.tier === "HIGH").length,
    medium: vals.filter((v) => v.tier === "MEDIUM").length,
    low:    vals.filter((v) => v.tier === "LOW").length,
  };
}

// ── StatCard ───────────────────────────────────────────────────────────────────
function StatCard({ label, value, color }) {
  return (
    <div
      style={{
        background:   "rgba(15, 23, 42, 0.8)",
        border:       `1px solid ${color}40`,
        borderRadius: "12px",
        padding:      "14px 20px",
        minWidth:     "130px",
        backdropFilter: "blur(6px)",
      }}
    >
      <div style={{ fontSize: "11px", color: "#64748b", fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: "28px", fontWeight: 800, color, marginTop: "2px" }}>{value}</div>
    </div>
  );
}

// ── Root App ───────────────────────────────────────────────────────────────────
export default function App() {
  const [scoreData,        setScoreData]        = useState(null);
  const [error,            setError]            = useState(null);
  const [lastUpdated,      setLastUpdated]      = useState(null);
  const [tooltip,          setTooltip]          = useState({ visible: false, district: null, x: 0, y: 0 });

  const handleUpdate = (data) => {
    setScoreData(data);
    setError(null);
    setLastUpdated(new Date().toLocaleTimeString());
  };

  const stats = computeStats(scoreData);

  return (
    <div
      style={{
        minHeight:   "100vh",
        background:  "linear-gradient(135deg, #020617 0%, #0f172a 50%, #0c1a2e 100%)",
        fontFamily:  "'Inter', sans-serif",
        display:     "flex",
        flexDirection: "column",
        padding:     "24px 28px",
        gap:         "20px",
      }}
    >
      {/* Google Font */}
      <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap"
        rel="stylesheet"
      />

      {/* ── Header ── */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1
            style={{
              margin:      0,
              fontSize:    "22px",
              fontWeight:  800,
              color:       "#f1f5f9",
              letterSpacing: "-0.3px",
            }}
          >
            🛡️ CIVIC-SHIELD
            <span
              style={{
                marginLeft:  "10px",
                fontSize:    "12px",
                fontWeight:  500,
                color:       "#22c55e",
                background:  "rgba(34,197,94,0.1)",
                border:      "1px solid rgba(34,197,94,0.3)",
                borderRadius:"6px",
                padding:     "2px 8px",
                verticalAlign:"middle",
              }}
            >
              NGO Command Center
            </span>
          </h1>
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#475569" }}>
            Spatiotemporal Anomaly Detection · Karnataka · T-GAT + Differential Privacy
          </p>
        </div>
        <div style={{ textAlign: "right", fontSize: "11px", color: "#475569" }}>
          {lastUpdated
            ? <>Last updated: <strong style={{ color: "#94a3b8" }}>{lastUpdated}</strong></>
            : <span style={{ color: "#ef4444" }}>Connecting to analytics server…</span>}
          {error && (
            <div style={{ color: "#ef4444", marginTop: "4px" }}>⚠️ {error}</div>
          )}
        </div>
      </header>

      {/* ── Stats Bar ── */}
      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
        <StatCard label="Total Incidents (DP)"  value={stats.total}  color="#60a5fa" />
        <StatCard label="HIGH Risk Districts"    value={stats.high}   color="#ef4444" />
        <StatCard label="MEDIUM Risk Districts"  value={stats.medium} color="#f59e0b" />
        <StatCard label="LOW Risk Districts"     value={stats.low}    color="#22c55e" />
      </div>

      {/* ── Map + Sidebar ── */}
      <div style={{ display: "flex", gap: "20px", flex: 1, minHeight: "520px" }}>
        {/* D3.js Map */}
        <div
          style={{
            flex:         1,
            background:   "rgba(15, 23, 42, 0.7)",
            borderRadius: "16px",
            border:       "1px solid #1e293b",
            overflow:     "hidden",
            backdropFilter: "blur(6px)",
            position:     "relative",
          }}
        >
          {!scoreData && (
            <div
              style={{
                position:   "absolute",
                inset:      0,
                display:    "flex",
                alignItems: "center",
                justifyContent: "center",
                color:      "#475569",
                fontSize:   "13px",
                zIndex:     5,
              }}
            >
              Loading district data…
            </div>
          )}
          <HeatmapLayer
            scoreData={scoreData}
            onDistrictHover={(name, x, y) => setTooltip({ visible: true, district: name, x, y })}
            onDistrictLeave={() => setTooltip((t) => ({ ...t, visible: false }))}
          />
        </div>

        {/* Alert Sidebar */}
        <AnomalyAlert scoreData={scoreData} />
      </div>

      {/* ── Legend ── */}
      <div style={{ display: "flex", gap: "20px", alignItems: "center", flexWrap: "wrap" }}>
        {[
          { color: "#22c55e", label: "LOW (score < 0.45)" },
          { color: "#f59e0b", label: "MEDIUM (0.45 – 0.75)" },
          { color: "#ef4444", label: "HIGH (score > 0.75)" },
        ].map(({ color, label }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <div
              style={{
                width: "12px", height: "12px",
                borderRadius: "3px",
                background: color,
              }}
            />
            <span style={{ fontSize: "11px", color: "#64748b" }}>{label}</span>
          </div>
        ))}
        <span style={{ fontSize: "10px", color: "#334155", marginLeft: "auto" }}>
          Counts protected by Laplace DP (ε=1.0) · Scores from trained T-GAT model
        </span>
      </div>

      {/* Tooltip (portal-like, fixed position) */}
      <DistrictTooltip
        district={tooltip.district}
        data={scoreData}
        x={tooltip.x}
        y={tooltip.y}
        visible={tooltip.visible}
      />

      {/* Non-visual live poller */}
      <LiveUpdater onUpdate={handleUpdate} onError={setError} />
    </div>
  );
}
