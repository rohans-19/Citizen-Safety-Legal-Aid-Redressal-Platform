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
All agents use Gemini 2.0 Flash for speed.
"""
import os
import uuid
from pathlib import Path
from typing import TypedDict, Annotated
from dotenv import load_dotenv

# Explicit path so it works regardless of working directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

try:
    from google import genai
except Exception:  # google-genai is optional; local fallbacks keep the API usable.
    genai = None

try:
    from langgraph.graph import StateGraph, END
except Exception:  # LangGraph is optional in offline judging environments.
    StateGraph = None
    END = "__end__"

# ── Gemini Setup (lazy — initialized on first call) ───────────────────────────
_GENAI_CLIENT = None
_MODEL_NAME = "gemini-2.0-flash"

def _get_genai_client():
    global _GENAI_CLIENT
    if _GENAI_CLIENT is None:
        if genai is None:
            raise ValueError("google-genai package not installed")
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
    "mr": "Marathi",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "bn": "Bengali",
    "or": "Odia"
}

# ── Robust Local Fallbacks when Gemini is rate-limited (429) ─────────────────
FALLBACK_EVIDENCE_MAP = {
    "en": {
        "caste_discrimination": [
            "Audio/video recordings of casteist slurs or abuse.",
            "Witness statements from bystanders or co-workers.",
            "Copy of formal written complaints sent to police.",
            "Photos/video showing physical exclusion or bar from public spaces.",
            "Identity details or names of the accused persons."
        ],
        "domestic_violence": [
            "Medical reports or photos of injuries/bruises.",
            "Police diary entry (GD) or CSR copy if filed.",
            "Audio/video recordings of threats or physical abuse.",
            "WhatsApp chats, SMS, or call logs showing harassment.",
            "Statements or contacts of neighbors/witnesses."
        ],
        "sexual_harassment_workplace": [
            "WhatsApp chats, emails, or messages showing harassment.",
            "Audio/video recording of inappropriate comments or demands.",
            "Notes detailing date, time, and specific actions of the accused.",
            "Statements or contacts of colleagues/witnesses.",
            "Copy of complaints sent to the Internal Complaints Committee (ICC)."
        ],
        "wage_theft": [
            "Bank statements showing unpaid salary or partial payment.",
            "Attendance register photos, log sheets, or muster rolls.",
            "Appointment letter, ID card, or employment contract.",
            "Text messages or WhatsApp chats discussing salary payment.",
            "Statements of other workers who did not get paid."
        ],
        "mnrega_denial": [
            "Job card copy showing registered details and dates.",
            "Copy of work demand receipt (Form 6) signed by Panchayat.",
            "Photos of the work site or muster roll.",
            "Written application submitted to the Panchayat Development Officer (PDO).",
            "Bank account statement showing MNREGA wage transaction history."
        ],
        "disability_discrimination": [
            "UDID card (disability certificate) copy.",
            "Photos/video of inaccessible infrastructure (lack of ramps, elevators).",
            "Written copy of request submitted to the institution/authority.",
            "Witness contacts of persons present during denial.",
            "Copy of rejection letters or formal communication from officers."
        ],
        "pension_denial": [
            "Pension registration number or acknowledgement slip.",
            "Bank passbook copy showing past transactions or stoppage.",
            "Copy of age proof, widow certificate, or disability certificate.",
            "Written application submitted to the Revenue inspector/Tahsildar.",
            "Rejection slip or reason statement issued by the department."
        ],
        "ration_denial": [
            "Ration card copy (BPL/AAY card).",
            "Video or photos of the ration shop being closed during hours.",
            "Receipt of payment or e-POS transaction logs.",
            "Written complaint submitted to the Food Inspector.",
            "Witness statements of other cardholders denied ration."
        ],
        "healthcare_denial": [
            "Ayushman Bharat (PM-JAY) card or state health card.",
            "Referral letter or emergency admission slip from doctor.",
            "Rejection slip or written refusal from hospital staff.",
            "Medical prescriptions, billing estimates, or receipt copies.",
            "Audio/video of staff refusing cashless admission."
        ],
        "child_labour": [
            "Photos/videos of children working in commercial establishments.",
            "Address and name of the factory, hotel, or dhaba.",
            "Names or contacts of local witnesses or customers.",
            "School dropout certificate or age proof if available.",
            "Details of the owner/employer."
        ],
        "bonded_labour": [
            "Agreement papers, ledger entries, or debt records.",
            "Written statement detailing confinement or lack of freedom.",
            "Audio/video showing force or confinement.",
            "Witness statements of family members or other workers.",
            "Names of the landlords/employers holding the citizen."
        ],
        "land_encroachment": [
            "RTC (Pahani), Mutation register copy, or Sale deed.",
            "Survey map or boundary demarcation documents.",
            "Photos/videos showing the encroachment or eviction.",
            "Police complaint copy or injunction order from civil court.",
            "Forest Rights Act (FRA) patta copy."
        ],
        "default": [
            "Photos or videos of the incident site.",
            "Detailed written timeline of events.",
            "Names and contact details of witnesses.",
            "Copy of any communications with the opposing party.",
            "Receipts, bank statements, or proof of loss."
        ]
    },
    "kn": {
        "caste_discrimination": [
            "ಜಾತಿ ನಿಂದನೆಯ ಆಡಿಯೋ ಅಥವಾ ವಿಡಿಯೋ ರೆಕಾರ್ಡಿಂಗ್.",
            "ಸಾಕ್ಷಿಗಳ ಹೇಳಿಕೆಗಳು ಅಥವಾ ಮೊಬೈಲ್ ನಂಬರ್ಗಳು.",
            "ಪೊಲೀಸ್ ಠಾಣೆಗೆ ನೀಡಿದ ದೂರಿನ ಸ್ವೀಕೃತಿ ಪತ್ರ.",
            "ಸಾರ್ವಜನಿಕ ಪ್ರವೇಶ ನಿರಾಕರಣೆಯ ಫೋಟೋ ಅಥವಾ ವಿಡಿಯೋ.",
            "ಆರೋಪಿಗಳ ಹೆಸರು ಮತ್ತು ವಿಳಾಸದ ಮಾಹಿತಿ."
        ],
        "domestic_violence": [
            "ದೈಹಿಕ ಗಾಯಗಳ ಫೋಟೋಗಳು ಅಥವಾ ವಿಡಿಯೋಗಳು.",
            "ಆಸ್ಪತ್ರೆಯ ವೈದ್ಯಕೀಯ ಚಿಕಿತ್ಸೆ ವರದಿಗಳು.",
            "ಹಿಂಸೆ ಅಥವಾ ಬೆದರಿಕೆಯ ಆಡಿಯೋ ರೆಕಾರ್ಡಿಂಗ್.",
            "ವಾಟ್ಸಾಪ್ ಚಾಟ್ಸ್ ಅಥವಾ ಬೆದರಿಕೆ ಸಂದೇಶಗಳು.",
            "ನೆರೆಹೊರೆಯವರ ಸಾಕ್ಷ್ಯ ಹೇಳಿಕೆಗಳು."
        ],
        "sexual_harassment_workplace": [
            "ವಾಟ್ಸಾಪ್ ಚಾಟ್‌ಗಳು ಅಥವಾ ಸಂದೇಶಗಳ ದಾಖಲೆ.",
            "ಕಿರುಕುಳದ ಆಡಿಯೋ ಅಥವಾ ವಿಡಿಯೋ ರೆಕಾರ್ಡಿಂಗ್.",
            "ದಿನಾಂಕ ಮತ್ತು ಸಮಯದ ವಿವರವಾದ ಟಿಪ್ಪಣಿಗಳು.",
            "ಸಹೋದ್ಯೋಗಿಗಳ ಸಾಕ್ಷ್ಯ ಹೇಳಿಕೆಗಳು.",
            "ಆಂತರಿಕ ದೂರು ಸಮಿತಿ (ICC) ಗೆ ಸಲ್ಲಿಸಿದ ದೂರಿನ ಪ್ರತಿ."
        ],
        "wage_theft": [
            "ಸಂಬಳ ಪಾವತಿಯಾಗದ ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು.",
            "ಕೆಲಸ ಮಾಡಿದ ದಿನಗಳ ಹಾಜರಾತಿ ಪುಸ್ತಕದ ಫೋಟೋ.",
            "ಉದ್ಯೋಗ ಗುರುತಿನ ಚೀಟಿ ಅಥವಾ ನೇಮಕಾತಿ ಪತ್ರ.",
            "ಮಾಲೀಕರೊಂದಿಗೆ ಸಂಬಳ ಕೇಳಿದ ಚಾಟ್ ಅಥವಾ ಸಂದೇಶಗಳು.",
            "ಇತರ ಸಹ-ಕೆಲಸಗಾರರ ಸಾಕ್ಷ್ಯ ಹೇಳಿಕೆಗಳು."
        ],
        "mnrega_denial": [
            "ಉದ್ಯೋಗ ಖಾತರಿ ಜಾಬ್ ಕಾರ್ಡ್ ನ ಪ್ರತಿ.",
            "ಕೆಲಸ ಕೇಳಿದ ಅರ್ಜಿ ರಸೀದಿ (ನಮೂನೆ 6 ಪ್ರತಿ).",
            "ಕೆಲಸದ ಸ್ಥಳದ ಫೋಟೋ ಅಥವಾ ಮಾಸ್ಟರ್ ರೋಲ್ ವಿವರ.",
            "ಪಂಚಾಯತ್ ಅಭಿವೃದ್ಧಿ ಅಧಿಕಾರಿಗೆ (PDO) ನೀಡಿದ ಲಿಖಿತ ಅರ್ಜಿ.",
            "ಉದ್ಯೋಗ ಖಾತರಿ ವೇತನದ ಬ್ಯಾಂಕ್ ಖಾತೆ ಮಾಹಿತಿ."
        ],
        "disability_discrimination": [
            "ಅಂಗವಿಕಲತೆಯ ಗುರುತಿನ ಚೀಟಿ (UDID ಕಾರ್ಡ್).",
            "ರ್ಯಾಂಪ್ ಅಥವಾ ಲಿಫ್ಟ್ ಇಲ್ಲದಿರುವ ಸ್ಥಳದ ಫೋಟೋ.",
            "ಅನುಮತಿ ಅಥವಾ ಪ್ರವೇಶ ನಿರಾಕರಣೆಯ ಲಿಖಿತ ಮಾಹಿತಿ.",
            "ಘಟನೆಯನ್ನು ನೋಡಿದ ಸಾಕ್ಷಿಗಳ ವಿವರಗಳು.",
            "ಅಧಿಕಾರಿಗಳು ನೀಡಿದ ತಿರಸ್ಕಾರ ಪತ್ರದ ಪ್ರತಿ."
        ],
        "pension_denial": [
            "ಪಿಂಚಣಿ ನೋಂದಣಿ ಸಂಖ್ಯೆ ಅಥವಾ ಅರ್ಜಿ ರಸೀದಿ.",
            "ಪಿಂಚಣಿ ನಿಂತುಹೋಗಿರುವುದನ್ನು ತೋರಿಸುವ ಬ್ಯಾಂಕ್ ಪಾಸ್ಬುಕ್ ಪ್ರತಿ.",
            "ವಯಸ್ಸಿನ ಪುರಾವೆ ಅಥವಾ ವಿಧವಾ ಪ್ರಮಾಣಪತ್ರದ ಪ್ರತಿ.",
            "ತಹಶೀಲ್ದಾರರಿಗೆ ಸಲ್ಲಿಸಿದ ಲಿಖಿತ ಅರ್ಜಿಯ ಸ್ವೀಕೃತಿ.",
            "ಇಲಾಖೆಯಿಂದ ನೀಡಿದ ನಿರಾಕರಣೆ ಪತ್ರ."
        ],
        "ration_denial": [
            "ಪಡಿತರ ಚೀಟಿ (ರೇಷನ್ ಕಾರ್ಡ್) ಪ್ರತಿ.",
            "ರೇಷನ್ ಅಂಗಡಿ ಮುಚ್ಚಿರುವ ಫೋಟೋ ಅಥವಾ ವಿಡಿಯೋ.",
            "ಬೆರಳು ಮುದ್ರೆ ಯಂತ್ರದ ದೋಷ ಅಥವಾ ತೂಕದ ರಸೀದಿಗಳು.",
            "ಆಹಾರ ನಿರೀಕ್ಷಕರಿಗೆ ಬರೆದ ಲಿಖಿತ ದೂರು ಪ್ರತಿ.",
            "ಪಡಿತರ ಸಿಗದ ಇತರ ಕಾರ್ಡುದಾರರ ಹೇಳಿಕೆಗಳು."
        ],
        "healthcare_denial": [
            "ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಅಥವಾ ರಾಜ್ಯ ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಪ್ರತಿ.",
            "ತುರ್ತು ದಾಖಲಾತಿ ಅಥವಾ ವೈದ್ಯರ ಶಿಫಾರಸು ಪತ್ರ.",
            "ಆಸ್ಪತ್ರೆ ಸಿಬ್ಬಂದಿ ಚಿಕಿತ್ಸೆ ನಿರಾಕರಿಸಿದ ಲಿಖಿತ ದಾಖಲೆ.",
            "ವೈದ್ಯಕೀಯ ಬಿಲ್ ವಿವರಗಳು ಅಥವಾ ರಸೀದಿಗಳು.",
            "ಚಿಕಿತ್ಸೆ ನಿರಾಕರಿಸಿದ ಆಡಿಯೋ/ವಿಡಿಯೋ ಪುರಾವೆ."
        ],
        "child_labour": [
            "ಮಕ್ಕಳು ಕೆಲಸ ಮಾಡುತ್ತಿರುವ ಸ್ಥಳದ ಫೋಟೋಗಳು.",
            "ಹೋಟೆಲ್ ಅಥವಾ ಅಂಗಡಿಯ ಹೆಸರು ಮತ್ತು ವಿಳಾಸ.",
            "ಘಟನೆಗೆ ಸಾಕ್ಷಿಯಾದ ಸ್ಥಳೀಯರ ವಿವರಗಳು.",
            "ಮಗುವಿನ ವಯಸ್ಸಿನ ಪುರಾವೆ ಅಥವಾ ಶಾಲಾ ದಾಖಲೆ.",
            "ಮಾಲೀಕ ಅಥವಾ ಉದ್ಯೋಗದಾತನ ವಿವರಗಳು."
        ],
        "bonded_labour": [
            "ಸಾಲದ ಒಪ್ಪಂದ ಅಥವಾ ಕಾಗದದ ದಾಖಲೆಗಳು.",
            "ಬಂಧನದಲ್ಲಿಟ್ಟಿರುವ ಸ್ಥಳದ ವಿವರಣೆ ಅಥವಾ ಹೇಳಿಕೆ.",
            "ದೈಹಿಕ ಬಲವಂತದ ಆಡಿಯೋ ಅಥವಾ ವಿಡಿಯೋ ಪುರಾವೆ.",
            "ಕುಟುಂಬದ ಸದಸ್ಯರ ಸಾಕ್ಷ್ಯ ಹೇಳಿಕೆಗಳು.",
            "ಬಂಧನದಲ್ಲಿಟ್ಟಿರುವ ಮಾಲೀಕರ ಹೆಸರು ಮತ್ತು ವಿಳಾಸ."
        ],
        "land_encroachment": [
            "ಆರ್‌ಟಿಸಿ (ಪಹಣಿ), ಭೂಮಿ ಖರೀದಿ ಪತ್ರದ ಪ್ರತಿ.",
            "ಸರ್ವೆ ನಕ್ಷೆ ಅಥವಾ ಹದ್ದುಬಸ್ತು ದಾಖಲೆಗಳು.",
            "ಭೂಮಿ ಒತ್ತುವರಿಯ ಫೋಟೋ ಅಥವಾ ವಿಡಿಯೋಗಳು.",
            "ಪೊಲೀಸ್ ದೂರು ಅಥವಾ ನ್ಯಾಯಾಲಯದ ತಡೆಯಾಜ್ಞೆ ಪ್ರತಿ.",
            "ಅರಣ್ಯ ಹಕ್ಕು ಕಾಯ್ದೆಯಡಿ ಪಡೆದ ಪಟ್ಟಾದ ಪ್ರತಿ."
        ],
        "default": [
            "ಘಟನಾ ಸ್ಥಳದ ಫೋಟೋಗಳು ಅಥವಾ ವಿಡಿಯೋಗಳು.",
            "ವಿವರವಾದ ಲಿಖಿತ ಘಟನಾ ಸರಪಳಿ.",
            "ಘಟನೆಯನ್ನು ನೋಡಿದ ಸಾಕ್ಷಿಗಳ ವಿವರಗಳು.",
            "ಎದುರಾಳಿಗಳೊಂದಿಗೆ ನಡೆಸಿದ ಸಂವಹನದ ದಾಖಲೆಗಳು.",
            "ಖರ್ಚುಗಳು ಅಥವಾ ನಷ್ಟದ ರಸೀದಿಗಳು."
        ]
    },
    "hi": {
        "caste_discrimination": [
            "जातिसूचक गाली-गलौज का ऑडियो या वीडियो रिकॉर्डिंग।",
            "गवाहों के बयान या उनके मोबाइल नंबर।",
            "थाने में दी गई शिकायत की पावती प्रति।",
            "सार्वजनिक स्थल पर प्रवेश रोकने का फोटो या वीडियो।",
            "आरोपियों के नाम और पते की जानकारी।"
        ],
        "domestic_violence": [
            "शारीरिक चोटों के फोटो या वीडियो।",
            "अस्पताल की मेडिकल पर्ची या इलाज की रिपोर्ट।",
            "मारपीट या धमकी की ऑडियो रिकॉर्डिंग।",
            "व्हाट्सएप चैट या धमकी भरे मैसेज।",
            "पड़ोसियों या रिश्तेदारों के गवाही बयान।"
        ],
        "sexual_harassment_workplace": [
            "व्हाट्सएप चैट या धमकी भरे संदेशों का स्क्रीनशॉट।",
            "उत्पीड़न की ऑडियो या वीडियो रिकॉर्डिंग।",
            "घटना की तिथि, समय और विवरण की डायरी।",
            "साथी कर्मचारियों के गवाही बयान।",
            "आंतरिक शिकायत समिति (ICC) को भेजी गई शिकायत की कॉपी।"
        ],
        "wage_theft": [
            "बैंक पासबुक या खाते का विवरण (सैलरी न मिलने का सबूत)।",
            "काम करने के दिनों का हाजिरी रजिस्टर या मस्टर रोल।",
            "नौकरी का आईडी कार्ड या नियुक्ति पत्र।",
            "मालिक से सैलरी मांगने के मैसेज या कॉल रिकॉर्डिंग।",
            "साथ काम करने वाले मजदूरों के बयान।"
        ],
        "mnrega_denial": [
            "मनरेगा जॉब कार्ड की फोटोकॉपी।",
            "काम मांगने की रसीद (फॉर्म ६ की प्रति)।",
            "कार्यस्थल की फोटो या मस्टर रोल का विवरण।",
            "पंचायत विकास अधिकारी (PDO) को दिया गया प्रार्थना पत्र।",
            "मनरेगा मजदूरी के बैंक खाते का विवरण।"
        ],
        "disability_discrimination": [
            "दिव्यांगता प्रमाण पत्र (UDID कार्ड) की प्रति।",
            "रैंप या लिफ्ट न होने वाले स्थान का फोटो।",
            "संस्थान द्वारा प्रवेश से इनकार का लिखित विवरण।",
            "घटना के गवाहों के संपर्क विवरण।",
            "अधिकारियों द्वारा जारी अस्वीकृति पत्र।"
        ],
        "pension_denial": [
            "पेंशन पंजीकरण संख्या या आवेदन की रसीद।",
            "पेंशन रुकने का विवरण दिखाने वाली बैंक पासबुक।",
            "आयु प्रमाण पत्र या विधवा प्रमाण पत्र की प्रति।",
            "तहसीलदार को दिए गए आवेदन की पावती।",
            "विभाग द्वारा जारी अस्वीकृति आदेश।"
        ],
        "ration_denial": [
            "राशन कार्ड की फोटोकॉपी (BPL/AAY)।",
            "राशन दुकान बंद होने या अनाज न होने का वीडियो।",
            "अंगूठे की मशीन (e-POS) की रसीद या एरर स्क्रीन।",
            "खाद्य निरीक्षक (Food Inspector) को दी गई लिखित शिकायत।",
            "अन्य लाभार्थियों के गवाही बयान।"
        ],
        "healthcare_denial": [
            "आयुष्मान कार्ड या राज्य स्वास्थ्य योजना कार्ड की प्रति।",
            "आपातकालीन पर्ची या डॉक्टर का रेफरल लेटर।",
            "अस्पताल द्वारा इलाज से मना करने का लिखित प्रमाण।",
            "दवाइयों या इलाज के खर्च की रसीदें।",
            "इलाज न करने वाले स्टाफ की वीडियो या ऑडियो रिकॉर्डिंग।"
        ],
        "child_labour": [
            "बच्चों से काम कराए जाने का फोटो या वीडियो।",
            "प्रतिष्ठान (होटल/दुकान) का नाम और पूरा पता।",
            "वहां मौजूद ग्राहकों या गवाहों के मोबाइल नंबर।",
            "बच्चे के स्कूल छोड़ने का प्रमाण पत्र।",
            "मालिक या ठेकेदार का नाम और विवरण।"
        ],
        "bonded_labour": [
            "ऋण या एग्रीमेंट से जुड़े कागजात।",
            "बंधक बनाकर रखे जाने के स्थान का फोटो/विवरण।",
            "जबरन काम कराने का वीडियो या ऑडियो साक्ष्य।",
            "परिवार के सदस्यों के गवाही बयान।",
            "बंधक बनाने वाले मालिक का नाम और विवरण।"
        ],
        "land_encroachment": [
            "खसरा-खतौनी या भूमि की रजिस्ट्री के कागजात।",
            "सीमांकन (जमीन की नपाई) का नक्शा या रिपोर्ट।",
            "जमीन पर अवैध कब्जे का फोटो या वीडियो।",
            "पुलिस शिकायत या न्यायालय का स्थगन आदेश (Stay Order)।",
            "वन अधिकार कानून के तहत जारी पट्टे की प्रति।"
        ],
        "default": [
            "घटनास्थल के फोटो या वीडियो।",
            "घटना का लिखित विवरण (तारीख और समय के साथ)।",
            "घटना के गवाहों के नाम और संपर्क।",
            "विपक्षी पक्ष के साथ हुई बातचीत के संदेश।",
            "खर्चों या नुकसान के बिल और रसीदें।"
        ]
    }
}

FALLBACK_EMPATHY = {
    "kn": "ನಿಮ್ಮ ದೂರನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ನಾವು ನಿಮ್ಮೊಂದಿಗೆ ಇದ್ದೇವೆ ಮತ್ತು ಶೀಘ್ರದಲ್ಲೇ ಪರಿಹಾರ ಸಿಗಲಿದೆ. ಕಾನೂನು ಸಹಾಯ ಕೇಂದ್ರವು ನಿಮ್ಮ ಪ್ರಕರಣವನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ.",
    "hi": "आपकी शिकायत सफलतापूर्वक दर्ज कर ली गई है। हम हर कदम पर आपके साथ हैं और जल्द ही आपको सहायता मिलेगी।",
    "ta": "உங்கள் புகார் வெற்றிகரமாக பதிவு செய்யப்பட்டுள்ளது. நாங்கள் உங்களுடன் இருக்கிறோம், விரைவில் தீர்வு கிடைக்கும்.",
    "te": "మీ ఫిర్యాదు విజయవంతంగా నమోదు చేయబడింది. మేము మీకు తోడుగా ఉంటాము మరియు త్వరలోనే సహాయం అందుతుంది.",
    "mr": "तुमची तक्रार यशस्वीरित्या नोंदवली गेली आहे. आम्ही तुमच्या पाठीशी आहोत आणि लवकरच मदत मिळेल.",
    "en": "We have received your complaint. You are not alone — help is on the way. The legal aid office will review your case shortly."
}

# ── Swarm State ───────────────────────────────────────────────────────────────

class SwarmState(TypedDict):
    # Inputs
    transcript: str
    incident_type: str
    district: str
    language: str
    legal_match: dict

    # Populated by agents
    severity: float
    routing: str
    narrative: str
    evidence_list: list
    next_action: str
    empathy_message: str
    pseudonym: str


def _call_gemini(prompt: str, fallback: str = "") -> str:
    # 1. Try Groq if GROQ_API_KEY is configured
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            response = httpx.post("https://api.groq.com/openai/v1/chat/completions", json=body, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                print(f"[Groq] API returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Groq] Error calling completion: {e}")

    # 2. Fallback to Gemini
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
    legal_details = ""
    lm = state.get("legal_match", {})
    if lm and lm.get("matched"):
        legal_details = f"\nUse this matching legal provision to ground your narrative:\nAct/Scheme: {lm.get('act', '')}\nSections: {', '.join(lm.get('sections', []))}"

    prompt = f"""You are a legal aid paralegal in India helping a marginalized citizen.

Convert the following voice transcript into a formal, legally-phrased complaint narrative 
suitable for submission to Indian courts/authorities.{legal_details}
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
    lm = state.get("legal_match", {})
    legal_context = ""
    if lm and lm.get("matched"):
        legal_context = f"\nMatched Law/Act: {lm.get('act', '')} (Sections: {', '.join(lm.get('sections', []))})"

    lang = state.get("language", "kn")
    lang_name = LANGUAGE_NAMES.get(lang, "English")

    prompt = f"""You are a legal aid expert helping an Indian citizen with:
Incident: {state['incident_type']}{legal_context}

List exactly 5 specific pieces of evidence they should collect to prove this specific legal violation under the matched sections.
Each item must be practical and collectible by a marginalized citizen with a smartphone (e.g. photos, witness contacts, audio recordings, job cards).
Format: numbered list, one per line, brief (under 10 words each).

You MUST write the response in {lang_name} using the native {lang_name} script (not transliterated).

Evidence list:"""

    # Fetch custom fallback list based on language and incident type
    incident = state['incident_type']
    lang_map = FALLBACK_EVIDENCE_MAP.get(lang, FALLBACK_EVIDENCE_MAP["en"])
    fb_list = lang_map.get(incident, lang_map["default"])
    fb_string = "\n".join(f"{i+1}. {item}" for i, item in enumerate(fb_list))

    raw = _call_gemini(prompt, fb_string)
    
    evidence_list = [
        line.strip().lstrip("0123456789.-) ")
        for line in raw.split("\n")
        if line.strip() and len(line.strip()) > 2  # Reduced to >2 for shorter native words
    ][:5]

    if not evidence_list:
        evidence_list = fb_list

    return {**state, "evidence_list": evidence_list}


# ── Agent 4: Routing ──────────────────────────────────────────────────────────

def routing_agent(state: SwarmState) -> SwarmState:
    """
    Determines the specific next action — which office to go to, what to say.
    Tailored to the district and incident type.
    """
    lm = state.get("legal_match", {})
    authority = "District Collector"
    escalation = ""
    if lm and lm.get("matched"):
        authority = lm.get("authority", "District Collector")
        if lm.get("escalation_path"):
            escalation = f" (Escalation Path: {' -> '.join(lm.get('escalation_path', []))})"

    lang = state.get("language", "kn")
    lang_name = LANGUAGE_NAMES.get(lang, "English")

    prompt = f"""You are a legal aid navigator for India.

Incident Type: {state['incident_type']}
District: {state['district']}
Severity: {state['severity']}
Primary Legal Authority: {authority}{escalation}

Give ONE specific, practical next action the complainant must take tomorrow morning.
Instruct them to submit their complaint to the Primary Legal Authority.
Include: where to go, what to bring, what to say.
Maximum 3 sentences. Simple language.

You MUST write the response in {lang_name} using the native {lang_name} script (not transliterated).

Next Action:"""

    if lang == "kn":
        fb_routing = f"ನಾಳೆ ಬೆಳಿಗ್ಗೆ {state['district']} ಜಿಲ್ಲೆಯ {authority} ಕಚೇರಿಗೆ ಭೇಟಿ ನೀಡಿ. ನಿಮ್ಮ ದೂರಿನ ಪಿಡಿಎಫ್‌ನ ಎರಡು ಪ್ರತಿಗಳು ಮತ್ತು ಗುರುತಿನ ಚೀಟಿಯನ್ನು ತೆಗೆದುಕೊಂಡು ಹೋಗಿ. ಕಚೇರಿಯ ಅಧಿಕಾರಿಗೆ ದೂರನ್ನು ಸಲ್ಲಿಸಿ ಸ್ವೀಕೃತಿ ಪತ್ರವನ್ನು ಪಡೆದುಕೊಳ್ಳಿ."
    elif lang == "hi":
        fb_routing = f"कल सुबह {state['district']} जिले के {authority} कार्यालय में जाएं। अपने शिकायत पीडीएफ की दो प्रतियां और एक पहचान पत्र साथ ले जाएं। वहां डेस्क अधिकारी को शिकायत सौंपकर पावती रसीद प्राप्त करें।"
    else:
        fb_routing = f"Go to the office of the {authority} in {state['district']} district tomorrow morning. Carry two printed copies of your complaint PDF along with your ID proof. Ask to submit the complaint to the desk officer and collect a signed acknowledgment receipt."

    next_action = _call_gemini(prompt, fb_routing)
    return {**state, "next_action": next_action}


# ── Agent 5: Empathy ──────────────────────────────────────────────────────────

def empathy_agent(state: SwarmState) -> SwarmState:
    """
    Generates a warm, supportive message in the user's native language.
    Critical for trust-building with traumatized users.
    """
    lang = state.get("language", "kn")
    lang_name = LANGUAGE_NAMES.get(lang, "English")
    
    prompt = f"""You are a compassionate legal aid assistant.

Write a brief, warm, reassuring message in {lang_name} for a citizen who just 
reported a {state['incident_type']} incident. 
Tell them: we heard you, their complaint has been processed, they are not alone, 
and help is on the way.

Write in {lang_name} script (not transliteration). Maximum 3 sentences.

Message:"""

    fb_empathy = FALLBACK_EMPATHY.get(lang, FALLBACK_EMPATHY["en"])
    empathy_message = _call_gemini(prompt, fb_empathy)
    return {**state, "empathy_message": empathy_message}


# ── Build LangGraph ───────────────────────────────────────────────────────────

def _build_graph() -> object:
    if StateGraph is None:
        return None

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


def _run_linear_fallback(state: SwarmState) -> SwarmState:
    """Run the same agent chain without LangGraph when the package is absent."""
    for agent in (triage_agent, narrative_agent, evidence_agent, routing_agent, empathy_agent):
        state = agent(state)
    return state


# ── District Detection & Geocoding ────────────────────────────────────────────

_KARNATAKA_DISTRICTS = [
    'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
    'Bidar', 'Chamarajanagara', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga',
    'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
    'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
    'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
    'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir', 'Vijayanagara'
]

_DISTRICT_ALIASES = {
    'bangalore': 'Bengaluru Urban',
    'bengaluru': 'Bengaluru Urban',
    'belgaum': 'Belagavi',
    'bellary': 'Ballari',
    'gulbarga': 'Kalaburagi',
    'bijapur': 'Vijayapura',
    'chikmagalur': 'Chikkamagaluru',
    'chikkamagalur': 'Chikkamagaluru',
    'mangalore': 'Dakshina Kannada',
    'coorg': 'Kodagu',
    'mysore': 'Mysuru',
    'shimoga': 'Shivamogga',
    'tumkur': 'Tumakuru',
}

def detect_district(transcript: str, current_district: str) -> str:
    if current_district and current_district.lower() != 'unknown' and current_district != '':
        return current_district

    normalized = transcript.lower()
    for alias, canonical in _DISTRICT_ALIASES.items():
        if alias in normalized:
            return canonical

    for d in _KARNATAKA_DISTRICTS:
        if d.lower() in normalized:
            return d

    # Gemini LLM extraction fallback
    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if genai is not None and api_key:
            client = genai.Client(api_key=api_key)
            prompt = f"""Given the following Indian citizen complaint transcript, identify if any location (district, city, town, taluk, or village) in Karnataka is mentioned.
If so, resolve it to EXACTLY one of these 31 districts of Karnataka:
{', '.join(_KARNATAKA_DISTRICTS)}

If no location in Karnataka is mentioned, respond with "Unknown".
Do not write anything else.

Complaint: "{transcript}"
"""
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            res = response.text.strip()
            for d in _KARNATAKA_DISTRICTS:
                if d.lower() in res.lower() or res.lower() in d.lower():
                    return d
    except Exception as e:
        print(f"[Swarm] LLM district extraction error: {e}")

    return "Unknown"


# ── Public API ────────────────────────────────────────────────────────────────

async def run_swarm(
    transcript: str,
    incident_type: str,
    district: str,
    language: str = "kn",
    legal_match: dict = None
) -> dict:
    """
    Runs the full 5-agent LangGraph swarm asynchronously.

    Args:
        transcript: Corrected ASR transcript
        incident_type: Canonical incident key from phonetic_parser
        district: District name (e.g. "Belagavi")
        language: ISO 639-1 language code
        legal_match: Dictionary of RAG matched legal provisions

    Returns:
        dict with severity, routing, narrative, evidence_list, 
        next_action, empathy_message, pseudonym, district
    """
    resolved_district = detect_district(transcript, district)

    initial_state: SwarmState = {
        "transcript": transcript,
        "incident_type": incident_type,
        "district": resolved_district,
        "language": language,
        "severity": 0.5,
        "routing": "AUTHORITY",
        "narrative": "",
        "evidence_list": [],
        "next_action": "",
        "empathy_message": "",
        "pseudonym": "",
        "legal_match": legal_match or {}
    }

    final_state = _SWARM.invoke(initial_state) if _SWARM is not None else _run_linear_fallback(initial_state)
    return {
        "severity": final_state.get("severity", 0.5),
        "routing": final_state.get("routing", "AUTHORITY"),
        "narrative": final_state.get("narrative", ""),
        "evidence_list": final_state.get("evidence_list", []),
        "next_action": final_state.get("next_action", ""),
        "empathy_message": final_state.get("empathy_message", ""),
        "pseudonym": final_state.get("pseudonym", "Citizen-XXXX"),
        "district": final_state.get("district", resolved_district)
    }
