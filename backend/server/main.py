from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "https://civic-shield.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ─────────────────────────────────────────────────

class VoicePayload(BaseModel):
    transcript: str
    district: str = "Unknown"
    language: str = "kn"          # kn = Kannada, hi = Hindi, en = English

class ZKPPayload(BaseModel):
    commitment: str               # hex string of Pedersen commitment
    proof: dict                   # {"value_hash": str, "blinding_hash": str}

class IncidentLog(BaseModel):
    incident_type: str
    district: str
    taluk: str = ""
    severity: float = 0.5
    law_matched: str = ""
    pseudonym: str = ""

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
        
    client_ip = request.client.host if request.client else "unknown"
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
        corrected = resolve_intent(payload.transcript)

        # Step 2: Run LangGraph swarm
        swarm_result = await run_swarm(
            transcript=corrected["resolved_text"],
            incident_type=corrected["incident_type"],
            district=payload.district,
            language=payload.language
        )

        # Step 3: Traverse legal graph for deterministic law matching
        legal_match = traverse_legal_graph(corrected["incident_type"])

        # Step 4: Build PDF complaint strictly in-memory (PII protection)
        pdf_bytes, filename = build_pdf(
            incident_type=corrected["incident_type"],
            district=payload.district,
            law=legal_match,
            narrative=swarm_result.get("narrative", ""),
            authority=legal_match.get("authority", "District Collector")
        )
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # Step 5: Log anonymized incident to Supabase
        await log_incident(IncidentLog(
            incident_type=corrected["incident_type"],
            district=payload.district,
            severity=swarm_result.get("severity", 0.5),
            law_matched=legal_match.get("act", ""),
            pseudonym=swarm_result.get("pseudonym", "Citizen-X")
        ))

        return {
            "success": True,
            "corrected_transcript": corrected["resolved_text"],
            "incident_type": corrected["incident_type"],
            "law_matched": legal_match,
            "authority": legal_match.get("authority"),
            "pdf_filename": filename,
            "pdf_base64": pdf_base64,
            "routing": swarm_result.get("routing"),
            "pseudonym": swarm_result.get("pseudonym")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    """
    try:
        from analytics.graph_builder import get_anomaly_scores
        scores = get_anomaly_scores()
        return scores
    except Exception as e:
        # Return empty scores if analytics not yet ready
        return {"scores": {}, "error": str(e)}

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
