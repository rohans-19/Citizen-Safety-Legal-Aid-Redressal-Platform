/**
 * DistrictTooltip.js — Member C
 * Hover tooltip showing DP-noised incident count + T-GAT anomaly score.
 * Positioned absolutely; parent must have position: relative.
 */
import React from "react";

const TIER_COLOR = {
  HIGH:   "#ef4444",
  MEDIUM: "#f59e0b",
  LOW:    "#22c55e",
};

export default function DistrictTooltip({ district, data, x, y, visible }) {
  if (!visible || !district || !data) return null;

  const info   = data[district] || {};
  const count  = info.count != null ? info.count.toFixed(1) : "—";
  const score  = info.anomaly_score != null ? (info.anomaly_score * 100).toFixed(1) : "—";
  const tier   = info.tier || "LOW";
  const color  = TIER_COLOR[tier];

  return (
    <div
      style={{
        position: "fixed",
        left:     x + 12,
        top:      y - 10,
        zIndex:   1000,
        pointerEvents: "none",
        background:    "rgba(15, 23, 42, 0.95)",
        border:        `1.5px solid ${color}`,
        borderRadius:  "10px",
        padding:       "10px 16px",
        minWidth:      "190px",
        boxShadow:     `0 4px 24px rgba(0,0,0,0.4), 0 0 12px ${color}40`,
        fontFamily:    "'Inter', sans-serif",
        color:         "#f1f5f9",
        transition:    "opacity 0.15s",
      }}
    >
      <div style={{ fontWeight: 700, fontSize: "14px", marginBottom: "6px" }}>
        {district}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "4px", fontSize: "12px" }}>
        <span style={{ color: "#94a3b8" }}>
          Incidents (DP-noised):{" "}
          <strong style={{ color: "#f1f5f9" }}>{count}</strong>
        </span>
        <span style={{ color: "#94a3b8" }}>
          Anomaly score:{" "}
          <strong style={{ color }}>{score}%</strong>
        </span>
        <span
          style={{
            marginTop: "4px",
            padding:   "2px 8px",
            borderRadius: "999px",
            background: `${color}20`,
            color,
            fontWeight: 700,
            fontSize:   "11px",
            display:    "inline-block",
            alignSelf:  "flex-start",
          }}
        >
          {tier} RISK
        </span>
      </div>
    </div>
  );
}
