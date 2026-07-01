from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

from server.legal_graph import traverse_legal_graph
from server.phonetic_parser import resolve_intent
from server.agent_swarm import run_swarm
from server.supabase_client import log_incident
from server.zkp_verifier import verify_commitment
from server.pdf_builder import build_pdf
from server.threat_detector import detect_threat

app = FastAPI(
    title="CIVIC-SHIELD API",
    description="Socio-Legal Safety, Grievance & Anomaly Detection System",
    version="1.0.0"
)

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


# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Member C's Analytics sub-app ────────────────────────────────────────
try:
    from analytics.anomaly_api import app as analytics_app
    app.mount("/analytics", analytics_app)
except Exception as e:
    print(f"[Warning] Failed to mount analytics sub-app: {e}")

# ── Optional Static Files ────────────────────────────────────────────────────
# Complaint PDFs are returned in-memory by default. Serving generated files is
# opt-in only, because public static PDFs are a privacy footgun.
if os.getenv("ENABLE_PDF_FILE_SERVE", "false").lower() == "true":
    os.makedirs("generated_pdfs", exist_ok=True)
    app.mount("/generated_pdfs", StaticFiles(directory="generated_pdfs"), name="generated_pdfs")

# ── Request / Response Models ─────────────────────────────────────────────────

class VoicePayload(BaseModel):
    transcript: str = Field(..., min_length=3, max_length=5000)
    district: str = Field(default="Unknown", max_length=80)
    language: str = Field(default="kn", pattern="^(kn|hi|en|te|ta|mr)$")
    incident_type_hint: str = Field(default="", max_length=80)

class ZKPPayload(BaseModel):
    commitment: str = Field(..., min_length=8, max_length=600)
    proof: dict = Field(default_factory=dict)

class IncidentLog(BaseModel):
    incident_type: str = Field(..., min_length=2, max_length=80)
    district: str = Field(..., min_length=2, max_length=80)
    taluk: str = Field(default="", max_length=80)
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    law_matched: str = Field(default="", max_length=240)
    pseudonym: str = Field(default="", max_length=80)

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "CIVIC-SHIELD Backend v1.0"}

# ── Simple IP-Based Rate Limiting Middleware ─────────────────────────────────
import time
from fastapi import Request
from fastapi.responses import JSONResponse

# Store IP request counts: {ip: [timestamp1, timestamp2, ...]}
_RATE_LIMIT_DB = {}
_LIMIT_WINDOW_SEC = 60
_MAX_REQUESTS_PER_WINDOW = 30

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    # Exclude health check from rate limiting
    if request.url.path == "/health":
        return await call_next(request)
        
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
    now = time.time()
    
    # Initialize list for new IP
    if client_ip not in _RATE_LIMIT_DB:
        _RATE_LIMIT_DB[client_ip] = []
        
    # Remove timestamps older than the window
    _RATE_LIMIT_DB[client_ip] = [t for t in _RATE_LIMIT_DB[client_ip] if now - t < _LIMIT_WINDOW_SEC]
    
    if len(_RATE_LIMIT_DB[client_ip]) >= _MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests. Rate limit exceeded (30 requests/min)."}
        )
        
    _RATE_LIMIT_DB[client_ip].append(now)
    return await call_next(request)

# ── Core Voice Processing ─────────────────────────────────────────────────────
import base64

@app.post("/process-voice", tags=["Core"])
async def process_voice(payload: VoicePayload):
    """
    Main pipeline:
    1. Phonetic parser corrects ASR errors in transcript
    2. LangGraph swarm processes corrected intent
    3. Legal graph traversal returns matched law + authority
    4. PDF complaint generated in-memory (returned as Base64)
    5. Incident logged to Supabase (anonymized)
    Returns: law match, authority, PDF Base64 string, routing decision
    """
    try:
        # Step 1: Correct ASR errors via phonetic parser
        corrected = resolve_intent(payload.transcript, hint=payload.incident_type_hint)

        # Step 2: Traverse legal graph for deterministic law matching (RAG step)
        legal_match = traverse_legal_graph(corrected["incident_type"])

        # Step 3: Run LangGraph swarm with legal match context injected
        # Use frontend-provided district as primary (from geolocation), not "Unknown"
        effective_district = payload.district if payload.district and payload.district.lower() != 'unknown' else ''
        swarm_result = await run_swarm(
            transcript=corrected["resolved_text"],
            incident_type=corrected["incident_type"],
            district=effective_district,
            language=payload.language,
            legal_match=legal_match
        )
        resolved_district = swarm_result.get("district", payload.district)

        # Step 4: Build PDF complaint strictly in-memory (PII protection)
        pdf_bytes, filename = build_pdf(
            incident_type=corrected["incident_type"],
            district=resolved_district,
            law=legal_match,
            narrative=swarm_result.get("narrative", ""),
            authority=legal_match.get("authority", "District Collector"),
            complainant_id=swarm_result.get("pseudonym", "Anonymous Citizen"),
            raw_transcript=payload.transcript
        )
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # Step 5: Log anonymized incident to Supabase
        db_logged = True
        try:
            await log_incident(IncidentLog(
                incident_type=corrected["incident_type"],
                district=resolved_district,
                severity=swarm_result.get("severity", 0.5),
                law_matched=legal_match.get("act", ""),
                pseudonym=swarm_result.get("pseudonym", "Citizen-X")
            ))
        except Exception as db_err:
            print(f"[DB] Supabase log failed (non-fatal): {db_err}")
            db_logged = False

        return {
            "success": True,
            "corrected_transcript": corrected["resolved_text"],
            "incident_type": corrected["incident_type"] if corrected["incident_type"] != "unknown" else "under_review",
            "law_matched": legal_match,
            "authority": legal_match.get("authority"),
            "district": resolved_district,
            "pdf_filename": filename,
            "pdf_base64": pdf_base64,
            "routing": swarm_result.get("routing"),
            "pseudonym": swarm_result.get("pseudonym"),
            "evidence_list": swarm_result.get("evidence_list", []),
            "next_action": swarm_result.get("next_action", ""),
            "empathy_message": swarm_result.get("empathy_message", ""),
            "severity": swarm_result.get("severity", 0.5),
            "db_logged": db_logged,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Unable to process the complaint safely right now. Please retry or contact legal aid."
        )

# ── Threat Detection ──────────────────────────────────────────────────────────

@app.post("/detect-threat", tags=["Safety"])
async def detect_threat_endpoint(audio: UploadFile = File(...)):
    """
    Accepts raw audio bytes.
    Runs AST (Audio Spectrogram Transformer) model on AudioSet classes.
    Returns threat label + probability.
    """
    try:
        audio_bytes = await audio.read()
        result = detect_threat(audio_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── ZKP Verification ──────────────────────────────────────────────────────────

@app.post("/verify-zkp", tags=["Privacy"])
def verify_zkp(payload: ZKPPayload):
    """
    Verifies a Pedersen commitment received from the client ZKP wallet.
    Returns True if commitment matches proof without revealing the actual value.
    """
    try:
        result = verify_commitment(payload.commitment, payload.proof)
        return {"verified": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── Legal Graph Query ─────────────────────────────────────────────────────────

@app.get("/legal-graph/{incident_type}", tags=["Legal"])
def query_legal_graph(incident_type: str):
    """
    Direct legal knowledge graph query.
    Returns matched act, sections, relief types, authority, and helplines.
    """
    result = traverse_legal_graph(incident_type)
    if not result:
        raise HTTPException(status_code=404, detail=f"No law found for: {incident_type}")
    return result

# ── Anomaly Scores (proxied from analytics service) ──────────────────────────

@app.get("/anomaly-scores", tags=["Analytics"])
async def get_anomaly_scores():
    """
    Returns T-GAT anomaly scores per district.
    Called by the NGO dashboard every 30 seconds.
    Proxies to the mounted Analytics sub-app logic.
    """
    try:
        from analytics.anomaly_api import anomaly_scores
        return await anomaly_scores()
    except Exception as e:
        return _demo_anomaly_scores(str(e))


def _demo_anomaly_scores(error: str = "") -> dict:
    districts = [
        "Bagalkote", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
        "Bidar", "Chamarajanagara", "Chikkaballapur", "Chikkamagaluru", "Chitradurga",
        "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan",
        "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal",
        "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga",
        "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir", "Vijayanagara",
    ]
    elevated = {
        "Bidar": (18.4, 0.86),
        "Raichur": (14.2, 0.79),
        "Kalaburagi": (10.7, 0.66),
        "Belagavi": (7.3, 0.51),
    }
    result = {}
    for index, district in enumerate(districts):
        count, score = elevated.get(district, (round((index % 4) * 1.3, 2), 0.18 + (index % 5) * 0.045))
        result[district] = {
            "count": count,
            "anomaly_score": round(score, 4),
            "tier": "HIGH" if score >= 0.75 else "MEDIUM" if score >= 0.45 else "LOW",
        }
    if error:
        result["_meta"] = {"mode": "demo_fallback", "reason": error[:160]}
    return result

# ── Log Incident (called internally) ─────────────────────────────────────────

@app.post("/log-incident", tags=["Analytics"])
async def log_incident_endpoint(payload: IncidentLog):
    """
    Logs an anonymized incident to Supabase.
    Called by Member C's scripts and internally by process-voice.
    """
    try:
        result = await log_incident(payload)
        return {"success": True, "id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
