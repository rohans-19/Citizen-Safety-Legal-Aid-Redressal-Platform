"""
inject_demo_spike.py
Member C — CIVIC-SHIELD Analytics
Injects a rapid spike of 15 caste_discrimination incidents into Bidar district
within seconds to trigger a live anomaly spike on the NGO dashboard during the demo.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
import random

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

raw_url = os.getenv("SUPABASE_URL", "")
SUPABASE_URL = raw_url.strip('"').strip("'").replace("/rest/v1/", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip('"').strip("'")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BIDAR_TALUKS = ["Bidar", "Humnabad", "Bhalki", "Basavakalyan", "Aurad"]


def inject_spike(count: int = 15):
    records = []
    now = datetime.now(timezone.utc)
    for i in range(count):
        # Spread over the last 2 hours so the LSTM temporal window captures them
        ts = now - timedelta(minutes=random.randint(0, 120))
        records.append({
            "incident_type": "caste_discrimination",
            "district":      "Bidar",
            "taluk":         random.choice(BIDAR_TALUKS),
            "created_at":    ts.isoformat(),
            "severity":      round(random.uniform(0.7, 1.0), 2),
            "law_matched":   "SC/ST Act Section 3(1)(v)",
            "pseudonym":     f"CITIZEN-{random.randint(1000, 9999)}",
        })

    supabase.table("civic_incidents").insert(records).execute()
    print(f"[SPIKE] Injected {count} spike incidents into Bidar district.")
    print("   Dashboard should update within 30-60 seconds and show Bidar as HIGH RISK (red).")


if __name__ == "__main__":
    inject_spike(15)
