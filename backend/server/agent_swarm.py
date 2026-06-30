"""
agent_swarm.py
LangGraph multi-agent orchestration swarm — Innovation #6.

5 Agents wired in a directed graph:
  1. Triage Agent     → classifies severity, routes to correct law domain
  2. Narrative Agent  → generates a legally coherent incident narrative
  3. Evidence Agent   → lists what evidence the complainant should collect
  4. Routing Agent    → determines best authority + next action
  5. Empathy Agent    → generates a human message in the user's language

Flow: Triage → Narrative → Evidence → Routing → Empathy
All agents use Gemini 1.5 Flash for speed.
"""
import os
import uuid
from pathlib import Path
from typing import TypedDict, Annotated
from dotenv import load_dotenv

# Explicit path so it works regardless of working directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from google import genai
from langgraph.graph import StateGraph, END

# ── Gemini Setup (lazy — initialized on first call) ───────────────────────────
_GENAI_CLIENT = None
_MODEL_NAME = "gemini-2.0-flash"

def _get_genai_client():
    global _GENAI_CLIENT
    if _GENAI_CLIENT is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in backend/.env")
        _GENAI_CLIENT = genai.Client(api_key=api_key)
    return _GENAI_CLIENT

LANGUAGE_NAMES = {
    "kn": "Kannada",
    "hi": "Hindi",
    "en": "English",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi"
}

# ── Swarm State ───────────────────────────────────────────────────────────────

class SwarmState(TypedDict):
    # Inputs
    transcript: str
    incident_type: str
    district: str
    language: str

    # Populated by agents
    severity: float
    routing: str
    narrative: str
    evidence_list: list
    next_action: str
    empathy_message: str
    pseudonym: str


# ── Utility: Call Gemini safely ───────────────────────────────────────────────

def _call_gemini(prompt: str, fallback: str = "") -> str:
    try:
        client = _get_genai_client()
        response = client.models.generate_content(
            model=_MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            print("[Gemini] API Quota Exceeded (429). Using graceful fallback response.")
        elif "API key not valid" in err_msg or "INVALID_ARGUMENT" in err_msg:
            print("[Gemini] Invalid API Key. Using graceful fallback response.")
        else:
            print(f"[Gemini] Error: {err_msg[:200]}")
        return fallback


# ── Agent 1: Triage ───────────────────────────────────────────────────────────

def triage_agent(state: SwarmState) -> SwarmState:
    """
    Classifies severity (0.0–1.0) and validates routing domain.
    High severity (>0.8) = immediate physical danger → police + helpline
    Medium (0.5–0.8) = legal violation → authority
    Low (<0.5) = administrative issue → complaint portal
    """
    prompt = f"""You are a legal triage AI for India's marginalized communities.
    
Incident: {state['transcript']}
Incident Type: {state['incident_type']}
District: {state['district']}

Rate the SEVERITY from 0.0 (minor) to 1.0 (life-threatening emergency).
Then state the routing: one of [POLICE, AUTHORITY, PORTAL, LEGAL_AID].

Respond in this exact format:
SEVERITY: 0.XX
ROUTING: POLICE|AUTHORITY|PORTAL|LEGAL_AID
REASON: one sentence
"""
    result = _call_gemini(prompt, "SEVERITY: 0.5\nROUTING: AUTHORITY\nREASON: Standard legal grievance.")
    
    severity = 0.5
    routing = "AUTHORITY"
    
    for line in result.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Case-insensitive checking
        upper_line = line.upper()
        if upper_line.startswith("SEVERITY:"):
            try:
                severity = float(line.split(":")[1].strip())
            except Exception:
                pass
        elif upper_line.startswith("ROUTING:"):
            try:
                routing = line.split(":")[1].strip().upper()
            except Exception:
                pass

    return {**state, "severity": severity, "routing": routing}


# ── Agent 2: Narrative ────────────────────────────────────────────────────────

def narrative_agent(state: SwarmState) -> SwarmState:
    """
    Converts the raw voice transcript into a formal legal complaint narrative.
    Output is used directly in the PDF complaint.
    """
    prompt = f"""You are a legal aid paralegal in India helping a marginalized citizen.

Convert the following voice transcript into a formal, legally-phrased complaint narrative 
suitable for submission to Indian courts/authorities. 
Use third-person formal language. Maximum 200 words.
Do NOT add any facts not present in the transcript. 

Transcript: {state['transcript']}
Incident Type: {state['incident_type']}
District: {state['district']}

Write the formal narrative:"""

    narrative = _call_gemini(
        prompt,
        f"The complainant states: \"{state['transcript']}\". This incident occurred in {state['district']} district and requires investigation by the appropriate authorities."
    )

    # Guard: never let 'unknown' appear as incident description in narrative
    if state['incident_type'] == 'unknown' and 'unknown' in narrative.lower():
        narrative = f"The complainant states: \"{state['transcript']}\". The exact legal classification is under review. This incident occurred in {state['district']} district and requires urgent attention from the appropriate authorities."

    pseudonym = "Citizen-" + uuid.uuid4().hex[:4].upper()
    return {**state, "narrative": narrative, "pseudonym": pseudonym}


# ── Agent 3: Evidence ─────────────────────────────────────────────────────────

def evidence_agent(state: SwarmState) -> SwarmState:
    """
    Lists practical, collectible evidence specific to the incident type.
    Output shown to the user as a checklist in the app.
    """
    prompt = f"""You are a legal aid expert helping an Indian citizen with:
Incident: {state['incident_type']}

List exactly 5 specific pieces of evidence they should collect.
Each item must be practical and collectible by an illiterate person with a smartphone.
Format: numbered list, one per line, brief (under 10 words each).

Evidence list:"""

    raw = _call_gemini(
        prompt,
        "1. Photograph of the location\n2. Names of witnesses\n3. Date and time of incident\n4. Any written notice received\n5. Medical records if injured"
    )
    
    evidence_list = [
        line.strip().lstrip("0123456789.-) ")
        for line in raw.split("\n")
        if line.strip() and len(line.strip()) > 5
    ][:5]

    return {**state, "evidence_list": evidence_list}


# ── Agent 4: Routing ──────────────────────────────────────────────────────────

def routing_agent(state: SwarmState) -> SwarmState:
    """
    Determines the specific next action — which office to go to, what to say.
    Tailored to the district and incident type.
    """
    prompt = f"""You are a legal aid navigator for India.

Incident Type: {state['incident_type']}
District: {state['district']}
Routing Decision: {state['routing']}
Severity: {state['severity']}

Give ONE specific, practical next action the complainant must take tomorrow morning.
Include: where to go, what to bring, what to say.
Maximum 3 sentences. Simple language.

Next Action:"""

    next_action = _call_gemini(
        prompt,
        f"Visit the District Collector's office in {state['district']} with your complaint and any documents. Ask for the grievance redressal cell."
    )
    return {**state, "next_action": next_action}


# ── Agent 5: Empathy ──────────────────────────────────────────────────────────

def empathy_agent(state: SwarmState) -> SwarmState:
    """
    Generates a warm, supportive message in the user's native language.
    Critical for trust-building with traumatized users.
    """
    lang_name = LANGUAGE_NAMES.get(state["language"], "English")
    
    prompt = f"""You are a compassionate legal aid assistant.

Write a brief, warm, reassuring message in {lang_name} for a citizen who just 
reported a {state['incident_type']} incident. 
Tell them: we heard you, their complaint has been processed, they are not alone, 
and help is on the way.

Write in {lang_name} script (not transliteration). Maximum 3 sentences.

Message:"""

    empathy_message = _call_gemini(
        prompt,
        "We have received your complaint. You are not alone — help is on the way. Your rights will be protected."
    )
    return {**state, "empathy_message": empathy_message}


# ── Build LangGraph ───────────────────────────────────────────────────────────

def _build_graph() -> object:
    graph = StateGraph(SwarmState)

    # Register nodes
    graph.add_node("triage_node", triage_agent)
    graph.add_node("narrative_node", narrative_agent)
    graph.add_node("evidence_node", evidence_agent)
    graph.add_node("routing_node", routing_agent)
    graph.add_node("empathy_node", empathy_agent)

    # Define flow
    graph.set_entry_point("triage_node")
    graph.add_edge("triage_node", "narrative_node")
    graph.add_edge("narrative_node", "evidence_node")
    graph.add_edge("evidence_node", "routing_node")
    graph.add_edge("routing_node", "empathy_node")
    graph.add_edge("empathy_node", END)

    return graph.compile()


_SWARM = _build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

async def run_swarm(
    transcript: str,
    incident_type: str,
    district: str,
    language: str = "kn"
) -> dict:
    """
    Runs the full 5-agent LangGraph swarm asynchronously.

    Args:
        transcript: Corrected ASR transcript
        incident_type: Canonical incident key from phonetic_parser
        district: District name (e.g. "Belagavi")
        language: ISO 639-1 language code

    Returns:
        dict with severity, routing, narrative, evidence_list, 
        next_action, empathy_message, pseudonym
    """
    initial_state: SwarmState = {
        "transcript": transcript,
        "incident_type": incident_type,
        "district": district,
        "language": language,
        "severity": 0.5,
        "routing": "AUTHORITY",
        "narrative": "",
        "evidence_list": [],
        "next_action": "",
        "empathy_message": "",
        "pseudonym": ""
    }

    final_state = _SWARM.invoke(initial_state)
    return {
        "severity": final_state.get("severity", 0.5),
        "routing": final_state.get("routing", "AUTHORITY"),
        "narrative": final_state.get("narrative", ""),
        "evidence_list": final_state.get("evidence_list", []),
        "next_action": final_state.get("next_action", ""),
        "empathy_message": final_state.get("empathy_message", ""),
        "pseudonym": final_state.get("pseudonym", "Citizen-XXXX")
    }
