import pytest
from server.phonetic_parser import resolve_intent, indian_soundex, levenshtein

def test_indian_soundex():
    # Retroflexes and dental mapping
    assert indian_soundex("Lakshmi") == indian_soundex("Laksmi")
    assert indian_soundex("caste") != ""

def test_levenshtein():
    assert levenshtein("caste", "caste") == 0
    assert levenshtein("caste", "cast") == 1
    assert levenshtein("caste", "kaste") == 1

def test_resolve_intent_abbreviations():
    # Test abbreviation mapping
    res = resolve_intent("sc st abuse in village")
    assert res["incident_type"] == "caste_discrimination"
    assert res["method"] == "abbreviation_match"

    res = resolve_intent("posh harassment at work")
    assert res["incident_type"] == "sexual_harassment_workplace"
    assert res["method"] == "abbreviation_match"

def test_resolve_intent_keywords():
    # Test keyword matching
    res = resolve_intent("my husband beat me at home and demanded dowry")
    assert res["incident_type"] == "domestic_violence"
    assert res["method"] == "keyword_match"

def test_resolve_intent_soundex():
    # Test phonetic Soundex match for Indian romanization
    res = resolve_intent("insulted casst on road")
    assert res["incident_type"] == "caste_discrimination"
    assert res["method"] == "soundex_phonetic"

def test_resolve_intent_hint_fallback():
    # Test fallback using direct key hint
    res = resolve_intent("xyz abc qrs", hint="domestic_violence")
    assert res["incident_type"] == "domestic_violence"
    assert res["method"] == "hint_fallback"

    # Test fallback using keyword hint
    res = resolve_intent("xyz abc qrs", hint="dalit")
    assert res["incident_type"] == "caste_discrimination"
    assert res["method"] == "hint_vocab_fallback"
