"""
anomaly_api.py
Member C — CIVIC-SHIELD Analytics
FastAPI analytics sub-app. Exposes /anomaly-scores endpoint.
Run as: uvicorn analytics.anomaly_api:app --port 8001 --reload
"""

import os
import sys

import torch
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Path setup so imports resolve from backend/ root ──────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "..")
sys.path.insert(0, BACKEND_DIR)

load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, ".env"))

from analytics.graph_builder import build_graph        # noqa: E402
from analytics.privacy_heatmap import apply_dp_noise, tier_from_score  # noqa: E402
from analytics.tgat_anomaly import TGATAnomalyDetector, WEIGHTS_PATH   # noqa: E402

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="CIVIC-SHIELD Analytics API", version="1.0.0")


def _split_origins(value: str) -> list[str]:
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


def _allowed_origins() -> list[str]:
    configured = _split_origins(os.getenv("CORS_ORIGINS", ""))
    frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
    if frontend_url:
        configured.append(frontend_url)
    defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    return sorted(set(configured + defaults))


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Load model once at startup ─────────────────────────────────────────────────
_model: TGATAnomalyDetector | None = None


def get_model() -> TGATAnomalyDetector:
    global _model
    if _model is None:
        _model = TGATAnomalyDetector()
        if os.path.exists(WEIGHTS_PATH):
            _model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
            print("[OK] T-GAT weights loaded.")
        else:
            print("[Warning] tgat_weights.pt not found — using untrained model. Run tgat_anomaly.py first.")
        _model.eval()
    return _model


@app.on_event("startup")
async def startup_event():
    get_model()


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics"}


@app.get("/anomaly-scores")
async def anomaly_scores():
    """Compute and return per-district anomaly scores with DP-noised incident counts.

    Response schema:
    {
      "Bidar": {"count": 12.3, "anomaly_score": 0.87, "tier": "HIGH"},
      "Raichur": {"count": 8.1, "anomaly_score": 0.72, "tier": "MEDIUM"},
      ...
    }
    """
    # 1. Build live graph from Supabase
    data, district_names, raw_counts = build_graph()

    # 2. Run T-GAT inference
    model = get_model()
    with torch.no_grad():
        scores = model(data).squeeze()  # [31]

    # 3. Apply Differential Privacy to counts
    noised_counts = apply_dp_noise(raw_counts, epsilon=1.0)

    # 4. Build response
    result = {}
    for i, name in enumerate(district_names):
        score = float(scores[i].item())
        result[name] = {
            "count":         noised_counts.get(name, 0.0),
            "anomaly_score": round(score, 4),
            "tier":          tier_from_score(score),
        }

    return result


if __name__ == "__main__":
    import uvicorn
    # Add backend/ to python path so uvicorn can find the module when reload is enabled
    sys.path.insert(0, BACKEND_DIR)
    uvicorn.run("analytics.anomaly_api:app", host="127.0.0.1", port=8001, reload=True)

