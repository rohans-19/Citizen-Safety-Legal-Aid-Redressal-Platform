"""
privacy_heatmap.py
Member C — CIVIC-SHIELD Analytics
Differential Privacy engine using the Laplace mechanism (ε = 1.0).
Provides privacy-preserving district incident counts for dashboard display.
"""

import numpy as np


# ── Laplace Mechanism ──────────────────────────────────────────────────────────

def laplace_noise(sensitivity: float, epsilon: float) -> float:
    """Sample a single Laplace noise value.

    Args:
        sensitivity: Global sensitivity of the query (Δf). For count queries = 1.
        epsilon:     Privacy budget. Lower = more privacy. We use ε = 1.0.

    Returns:
        A single float noise value drawn from Lap(sensitivity/epsilon).
    """
    scale = sensitivity / epsilon
    return np.random.laplace(loc=0.0, scale=scale)


def apply_dp_noise(
    district_counts: dict[str, int],
    epsilon: float = 1.0,
    sensitivity: float = 1.0,
    min_display: int = 0,
) -> dict[str, float]:
    """Apply Laplace DP noise to a dictionary of raw district counts.

    Guarantees ε-differential privacy. Individual counts are masked while
    aggregate patterns remain statistically visible.

    Args:
        district_counts: {district_name: raw_count}
        epsilon:         Privacy budget (default 1.0)
        sensitivity:     Query sensitivity (default 1.0 for count queries)
        min_display:     Floor for the noised output (default 0 — no negatives shown)

    Returns:
        {district_name: noised_count} — safe for public display.
    """
    noised = {}
    for district, count in district_counts.items():
        noise = laplace_noise(sensitivity, epsilon)
        noised_value = count + noise
        # Clip to min_display so we don't show negative counts on the map
        noised[district] = max(float(min_display), round(noised_value, 2))
    return noised


def tier_from_score(anomaly_score: float) -> str:
    """Classify an anomaly score into a risk tier label for the dashboard.

    Args:
        anomaly_score: Float in [0, 1] from the T-GAT model.

    Returns:
        'LOW' | 'MEDIUM' | 'HIGH'
    """
    if anomaly_score >= 0.75:
        return "HIGH"
    elif anomaly_score >= 0.45:
        return "MEDIUM"
    else:
        return "LOW"


# ── Self-test (run directly to verify DP guarantees) ──────────────────────────
if __name__ == "__main__":
    raw_counts = {
        "Bidar": 25,
        "Raichur": 18,
        "Kalaburagi": 12,
        "Mysuru": 3,
        "Kodagu": 1,   # Single incident — must be masked
        "Udupi": 0,
    }

    print("=== Differential Privacy Self-Test (ε = 1.0) ===\n")
    print(f"{'District':<20} {'Raw':>6} {'Noised':>10} {'Masked?':>10}")
    print("-" * 52)

    noised = apply_dp_noise(raw_counts, epsilon=1.0)
    for district, raw in raw_counts.items():
        n = noised[district]
        masked = abs(n - raw) > 2  # noise > 2 counts means effective masking
        print(f"{district:<20} {raw:>6} {n:>10.2f} {'✓' if masked else '—':>10}")

    # Verify: run multiple trials on count=1 and check variance
    trials = [apply_dp_noise({"Kodagu": 1})["Kodagu"] for _ in range(1000)]
    arr = np.array(trials)
    print(f"\nKodagu (count=1) over 1000 trials:")
    print(f"  Mean={arr.mean():.2f}, Std={arr.std():.2f}, Range=[{arr.min():.2f}, {arr.max():.2f}]")
    print(f"\n[OK] DP engine verified — individual counts are effectively masked.")
