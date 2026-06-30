# CIVIC-SHIELD: Backend API Documentation

This document describes all API endpoints provided by the CIVIC-SHIELD backend.

**Base URL:** `http://localhost:8000` (Local Development)

---

## 1. System Endpoints

### `GET /health`
Returns the status of the API server.

*   **Response (200 OK):**
    ```json
    {
      "status": "ok",
      "service": "CIVIC-SHIELD Backend v1.0"
    }
    ```

---

## 2. Core Voice Processing Pipeline

### `POST /process-voice`
Main speech-to-intent pipeline. Resolves ASR phonetic errors, triggers the LangGraph agent swarm, matches deterministic laws, builds a PDF complaint, and logs anonymized metadata to Supabase.

*   **Request Body:**
    ```json
    {
      "transcript": "i was insulted because of my casst on the road by the landlord",
      "district": "Belagavi",
      "language": "en",
      "incident_type_hint": ""
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "success": true,
      "corrected_transcript": "i was insulted because of my casst on the road by the landlord",
      "incident_type": "caste_discrimination",
      "law_matched": {
        "node_key": "caste_discrimination",
        "label": "Caste-Based Discrimination / Atrocity",
        "act": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "sections": ["Section 3(1)", "Section 3(2)", "Section 14A"],
        "authority": "District Magistrate / Special Court (SC/ST)",
        "helpline": "14566",
        "relief_types": [
          "FIR Registration",
          "Compensation under Rule 12(4)",
          "Witness Protection"
        ],
        "escalation_path": ["Local Police", "District SP", "State SC/ST Commission", "NHRC"],
        "timeline_days": 7,
        "compensation_max_inr": 825000,
        "matched": true
      },
      "authority": "District Magistrate / Special Court (SC/ST)",
      "district": "Belagavi",
      "pdf_filename": "complaint_caste_discrimination_Belagavi_20260630_205522.pdf",
      "pdf_base64": "JVBERi0x...",
      "routing": "AUTHORITY",
      "pseudonym": "Citizen-1D88",
      "evidence_list": ["Witness contact details", "Photos or videos of incident site"],
      "next_action": "Go to the District Magistrate office with two PDF copies and ID proof.",
      "empathy_message": "We have received your complaint. You are not alone.",
      "severity": 0.82,
      "db_logged": true
    }
    ```

The frontend predicts incident type from the statement by default. `incident_type_hint` is only used when the user corrects the AI-detected category after submission.

---

## 3. Client Safety Endpoints

### `POST /detect-threat`
Accepts binary audio data and classifies threat levels (shouting, aggression, crying) using RMS energy analytics.

*   **Request Headers:** `Content-Type: multipart/form-data`
*   **Request Body:** (Form-data containing audio binary file)
*   **Response (200 OK):**
    ```json
    {
      "label": "shouting",
      "probability": 0.78,
      "is_threat": true,
      "action": "ALERT_SENT",
      "rms_db": -12.4,
      "duration_sec": 5.2,
      "model": "energy_heuristic_v1"
    }
    ```

---

## 4. Privacy & ZKP Verification

### `POST /verify-zkp`
Verifies a Pedersen commitment wallet proof offline without revealing any user PII.

*   **Request Body:**
    ```json
    {
      "commitment": "0x5f9a...",
      "proof": {
        "value_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
        "blinding_hash": "82e3d9370b43e88705030e26e83b2ac5b9e29e1b161e5c1fa7425e7304336287f3"
      }
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "verified": true
    }
    ```

---

## 5. Direct Legal Knowledge Graph Queries

### `GET /legal-graph/{incident_type}`
Determines legal acts, sections, relief types, and escalation paths for a specific incident type.

*   **Response (200 OK):**
    ```json
    {
      "node_key": "domestic_violence",
      "label": "Domestic Violence",
      "act": "Protection of Women from Domestic Violence Act, 2005",
      "sections": ["Section 12", "Section 18", "Section 19"],
      "authority": "Protection Officer / Magistrate",
      "helpline": "181",
      "relief_types": ["Protection Order", "Residence Order", "Monetary Relief"],
      "escalation_path": ["Protection Officer", "DLSA", "Family Court"],
      "timeline_days": 3,
      "compensation_max_inr": 500000,
      "matched": true
    }
    ```

---

## 6. Analytics Dashboard

### `GET /anomaly-scores`
Returns district-level anomaly scores and differential-privacy protected incident counts for the NGO dashboard at `/dashboard`.

*   **Response (200 OK):**
    ```json
    {
      "Bidar": {
        "count": 18.4,
        "anomaly_score": 0.86,
        "tier": "HIGH"
      },
      "Raichur": {
        "count": 14.2,
        "anomaly_score": 0.79,
        "tier": "HIGH"
      }
    }
    ```

If Supabase/model dependencies are unavailable, the endpoint returns a deterministic demo fallback with `_meta.mode = "demo_fallback"` instead of breaking the dashboard.
