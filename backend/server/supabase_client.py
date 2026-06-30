"""
supabase_client.py
Supabase PostgreSQL client for CIVIC-SHIELD.
All data is anonymized before storage — no PII ever written to DB.
"""
import os
import hashlib
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# ── Client Setup ──────────────────────────────────────────────────────────────
_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

_client: Client = None

def _get_client() -> Client:
    global _client
    if _client is None:
        if not _SUPABASE_URL or not _SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        _client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
    return _client


# ── Pseudonymization ──────────────────────────────────────────────────────────

def generate_pseudonym() -> str:
    """Generates a short anonymous ID like 'Citizen-A7F2'."""
    return "Citizen-" + uuid.uuid4().hex[:4].upper()

def hash_identifier(value: str) -> str:
    """One-way SHA256 hash for any identifier that must not be stored in plaintext."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


# ── Incident Logging ──────────────────────────────────────────────────────────

async def log_incident(payload) -> str:
    """
    Logs an anonymized incident to the `incidents` table.
    
    Schema expected in Supabase:
    CREATE TABLE incidents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        incident_type TEXT NOT NULL,
        district TEXT NOT NULL,
        taluk TEXT DEFAULT '',
        severity FLOAT DEFAULT 0.5,
        law_matched TEXT DEFAULT '',
        pseudonym TEXT DEFAULT '',
        created_at TIMESTAMPTZ DEFAULT now()
    );

    Args:
        payload: IncidentLog pydantic model from main.py

    Returns:
        Inserted row ID as string
    """
    try:
        client = _get_client()
        record = {
            "incident_type": payload.incident_type,
            "district": payload.district,
            "taluk": payload.taluk or "",
            "severity": payload.severity,
            "law_matched": payload.law_matched or "",
            "pseudonym": payload.pseudonym or generate_pseudonym(),
            "created_at": datetime.utcnow().isoformat()
        }
        response = client.table("civic_incidents").insert(record).execute()
        if response.data:
            return response.data[0].get("id", "unknown")
        return "inserted"
    except Exception as e:
        # Log to console but don't crash the API — analytics loss is acceptable
        print(f"[Supabase] log_incident failed: {e}")
        return "error"


# ── Analytics Queries ─────────────────────────────────────────────────────────

def get_incidents_by_district(district: str, limit: int = 100) -> list:
    """Fetches recent anonymized incidents for a given district."""
    try:
        client = _get_client()
        response = (
            client.table("civic_incidents")
            .select("incident_type, district, taluk, severity, law_matched, created_at")
            .eq("district", district)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[Supabase] get_incidents_by_district failed: {e}")
        return []


def get_district_summary() -> list:
    """
    Returns incident counts grouped by district.
    Used by T-GAT analytics and the NGO heatmap.
    """
    try:
        client = _get_client()
        # Raw SQL via Supabase RPC (create this function in Supabase SQL editor)
        response = client.rpc("district_incident_summary").execute()
        return response.data or []
    except Exception as e:
        # Fallback: manual grouping
        print(f"[Supabase] district_summary RPC failed, using fallback: {e}")
        try:
            client = _get_client()
            response = client.table("civic_incidents").select("district, incident_type, severity").execute()
            data = response.data or []
            summary: dict = {}
            for row in data:
                d = row["district"]
                summary[d] = summary.get(d, {"district": d, "count": 0, "avg_severity": 0})
                summary[d]["count"] += 1
                summary[d]["avg_severity"] = (
                    (summary[d]["avg_severity"] * (summary[d]["count"] - 1) + row["severity"])
                    / summary[d]["count"]
                )
            return list(summary.values())
        except Exception as e2:
            print(f"[Supabase] fallback also failed: {e2}")
            return []


def get_recent_incidents(limit: int = 50) -> list:
    """Returns the most recent anonymized incidents for live dashboard feed."""
    try:
        client = _get_client()
        response = (
            client.table("civic_incidents")
            .select("incident_type, district, severity, law_matched, pseudonym, created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[Supabase] get_recent_incidents failed: {e}")
        return []


def health_check() -> bool:
    """Quick connectivity check to Supabase."""
    try:
        client = _get_client()
        client.table("civic_incidents").select("id").limit(1).execute()
        return True
    except Exception:
        return False
