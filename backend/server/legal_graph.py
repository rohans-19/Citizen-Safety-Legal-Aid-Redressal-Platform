"""
legal_graph.py
Deterministic traversal of the Legal Knowledge Graph JSON.
No LLM involved — pure rule-based matching for legal reliability.
"""
import json
import os
from pathlib import Path
from typing import Optional

# ── Load graph once at import time ────────────────────────────────────────────
_GRAPH_PATH = Path(__file__).parent.parent / "data" / "legal_knowledge_graph.json"

with open(_GRAPH_PATH, "r", encoding="utf-8") as f:
    _GRAPH = json.load(f)

_NODES = _GRAPH["nodes"]
_INTENT_MAP = _GRAPH["intent_map"]


def traverse_legal_graph(incident_type: str) -> dict:
    """
    Given a normalised incident_type string, returns the full legal node.
    Falls back to a generic authority + helpline if no match found.

    Args:
        incident_type: e.g. "caste_discrimination", "wage_theft"

    Returns:
        dict with keys: act, sections, authority, helpline, relief_types,
                        escalation_path, timeline_days, compensation_max_inr
    """
    # Normalise key
    key = incident_type.strip().lower().replace(" ", "_").replace("-", "_")

    # Direct lookup
    if key in _NODES:
        return _build_response(key, _NODES[key])

    # Lookup via intent_map aliases
    if key in _INTENT_MAP:
        target_keys = _INTENT_MAP[key]
        if target_keys and target_keys[0] in _NODES:
            return _build_response(target_keys[0], _NODES[target_keys[0]])

    # Keyword search fallback
    for node_key, node in _NODES.items():
        for kw in node.get("keywords", []):
            if kw in key or key in kw:
                return _build_response(node_key, node)

    # Ultimate fallback
    return {
        "node_key": "unknown",
        "label": "General Grievance",
        "act": "Right to Information Act, 2005 / General Grievance Redressal",
        "sections": ["Section 4(1)(b)"],
        "authority": _GRAPH.get("fallback_authority", "District Collector"),
        "helpline": _GRAPH.get("fallback_helpline", "1916"),
        "relief_types": ["Grievance registration", "RTI filing"],
        "escalation_path": ["District Collector", "State Grievance Cell", "PG Portal (pgportal.gov.in)"],
        "timeline_days": 30,
        "compensation_max_inr": 0,
        "matched": False
    }


def _build_response(key: str, node: dict) -> dict:
    """Builds a clean response dict from a graph node."""
    return {
        "node_key": key,
        "label": node.get("label", ""),
        "act": node.get("act", ""),
        "sections": node.get("sections", []),
        "authority": node.get("authority", "District Collector"),
        "helpline": node.get("helpline", "1916"),
        "relief_types": node.get("relief_types", []),
        "escalation_path": node.get("escalation_path", []),
        "timeline_days": node.get("timeline_days", 30),
        "compensation_max_inr": node.get("compensation_max_inr", 0),
        "matched": True
    }


def get_all_incident_types() -> list:
    """Returns all supported incident type keys."""
    return list(_NODES.keys())


def keyword_search(text: str) -> Optional[dict]:
    """
    Searches all nodes for keyword presence in free text.
    Used as a fallback when phonetic parser cannot resolve intent.
    """
    text_lower = text.lower()
    best_match = None
    best_score = 0

    for node_key, node in _NODES.items():
        score = sum(1 for kw in node.get("keywords", []) if kw in text_lower)
        if score > best_score:
            best_score = score
            best_match = (node_key, node)

    if best_match and best_score > 0:
        return _build_response(best_match[0], best_match[1])
    return None
