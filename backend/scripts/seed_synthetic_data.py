"""
seed_synthetic_data.py
Member C — CIVIC-SHIELD Analytics
Seeds Supabase civic_incidents table with 200+ realistic synthetic incidents
spread across Karnataka's 31 districts over the past 30 days.
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from supabase import create_client

# ── Load env ───────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

raw_url = os.getenv("SUPABASE_URL", "")
# Strip quotes and trailing REST path — we need the base project URL
SUPABASE_URL = raw_url.strip('"').strip("'").replace("/rest/v1/", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip('"').strip("'")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── District baseline weights (higher = more incidents historically) ─────────
DISTRICTS = {
    "Bagalkote":        0.4,
    "Ballari":          0.6,
    "Belagavi":         0.5,
    "Bengaluru Rural":  0.3,
    "Bengaluru Urban":  0.7,
    "Bidar":            0.8,   # historically high — will become anomaly
    "Chamarajanagar":   0.6,
    "Chikkaballapura":  0.3,
    "Chikkamagaluru":   0.3,
    "Chitradurga":      0.4,
    "Dakshina Kannada": 0.4,
    "Davanagere":       0.5,
    "Dharwad":          0.5,
    "Gadag":            0.3,
    "Hassan":           0.3,
    "Haveri":           0.4,
    "Kalaburagi":       0.7,
    "Kodagu":           0.2,
    "Kolar":            0.4,
    "Koppal":           0.5,
    "Mandya":           0.4,
    "Mysuru":           0.5,
    "Raichur":          0.7,
    "Ramanagara":       0.3,
    "Shivamogga":       0.4,
    "Tumakuru":         0.4,
    "Udupi":            0.2,
    "Uttara Kannada":   0.3,
    "Vijayapura":       0.5,
    "Yadgir":           0.6,
    "Vijayanagara":     0.5,
}

INCIDENT_TYPES = [
    "caste_discrimination",
    "gender_based_violence",
    "disability_discrimination",
    "wage_theft",
    "land_rights_violation",
    "domestic_violence",
    "public_harassment",
]

LAWS = {
    "caste_discrimination":     "SC/ST Act Section 3(1)(v)",
    "gender_based_violence":    "IPC 354",
    "disability_discrimination":"Rights of Persons with Disabilities Act Section 92",
    "wage_theft":               "Minimum Wages Act Section 22",
    "land_rights_violation":    "SC/ST Act Section 3(2)(v)",
    "domestic_violence":        "PWDV Act Section 3",
    "public_harassment":        "IPC 509",
}

TALUKS = {
    "Bidar":     ["Bidar", "Humnabad", "Bhalki", "Basavakalyan", "Aurad"],
    "Raichur":   ["Raichur", "Manvi", "Sindhanur", "Lingsugur", "Devadurga"],
    "Kalaburagi":["Kalaburagi", "Afzalpur", "Chincholi", "Jewargi", "Yadgir"],
    "Ballari":   ["Ballari", "Sandur", "Hospet", "Hagaribommanahalli", "Siruguppa"],
}


def random_incident(district: str, days_ago_max: int = 30) -> dict:
    incident_type = random.choice(INCIDENT_TYPES)
    days_ago = random.uniform(0, days_ago_max)
    ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
    taluk_list = TALUKS.get(district, [district])
    return {
        "incident_type": incident_type,
        "district":      district,
        "taluk":         random.choice(taluk_list),
        "created_at":    ts.isoformat(),
        "severity":      round(random.uniform(0.3, 1.0), 2),
        "law_matched":   LAWS[incident_type],
        "pseudonym":     f"CITIZEN-{random.randint(1000, 9999)}",
    }


def seed():
    records = []

    # Generate proportional incidents per district (total ≥ 200)
    for district, weight in DISTRICTS.items():
        count = max(3, int(weight * 15))  # min 3, up to 12 per district
        for _ in range(count):
            records.append(random_incident(district))

    random.shuffle(records)

    # Insert in batches of 50
    BATCH = 50
    for i in range(0, len(records), BATCH):
        batch = records[i : i + BATCH]
        supabase.table("civic_incidents").insert(batch).execute()
        print(f"  Inserted batch {i // BATCH + 1}: {len(batch)} records")

    print(f"\nDone! Seeded {len(records)} synthetic incidents across {len(DISTRICTS)} districts.")


if __name__ == "__main__":
    print("Seeding civic_incidents table...")
    seed()
