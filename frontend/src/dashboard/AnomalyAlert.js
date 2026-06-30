/**
 * AnomalyAlert.js — Member C
 * Sidebar panel that lists districts where the T-GAT anomaly score > 0.75 (HIGH risk).
 * Sorted by score descending. Pulses on new alerts.
 */
import React, { useEffect, useRef, useState } from "react";

export default function AnomalyAlert({ scoreData }) {
  const [alerts, setAlerts]       = useState([]);
  const [hasNew, setHasNew]       = useState(false);
  const prevCountRef              = useRef(0);

  useEffect(() => {
    if (!scoreData) return;
    const highRisk = Object.entries(scoreData)
      .filter(([, v]) => v.tier === "HIGH")
      .sort(([, a], [, b]) => b.anomaly_score - a.anomaly_score)
      .map(([district, v]) => ({ district, ...v }));

    if (highRisk.length > prevCountRef.current) {
      setHasNew(true);
      setTimeout(() => setHasNew(false), 2500);
    }
    prevCountRef.current = highRisk.length;
    setAlerts(highRisk);
  }, [scoreData]);

  return (
    <aside
      style={{
        width:         "280px",
        flexShrink:    0,
        background:    "rgba(15, 23, 42, 0.9)",
        border:        `1px solid ${hasNew ? "#ef4444" : "#1e293b"}`,
        borderRadius:  "16px",
        padding:       "20px",
        display:       "flex",
        flexDirection: "column",
        gap:           "12px",
        backdropFilter:"blur(8px)",
        transition:    "border-color 0.4s",
        boxShadow:     hasNew ? "0 0 24px rgba(239,68,68,0.3)" : "none",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontSize: "18px" }}>🚨</span>
        <span
          style={{
            fontWeight: 700,
            fontSize:   "14px",
            color:      "#f1f5f9",
            fontFamily: "'Inter', sans-serif",
          }}
        >
          Anomaly Alerts
        </span>
        {alerts.length > 0 && (
          <span
            style={{
              marginLeft:   "auto",
              background:   "#ef4444",
              color:        "#fff",
              borderRadius: "999px",
              padding:      "2px 8px",
              fontSize:     "11px",
              fontWeight:   700,
            }}
          >
            {alerts.length}
          </span>
        )}
      </div>

      {/* Alert list */}
      {alerts.length === 0 ? (
        <div
          style={{
            color:      "#64748b",
            fontSize:   "12px",
            textAlign:  "center",
            marginTop:  "16px",
            fontFamily: "'Inter', sans-serif",
          }}
        >
          No high-risk districts detected.
          <br />
          System monitoring active.
        </div>
      ) : (
        alerts.map(({ district, anomaly_score, count, tier }) => (
          <div
            key={district}
            style={{
              background:   "rgba(239, 68, 68, 0.08)",
              border:       "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "10px",
              padding:      "12px 14px",
              fontFamily:   "'Inter', sans-serif",
            }}
          >
            <div
              style={{
                fontWeight: 700,
                fontSize:   "13px",
                color:      "#fca5a5",
                marginBottom: "4px",
              }}
            >
              {district}
            </div>
            <div style={{ fontSize: "11px", color: "#94a3b8", lineHeight: "1.6" }}>
              Score: <strong style={{ color: "#ef4444" }}>{(anomaly_score * 100).toFixed(1)}%</strong>
              <br />
              Incidents: <strong style={{ color: "#f1f5f9" }}>{count != null ? count.toFixed(0) : "—"}</strong>
              <br />
              Risk: <strong style={{ color: "#ef4444" }}>HIGH</strong>
            </div>
          </div>
        ))
      )}

      {/* Footer note */}
      <div
        style={{
          marginTop:  "auto",
          fontSize:   "10px",
          color:      "#475569",
          fontFamily: "'Inter', sans-serif",
          borderTop:  "1px solid #1e293b",
          paddingTop: "10px",
        }}
      >
        Scores from T-GAT model. Counts are ε-differentially private (ε=1.0). 
        Updates every 30 seconds.
      </div>
    </aside>
  );
}
