/**
 * LiveUpdater.js — Member C
 * Polls /anomaly-scores every 30 seconds and calls onUpdate with fresh data.
 * Usage: mount once at the root dashboard. Unmounts cleanly.
 */
import { useEffect, useRef } from "react";

const POLL_INTERVAL_MS = 30_000;

export default function LiveUpdater({ onUpdate, onError }) {
  const timerRef = useRef(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8001";

  const fetchScores = async () => {
    try {
      const res = await fetch(`${backendUrl}/anomaly-scores`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      onUpdate(data);
    } catch (err) {
      console.error("[LiveUpdater] Fetch failed:", err.message);
      if (onError) onError(err.message);
    }
  };

  useEffect(() => {
    // Immediate first fetch
    fetchScores();
    // Then poll every 30 seconds
    timerRef.current = setInterval(fetchScores, POLL_INTERVAL_MS);
    return () => clearInterval(timerRef.current);
  }, []);

  return null; // non-visual component
}
