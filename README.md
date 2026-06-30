# CIVIC-SHIELD
### Socio-Legal Safety, Grievance & Anomaly Detection System

> Empowering marginalized citizens from fear of retaliation to documented legal action — through a secure, voice-driven platform that exposes systemic discrimination patterns.

**Theme:** AWAAZ | **Sub-Theme:** Anti-discrimination tools (Caste, Gender, Disability)

---

## The Problem
India's grievance infrastructure suffers from 3 structural failures:
1. **Safety Barrier** — A Dalit worker or abuse victim cannot safely open a legal app. Oppressors inspect phones.
2. **Access Barrier** — Government portals are text-heavy, English-first, and require documents marginalized citizens don't have.
3. **Accountability Gap** — Individual complaints are isolated. No system maps whether a specific district is systematically denying rights.

## Our Solution: 3-Stage Lifecycle
`
[STAGE 1: SAFETY]         [STAGE 2: SECURE ACTION]       [STAGE 3: SYSTEMIC INSIGHT]
Decoy UI + AST Alarm  →   Voice → Legal PDF Filing    →   T-GAT Anomaly + DP Heatmap
Protects user before      Bypasses illiteracy,            Exposes structural exclusion
and during reporting.     document gap & forms.           to NGOs and administrators.
`

## 8 Core Innovations
1. Language-Agnostic Acoustic Threat Detector (AST on AudioSet)
2. Semantic Code Word Engine (MiniLM sentence transformers)
3. Dual-Layer Shadow UI + Shake-to-Wipe
4. Phonetic Speech-to-Intent Parser (Indian Soundex + Levenshtein)
5. Deterministic Legal Knowledge Graph Traversal
6. LangGraph Multi-Agent Orchestration Swarm (5 agents)
7. Offline Zero-Knowledge Proofs (Pedersen Commitments)
8. Temporal Graph Attention Network (T-GAT) + Differential Privacy

## Tech Stack
| Layer | Technology |
|:---|:---|
| Frontend | React.js + Vite (Vercel) |
| Backend | FastAPI + Python (Render) |
| Agent Swarm | LangGraph + Gemini 2.0 Flash |
| GNN | PyTorch + PyTorch Geometric |
| Database | Supabase PostgreSQL |
| Dashboard | React + D3.js |

## Repo Structure
`
civic-shield/
├── frontend/     ← React app + NGO dashboard (deploys to Vercel)
└── backend/      ← FastAPI + Analytics engine (deploys to Render)
`

## Prototype-Ready User Flow
1. Citizen opens the decoy recipe app.
2. A 3-finger hold unlocks secure mode; shake exits and clears session state.
3. The report screen automatically asks the browser for GPS permission, resolves the nearest Karnataka district on-device, and sends only the district name to the backend.
4. The citizen records or types the statement. The backend predicts the incident type from the case facts using the phonetic parser and legal graph.
5. The confirmation screen shows the predicted type, district, legal provision, authority, evidence checklist, and generated complaint PDF. If prediction is wrong, the user can correct it and regenerate.
6. NGOs can open `/dashboard` to view district-level anomaly scores and differential-privacy protected counts.

## Real-World Guardrails
- Emergency-first UX: immediate danger is routed to India's `112` emergency response number before complaint filing.
- Privacy by design: no raw coordinates are sent to third-party geocoding/IP services; only district-level metadata is logged for analytics.
- Offline resilience: Gemini/Groq/LangGraph/Supabase failures degrade to deterministic local fallbacks so a demo or field pilot does not collapse.
- Honest demo mode: frontend mock responses are enabled only in local development or when `VITE_ENABLE_MOCKS=true`.
- Public PDF safety: generated complaint PDFs are returned in-memory; static PDF serving is disabled unless `ENABLE_PDF_FILE_SERVE=true`.

## Run Locally
Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open the citizen app at `http://localhost:3000` and the NGO dashboard at `http://localhost:3000/dashboard`.

## Verification
```bash
python -m pytest
cd frontend && npm run build
```

## Team
- Member A — Frontend & Client Safety
- Member B — Backend & Agent Swarm
- Member C — Analytics & Dashboard
