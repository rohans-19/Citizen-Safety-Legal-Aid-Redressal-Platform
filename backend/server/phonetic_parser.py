"""
phonetic_parser.py
Indian Soundex + Levenshtein distance corrector for ASR output.

Handles:
  - Dialect variations: "Gruha Laksmi" → "Gruha Lakshmi"
  - Phonetic misspellings: "SC ST act" → "caste_discrimination"
  - Code-switched speech: Kannada/Hindi words in English ASR output
  - Abbreviation expansion: "MNREGA" → "mnrega_denial"

Innovation #4: Phonetic Speech-to-Intent Parser
"""
import re
import unicodedata
from typing import Optional

# ── Intent Vocabulary ─────────────────────────────────────────────────────────
# Maps canonical intent keys to lists of phonetic variants and trigger phrases

INTENT_VOCABULARY = {
    "caste_discrimination": [
        "caste", "dalit", "sc", "st", "atrocity", "untouchability",
        "discrimination", "harijan", "banjara", "lambada", "oppression",
        "jati", "jaati", "varna", "ambedkar", "reserved", "humiliated caste",
        "called names", "jati ke naam", "sc st", "scheduled caste",
        "scheduled tribe", "prevent from temple", "barred entry",
        "upper caste", "lower caste", "brahmin", "OBC abuse",
        "gruhaa lakshmi sc", "caste atrocity", "ssc", "sebc"
    ],
    "domestic_violence": [
        "domestic", "husband", "wife", "beaten", "beat", "abuse",
        "violence", "dowry", "harassment", "marital", "battered",
        "pati", "gharelu hinsa", "stree", "mahila", "ghar mein",
        "pita raha", "mara", "maar", "dowry death", "498a",
        "domestic abuse", "home violence", "ghar pe maar",
        "in laws", "sasural", "family violence"
    ],
    "sexual_harassment_workplace": [
        "sexual harassment", "posh", "workplace", "boss", "colleague",
        "molested", "touched", "inappropriate", "unwanted", "office",
        "job", "superior", "manager", "sexual advance", "groping",
        "dirty jokes", "hostile work", "gender discrimination",
        "yoni peedan", "laiṅgik utpīṛan"
    ],
    "wage_theft": [
        "salary", "wages", "not paid", "money withheld", "labour",
        "worker", "employer", "bonus", "dues", "payment pending",
        "mazdoor", "vetana", "tankhwa", "kaam ke paise", "paisa nahi",
        "mujhe paise do", "contract labour", "daily wage", "minimum wage",
        "unpaid", "payroll", "overdue salary", "salary cut"
    ],
    "mnrega_denial": [
        "mnrega", "nrega", "job card", "100 days", "rural work",
        "gram panchayat", "muster roll", "work not given", "employment",
        "sarpanch cheating", "job card nahi", "kaam nahi mila",
        "rozgar guarantee", "mgnrega", "rozgar", "gram sabha work"
    ],
    "disability_discrimination": [
        "disability", "disabled", "handicap", "wheelchair", "blind",
        "deaf", "differently abled", "special needs", "rpwd", "viklang",
        "divyang", "andha", "bahira", "pahiya kursi", "prosthetic",
        "barrier", "ramp not given", "accessible", "disability card"
    ],
    "pension_denial": [
        "pension", "old age", "widow pension", "disability pension",
        "social security", "not receiving", "stopped pension",
        "budhapa", "vidhwa", "vridha", "pension band ho gaya",
        "pension nahi aa raha", "vriddha pension", "nsap",
        "ignoaps", "old age home", "senior citizen"
    ],
    "ration_denial": [
        "ration", "pds", "fair price shop", "ration card", "food",
        "rice", "wheat", "grain", "not giving ration", "ration denied",
        "anna bhagya", "ration dukan", "kerosene", "subsidized food",
        "ration shop closed", "weight less", "short weight",
        "fpds", "nfsa", "sasta anaj", "bpl card"
    ],
    "healthcare_denial": [
        "hospital", "treatment", "ayushman", "pmjay", "health card",
        "denied treatment", "medicine", "doctor refused", "emergency",
        "icu", "ambulance", "operation denied", "arogya", "swasthya",
        "ilaj", "dawai nahi", "hospital ne bhaga diya", "bedside",
        "free treatment", "cashless", "insurance card rejected"
    ],
    "child_labour": [
        "child labour", "child work", "minor working", "school dropout",
        "child factory", "balmazdoori", "bachcha", "chota ladka kaam",
        "hotel pe kaam", "dhaba pe ladka", "underage working",
        "forced child", "child servant", "bonded child"
    ],
    "bonded_labour": [
        "bonded labour", "forced work", "debt bondage", "slavery",
        "bandhua", "cannot leave", "imprisoned working", "bandhua mazdoor",
        "forced to work", "held against will", "debt trap work",
        "advance taken cannot go", "farm bondage"
    ],
    "land_encroachment": [
        "land", "eviction", "encroachment", "forest rights", "patta",
        "tribal land", "dispossession", "bulldozer", "zameen",
        "mera zameen", "van adhikar", "pattas nahi", "PESA",
        "forest act", "writ of possession", "khata khatauni",
        "land record", "revenue record", "phaisal"
    ]
}

# ── Indian Soundex ────────────────────────────────────────────────────────────

SOUNDEX_TABLE = {
    'A': '0', 'E': '0', 'I': '0', 'O': '0', 'U': '0', 'H': '0', 'W': '0', 'Y': '0',
    'B': '1', 'F': '1', 'P': '1', 'V': '1',
    'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
    'D': '3', 'T': '3',
    'L': '4',
    'M': '5', 'N': '5',
    'R': '6',
    # Indian-specific: retroflexes map to same code as their dental pair
    'Ṭ': '3', 'Ḍ': '3', 'Ṇ': '5', 'Ś': '2', 'Ṣ': '2', 'Ḥ': '0', 'Ṃ': '5'
}


def indian_soundex(word: str) -> str:
    """
    Computes an Indian-variant Soundex code for a word.
    Handles transliterated Kannada/Hindi words more reliably than standard Soundex.
    """
    if not word:
        return ""
    word = word.upper().strip()
    # Normalize unicode (Kannada romanizations)
    word = unicodedata.normalize("NFKD", word)
    word = re.sub(r'[^A-Z]', '', word)
    if not word:
        return ""

    first = word[0]
    code = first
    prev_digit = SOUNDEX_TABLE.get(first, '0')

    for char in word[1:]:
        digit = SOUNDEX_TABLE.get(char, '0')
        if digit != '0' and digit != prev_digit:
            code += digit
        prev_digit = digit
        if len(code) == 4:
            break

    return code.ljust(4, '0')


def levenshtein(s1: str, s2: str) -> int:
    """Standard Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for c1 in s1:
        curr = [prev[0] + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


# ── Abbreviation Expansion ────────────────────────────────────────────────────

ABBREVIATIONS = {
    "sc st": "caste_discrimination",
    "scst": "caste_discrimination",
    "498a": "domestic_violence",
    "pocso": "child_labour",
    "posh": "sexual_harassment_workplace",
    "nrega": "mnrega_denial",
    "mnrega": "mnrega_denial",
    "mgnrega": "mnrega_denial",
    "pds": "ration_denial",
    "pmjay": "healthcare_denial",
    "ayushman": "healthcare_denial",
    "rpwd": "disability_discrimination",
    "nsap": "pension_denial",
    "fra": "land_encroachment",
    "pesa": "land_encroachment",
}

# Pre-build soundex index for all vocabulary terms
_SOUNDEX_INDEX: dict[str, list[str]] = {}
for _intent, _terms in INTENT_VOCABULARY.items():
    for _term in _terms:
        for _word in _term.split():
            _code = indian_soundex(_word)
            if _code not in _SOUNDEX_INDEX:
                _SOUNDEX_INDEX[_code] = []
            if _intent not in _SOUNDEX_INDEX[_code]:
                _SOUNDEX_INDEX[_code].append(_intent)


# ── Main Resolution Function ──────────────────────────────────────────────────

def resolve_intent(raw_transcript: str) -> dict:
    """
    Takes raw ASR transcript and returns:
      - resolved_text: corrected text
      - incident_type: canonical intent key
      - confidence: 0.0 - 1.0
      - method: how the match was found

    Args:
        raw_transcript: Raw speech-to-text output, may contain errors.

    Returns:
        dict with resolved_text, incident_type, confidence, method
    """
    text = raw_transcript.strip().lower()

    # Step 1: Check abbreviations first (fast, exact)
    for abbr, intent in ABBREVIATIONS.items():
        if abbr in text:
            return {
                "resolved_text": text,
                "incident_type": intent,
                "confidence": 0.95,
                "method": "abbreviation_match"
            }

    # Step 2: Direct keyword substring match
    scores: dict[str, float] = {}
    for intent, terms in INTENT_VOCABULARY.items():
        score = 0.0
        for term in terms:
            if term in text:
                # Longer matches score higher
                score += len(term.split()) * 1.5
        if score > 0:
            scores[intent] = score

    if scores:
        best_intent = max(scores, key=scores.__getitem__)
        confidence = min(scores[best_intent] / 10.0, 0.98)
        return {
            "resolved_text": text,
            "incident_type": best_intent,
            "confidence": confidence,
            "method": "keyword_match"
        }

    # Step 3: Soundex phonetic matching for each word
    words = re.findall(r'\b\w+\b', text)
    soundex_scores: dict[str, int] = {}
    for word in words:
        code = indian_soundex(word)
        if code in _SOUNDEX_INDEX:
            for intent in _SOUNDEX_INDEX[code]:
                soundex_scores[intent] = soundex_scores.get(intent, 0) + 1

    if soundex_scores:
        best_intent = max(soundex_scores, key=soundex_scores.__getitem__)
        confidence = min(soundex_scores[best_intent] / 5.0, 0.75)
        return {
            "resolved_text": text,
            "incident_type": best_intent,
            "confidence": confidence,
            "method": "soundex_phonetic"
        }

    # Step 4: Levenshtein fuzzy match on individual words against all vocab terms
    best_intent = "unknown"
    best_distance = 999
    for word in words:
        if len(word) < 4:
            continue
        for intent, terms in INTENT_VOCABULARY.items():
            for term in terms:
                term_word = term.split()[0]  # Compare against first word of each term
                dist = levenshtein(word, term_word)
                if dist < best_distance and dist <= 2:
                    best_distance = dist
                    best_intent = intent

    if best_intent != "unknown":
        confidence = max(0.3, 1.0 - (best_distance / 5.0))
        return {
            "resolved_text": text,
            "incident_type": best_intent,
            "confidence": confidence,
            "method": "levenshtein_fuzzy"
        }

    # Step 5: Total fallback
    return {
        "resolved_text": text,
        "incident_type": "unknown",
        "confidence": 0.0,
        "method": "no_match"
    }


def get_all_intent_types() -> list:
    """Returns all canonical intent keys."""
    return list(INTENT_VOCABULARY.keys())
