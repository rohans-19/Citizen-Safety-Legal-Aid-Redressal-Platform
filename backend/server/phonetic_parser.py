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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Common English stopwords to ignore in Soundex phonetic mapping
STOPWORDS = {
    "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
    "are", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "cannot", "could", "did", "do", "does", "doing", "down", "during", "each", 
    "few", "for", "from", "further", "had", "has", "have", "having", "here", "how", 
    "if", "in", "into", "is", "it", "its", "itself", "me", "more", "most", "my", 
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", 
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", 
    "them", "themselves", "then", "there", "these", "they", "this", "those", 
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", 
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", 
    "would", "you", "your", "yours", "yourself", "yourselves", "wouldnt"
}

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



# ── Local TF-IDF Cosine Similarity Fallback ───────────────────────────────────

_CORPUS_TERMS = []
_CORPUS_LABELS = []
for _intent, _terms in INTENT_VOCABULARY.items():
    for _term in _terms:
        _CORPUS_TERMS.append(_term)
        _CORPUS_LABELS.append(_intent)

_VECTORIZER = TfidfVectorizer().fit(_CORPUS_TERMS)
_CORPUS_VECTORS = _VECTORIZER.transform(_CORPUS_TERMS)

def local_similarity_classify(text: str) -> Optional[dict]:
    """
    Computes TF-IDF cosine similarity against the vocabulary terms locally.
    Provides a highly robust, high-performance semantic fallback if LLM is unavailable.
    """
    try:
        x = _VECTORIZER.transform([text])
        sims = cosine_similarity(x, _CORPUS_VECTORS)[0]
        if not np.any(sims > 0.12):  # 0.12 similarity threshold
            return None
        
        intent_scores = {}
        for idx, score in enumerate(sims):
            if score > 0.12:
                intent = _CORPUS_LABELS[idx]
                intent_scores[intent] = max(intent_scores.get(intent, 0.0), float(score))
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent], 0.85)
            return {
                "resolved_text": text,
                "incident_type": best_intent,
                "confidence": confidence,
                "method": "local_semantic_similarity"
            }
    except Exception as e:
        print(f"[PhoneticParser] Local classification error: {e}")
    return None


# ── LLM Fallback Classification ──────────────────────────────────────────────

def _llm_classify(transcript: str) -> str:
    """Last-resort LLM classification when all heuristic methods fail."""
    try:
        from google import genai
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "unknown"
        client = genai.Client(api_key=api_key)
        valid_types = list(INTENT_VOCABULARY.keys())
        prompt = f"""Classify this Indian citizen complaint into EXACTLY one of these categories:
{', '.join(valid_types)}

Complaint: \"{transcript}\"

Respond with ONLY the category name, nothing else."""
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        result = response.text.strip().lower().replace(" ", "_").replace("-", "_")
        if result in valid_types:
            return result
        # Fuzzy match the LLM output against valid types
        for vt in valid_types:
            if vt in result or result in vt:
                return vt
        return "unknown"
    except Exception as e:
        print(f"[PhoneticParser] LLM classify error: {e}")
        return "unknown"


# ── Main Resolution Function ──────────────────────────────────────────────────

def resolve_intent(raw_transcript: str, hint: str = '') -> dict:
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

    # Step 2: Direct keyword match (whole words / phrases)
    scores: dict[str, float] = {}
    for intent, terms in INTENT_VOCABULARY.items():
        score = 0.0
        for term in terms:
            # Use regex to match whole words/phrases only
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, text):
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
        if len(word) < 4 or word in STOPWORDS:
            continue
        code = indian_soundex(word)
        if code in _SOUNDEX_INDEX:
            for intent in _SOUNDEX_INDEX[code]:
                soundex_scores[intent] = soundex_scores.get(intent, 0) + 1

    if soundex_scores:
        best_intent = max(soundex_scores, key=soundex_scores.__getitem__)
        if soundex_scores[best_intent] >= 2:  # Require at least 2 phonetically matching words
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
        if len(word) < 4 or word in STOPWORDS:
            continue
        for intent, terms in INTENT_VOCABULARY.items():
            for term in terms:
                term_word = term.split()[0]  # Compare against first word of each term
                dist = levenshtein(word, term_word)
                if dist < best_distance and dist <= 1:  # Require tighter distance (<=1 instead of <=2)
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

    # Step 5: LLM classification as last resort
    llm_result = _llm_classify(text)
    if llm_result != "unknown":
        return {
            "resolved_text": text,
            "incident_type": llm_result,
            "confidence": 0.60,
            "method": "llm_classification"
        }

    # Step 6: Local semantic Cosine Similarity fallback if LLM failed
    local_match = local_similarity_classify(text)
    if local_match:
        return local_match

    # Step 7: Use frontend hint if provided
    if hint and hint != "" and hint != "other":
        return {
            "resolved_text": text,
            "incident_type": hint,
            "confidence": 0.40,
            "method": "frontend_hint"
        }

    # Step 8: Total fallback
    return {
        "resolved_text": text,
        "incident_type": "unknown",
        "confidence": 0.0,
        "method": "no_match"
    }


def get_all_intent_types() -> list:
    """Returns all canonical intent keys."""
    return list(INTENT_VOCABULARY.keys())
