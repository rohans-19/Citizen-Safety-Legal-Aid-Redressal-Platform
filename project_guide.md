# CIVIC-SHIELD — Complete Team Project Guide
### Socio-Legal Safety, Grievance & Anomaly Detection System
**Theme:** AWAAZ | **Sub-Theme:** Anti-discrimination tools (Caste, Gender, Disability)
**Team Size:** 3 Members

---

## PART 1: WHAT IS OUR PROJECT?

### The One-Line Pitch
> "A secure, voice-driven platform that takes a marginalized Indian citizen from fear of retaliation all the way to documented legal action, while simultaneously exposing systemic discrimination patterns to administrators."

### The Real-World Problem We Solve
India's grievance and safety infrastructure suffers from 3 structural failures:
1. **Safety Barrier:** A Dalit worker or a woman in an abusive house cannot safely open a legal app on their phone. Abusers and oppressors inspect phones.
2. **Access Barrier:** Government portals are text-heavy, English-first, and require physical documents that marginalized citizens don't have.
3. **Accountability Gap:** Individual complaints are treated as isolated events. No system maps whether a specific panchayat or district is systematically denying rights, until protests erupt.

### Our Three-Stage Lifecycle (This is the project's entire narrative)

```
[STAGE 1: SAFETY]         [STAGE 2: SECURE ACTION]       [STAGE 3: SYSTEMIC INSIGHT]
Decoy UI + AST Alarm  →   Voice → Legal PDF Filing    →   T-GAT Anomaly + DP Heatmap
Protects user before      Bypasses illiteracy,            Exposes structural exclusion
and during reporting.     documents gap & forms.          to NGOs and administrators.
```

**Why they are NOT disconnected:** Safety is the prerequisite for justice. A citizen must first be safe on their device (Stage 1) before they can even attempt to file (Stage 2). Only then can their anonymized data contribute to collective accountability (Stage 3).

---

## PART 2: THE 8 INNOVATIONS (What We Build)

These 8 innovations span 3 modules. Each is custom-built (not simple API calls):

| # | Innovation | Module | Technical Credibility |
|:--|:---|:---|:---|
| 1 | Language-Agnostic Acoustic Threat Detector (AST on AudioSet) | Client Safety | AudioSet is language-independent; survives ML Q&A |
| 2 | Semantic Code Word Engine (Sentence-Transformers MiniLM) | Client Safety | On-device, multilingual, no internet needed |
| 3 | Dual-Layer Shadow UI & Shake-to-Wipe (React.js + Vite) | Client Safety | Custom gesture + accelerometer engineering |
| 4 | Phonetic Speech-to-Intent Parser (Indian Soundex + Levenshtein) | Backend Core | Corrects ASR errors on regional dialects |
| 5 | Deterministic Legal Knowledge Graph Traversal | Backend Core | Prevents hallucinations; JSON dictionary traversal mapping |
| 6 | LangGraph Multi-Agent Orchestration Swarm | Backend Core | 5-agent state machine (Triage, Narrative, Evidence, Routing, Empathy) |
| 7 | Offline Zero-Knowledge Proofs (Pedersen Commitments via SHA-256) | Backend Core | Proves eligibility without exposing documents |
| 8 | Temporal Graph Attention Network (T-GAT) + Differential Privacy | Analytics | Full GNN; spatiotemporal anomaly detection (GATConv + GRU) |

---

## PART 3: SYSTEM ARCHITECTURE (Full Data Flow)

```
USER INPUT (Voice/Audio)
       │
       ▼
┌──────────────────────────────────────────────┐
│           CLIENT APP (Member A)              │
│  Decoy Recipe Shell (React.js + Vite)        │
│  3-Finger Gesture → Unlock Shadow UI         │
│  ┌─────────────────────────────────┐         │
│  │ AST Scream/Thud Detector        │ ◄─ Mic  │
│  │ Sentence-Transformer Code Word  │ ◄─ ASR  │
│  │ Shake Accelerometer Wipe        │ ◄─ Gyro │
│  └─────────────────────────────────┘         │
│  Voice Note Recorded → Transcribed           │
│  ZKP QR Code Generator                       │
└──────────────────┬───────────────────────────┘
                   │ HTTPS to Backend
                   ▼
┌──────────────────────────────────────────────┐
│         BACKEND SWARM (Member B)             │
│  FastAPI Server (Python)                     │
│  ┌─────────────────────────────────┐         │
│  │ Phonetic Soundex Parser         │         │
│  │ LangGraph State Machine         │         │
│  │  Agent 1: Triage Agent          │         │
│  │  Agent 2: Narrative Agent       │         │
│  │  Agent 3: Evidence Agent        │         │
│  │  Agent 4: Routing Agent         │         │
│  │  Agent 5: Empathy Agent         │         │
│  │ Legal Knowledge Graph (JSON)    │         │
│  └─────────────────────────────────┘         │
│  → PDF Complaint Generated                   │
│  → Routed to NGO/One Stop Centre             │
└──────────────────┬───────────────────────────┘
                   │ Anonymized metadata
                   ▼
┌──────────────────────────────────────────────┐
│       ANALYTICS ENGINE (Member C)            │
│  ┌─────────────────────────────────┐         │
│  │ Differential Privacy Engine     │         │
│  │ (Laplace Noise Injector)        │         │
│  │ T-GAT Anomaly Detector          │         │
│  │ (GATConv + GRU in PyTorch)      │         │
│  │ Supabase DB (District Vectors)  │         │
│  │ React Dashboard (D3.js Map)     │         │
│  └─────────────────────────────────┘         │
│  → NGO Command Center Heatmap                │
└──────────────────────────────────────────────┘
```

---

## PART 4: TEAM DIVISION OF WORK

> **Rule:** Each member owns one complete module end-to-end. Integration happens at two fixed checkpoints.

---

### 👤 MEMBER A — Frontend & Client Safety Engineer

**Your Module:** Client App (React.js + Vite Web App)
**Your Innovations:** #1 (AST Detector), #2 (Code Word Engine), #3 (Shadow UI + ZKP)

**What You Build:**
| File | What It Does |
|:---|:---|
| `app/ShadowWrapper.js` | Decoy recipe UI, 3-finger unlock, shake-to-wipe accelerometer |
| `app/ASTDetector.js` | Calls backend `/detect-threat` endpoint, displays alert state |
| `app/CodeWordEngine.js` | Local sentence-transformer similarity check on transcribed text |
| `app/ZKPWallet.js` | Pedersen commitment generation, QR code output |
| `app/VoiceRecorder.js` | Records audio, sends to backend for processing |
| `app/DecoyApp.js` | Fully working recipe shell (the decoy) |

**Tech Stack You Use:**
- React.js + Vite (Web App)
- Accelerometer API via Window DeviceMotionEvent / standard Web Sensors
- TouchEvents (multi-touch gesture tracking)
- webkitSpeechRecognition API (voice transcription)
- `crypto-js` or browser WebCrypto API (for ZKP)
- `qrcode.react` (QR generation)

**Timeline:**
- **Hour 0-3:** Set up React.js + Vite project. Build the decoy recipe shell UI completely first.
- **Hour 3-8:** Implement the 3-finger gesture unlock and shake-to-wipe.
- **Hour 8-14:** Wire up VoiceRecorder and webkitSpeechRecognition transcription.
- **Hour 14-20:** Implement ZKP wallet and QR code generator.
- **Hour 20-24:** Connect to Member B's backend API endpoints. Test full flow.

**What You Depend On:**
- Member B's `/process-voice` and `/detect-threat` API endpoints (available by Hour 14).

---

### 👤 MEMBER B — Backend & Agent Swarm Engineer

**Your Module:** FastAPI Backend + LangGraph Swarm + Legal Knowledge Graph
**Your Innovations:** #4 (Phonetic Parser), #5 (Legal Graph), #6 (LangGraph Swarm), #7 (ZKP Verification)

**What You Build:**
| File | What It Does |
|:---|:---|
| `server/main.py` | FastAPI app with all endpoint definitions |
| `server/phonetic_parser.py` | Indian Soundex + Levenshtein ASR error correction |
| `server/legal_graph.py` | JSON legal knowledge graph + traversal method |
| `server/agent_swarm.py` | LangGraph StateGraph with 5 agent nodes |
| `server/zkp_verifier.py` | Verifies ZKP Pedersen commitments from client |
| `server/threat_detector.py` | AST model loaded, runs on received audio bytes |
| `server/pdf_builder.py` | Generates formatted legal complaint PDFs |
| `data/legal_knowledge_graph.json` | Full JSON definition of all laws, schemes, edges |

**Tech Stack You Use:**
- Python + FastAPI
- LangGraph + LangChain
- Gemini 2.0 Flash API (Free tier, 1M tokens/day)
- `sentence-transformers` MiniLM
- `transformers` (HuggingFace, for AST model)
- `reportlab` or `fpdf2` (PDF generation)
- JSON dictionary traversal mapping (zero-dependency graph lookup)

**Timeline:**
- **Hour 0-4:** Set up FastAPI server. Define all endpoint signatures first (even empty stubs) so Member A can integrate.
- **Hour 4-8:** Build the Legal Knowledge Graph JSON fully. Write traversal function.
- **Hour 8-14:** Build LangGraph swarm (all 5 agents wired together: Triage, Narrative, Evidence, Routing, Empathy).
- **Hour 14-18:** Integrate phonetic parser into the swarm pipeline.
- **Hour 18-22:** Load AST threat detector, wire PDF builder, test end-to-end.
- **Hour 22-24:** Integration testing with Member A's frontend.

**What You Depend On:**
- Member C's Supabase DB schema (table structure for storing anonymized incident metadata) — needed by Hour 8.
- Gemini API key.

---

### 👤 MEMBER C — Analytics & Dashboard Engineer

**Your Module:** T-GAT Anomaly Engine + Differential Privacy + NGO Dashboard
**Your Innovations:** #8 (T-GAT + DP Heatmap)

**What You Build:**
| File | What It Does |
|:---|:---|
| `server/tgat_anomaly.py` | GATConv + GRU anomaly detector (PyTorch Geometric) |
| `server/privacy_heatmap.py` | Laplace noise DP engine + district aggregation |
| `server/graph_builder.py` | Constructs community graph from Supabase incident data |
| `dashboard/index.html` | React + D3.js NGO command center map |
| `dashboard/HeatmapLayer.js` | Renders DP-noised incident density by district |
| `dashboard/AnomalyAlert.js` | Renders T-GAT anomaly scores on the map |
| `data/karnataka_district_graph.json` | Pre-built district adjacency graph (nodes + edges) |
| `scripts/seed_synthetic_data.py` | Seeds the graph with synthetic historical incidents for demo |

**Tech Stack You Use:**
- Python + PyTorch + PyTorch Geometric (`torch_geometric`)
- `numpy` (Laplace noise)
- Supabase (PostgreSQL, free tier)
- React.js + D3.js (dashboard map)
- ACLED India dataset (free, public — seed real historical conflict data into graph)

**Timeline:**
- **Hour 0-4:** Set up Supabase DB schema. Define the district incidents table.
- **Hour 4-10:** Build Karnataka district adjacency graph JSON (pull census district border data). Seed synthetic incident data.
- **Hour 10-18:** Build and train T-GAT model on synthetic graph. Validate anomaly scoring.
- **Hour 18-22:** Build React + D3.js dashboard. Wire Supabase live data to the map.
- **Hour 22-24:** Integration testing. Connect Member B's backend incident logging to your Supabase table. Final heatmap demo polish.

**What You Depend On:**
- Member B's incident logging endpoint (needs to write to your Supabase table) — coordinate schema by Hour 4.
- No hard dependency on Member A.

---

## PART 5: INTEGRATION CHECKPOINTS

There are exactly **2 integration moments** where all 3 members must sync:

### 🔁 Checkpoint 1 — Hour 4 (Schema Sync)
**Who:** Member B + Member C
**What:** Agree on the exact JSON schema of an incident object that gets logged to Supabase.
```json
{
  "id": "uuid",
  "incident_type": "caste_discrimination",
  "district": "Bidar",
  "taluk": "Humnabad",
  "timestamp": "2025-06-30T12:00:00Z",
  "severity": 0.8,
  "law_matched": "SC/ST Act Section 3(1)(v)"
}
```
Once agreed, both can work independently.

### 🔁 Checkpoint 2 — Hour 22 (Full Integration Test)
**Who:** All 3 Members
**What:** Run a complete end-to-end demo flow together:
1. Member A sends a voice note from the React.js + Vite client.
2. Member B's swarm processes it and logs to Supabase.
3. Member C's dashboard picks up the new incident, runs DP noise, shows T-GAT anomaly spike.
4. Fix any integration bugs together.

---

## PART 6: DEMO SCRIPT (What Judges See)

**Duration: 90 seconds**

| Time | What Happens | Who Built It |
|:---|:---|:---|
| 0:00 - 0:15 | Open phone. It shows a recipe app. | Member A (Decoy UI) |
| 0:15 - 0:25 | 3-finger hold → Secure mode unlocks. | Member A (Shadow UI) |
| 0:25 - 0:40 | User sends Kannada voice note describing caste discrimination. Phonetic parser corrects ASR errors live on screen. | Member B (Phonetic + Swarm) |
| 0:40 - 0:55 | LangGraph agents traverse Legal Graph → identify SC/ST Act Section 3(1)(v) → PDF complaint generated and downloaded. | Member B (LangGraph + Legal Graph) |
| 0:55 - 1:05 | ZKP QR shown: "Income eligibility proven offline. No Aadhaar data shared." | Member A (ZKP Wallet) |
| 1:05 - 1:30 | Switch to NGO dashboard. Karnataka map shows DP-noised heatmap. T-GAT spikes on Bidar district: "Systemic exclusion anomaly detected." | Member C (T-GAT + Dashboard) |

---

## PART 7: FREE TECH STACK SUMMARY

| Component | Technology | Cost |
|:---|:---|:---|
| Frontend | React Native / React.js | Free |
| Backend | FastAPI on Render | Free tier |
| Agent Swarm | LangGraph + LangChain | Free |
| LLM | Gemini 2.0 Flash API | Free (1M tokens/day) |
| GNN | PyTorch + PyTorch Geometric | Free |
| AST Model | HuggingFace MIT/ast-audioset | Free |
| Sentence NLP | paraphrase-multilingual-MiniLM | Free |
| Database | Supabase PostgreSQL | Free tier |
| Dashboard | React + D3.js | Free |
| ZKP Crypto | Node.js `crypto` (built-in) | Free |
| Privacy | numpy Laplace noise | Free |
| **Total** | | **₹0** |

---

## PART 8: GIT BRANCHING STRATEGY & COLLABORATION WORKFLOW

### 8.1 Repository Setup (Do This First — All 3 Members Together, 15 Minutes)

One person creates the GitHub repo. Everyone clones it.

```bash
# Person creating the repo (suggested: Member B as backend is the integration point)
git init civic-shield
cd civic-shield
git remote add origin https://github.com/your-team/civic-shield.git

# Create the folder structure before first push
mkdir -p app server dashboard data scripts server/tests
touch app/.gitkeep server/.gitkeep dashboard/.gitkeep

git add .
git commit -m "chore: initial repo structure"
git push origin main
```

Everyone else clones:
```bash
git clone https://github.com/your-team/civic-shield.git
cd civic-shield
```

---

### 8.2 Branch Structure (The Rules)

```
main                          ← Production-ready, demo-ready code ONLY
│
├── dev                       ← Integration branch. All features merge here first.
│   │
│   ├── feature/client-app    ← Member A (frontend/src/app/)
│   ├── feature/backend-swarm ← Member B (backend/server/)
│   └── feature/analytics     ← Member C (frontend/src/dashboard/ + backend/analytics/)
```

**Rule 1:** Nobody ever commits directly to `main` or `dev`.  
**Rule 2:** Each member only works in their own `feature/` branch.  
**Rule 3:** `dev` is merged into `main` only at the end when everything is stable and the demo is rehearsed.  
**Rule 4:** Before every Checkpoint sync, pull the latest `dev` into your branch.

> **Deployment boundary:** `frontend/` folder → Vercel. `backend/` folder → Render. Both live in the same repo.

---

### 8.3 Daily Branch Commands (What Each Member Runs)

**Setting up your branch (do once at the start):**
```bash
# Member A
git checkout -b feature/client-app
git push -u origin feature/client-app

# Member B
git checkout -b feature/backend-swarm
git push -u origin feature/backend-swarm

# Member C
git checkout -b feature/analytics
git push -u origin feature/analytics
```

**Your daily work loop (repeat throughout the hackathon):**
```bash
# 1. Pull latest changes from dev into your branch first (do this every 2-3 hours)
git fetch origin
git merge origin/dev

# 2. Do your work, then save progress frequently (every 1-2 hours minimum)
git add .
git commit -m "feat(client): implement shake-to-wipe accelerometer handler"

# 3. Push to your remote branch
git push origin feature/client-app  # (or your branch name)
```

---

### 8.4 Commit Message Convention (Keep It Professional)

Use this format for all commits:  
`type(scope): short description`

| Type | When to Use | Example |
|:---|:---|:---|
| `feat` | New feature added | `feat(backend): add LangGraph voice-parser agent` |
| `fix` | Bug fixed | `fix(client): correct accelerometer threshold value` |
| `chore` | Setup, config, deps | `chore: add requirements.txt` |
| `data` | Data files added | `data: add karnataka district adjacency graph JSON` |
| `test` | Test scripts added | `test(backend): add phonetic parser accuracy tests` |
| `docs` | Documentation update | `docs: update API endpoint list in README` |
| `wip` | Work in progress, incomplete | `wip(analytics): partial T-GAT forward pass` |

---

### 8.5 Merge Schedule (When, Who, What)

This is the exact schedule of every merge event during the hackathon:

```
HOUR 0 ─── Repo setup. All 3 push initial empty structure to their branches.

HOUR 4 ─── CHECKPOINT 1 (B + C only)
            Member B: push feature/backend-swarm (Supabase schema defined)
            Member C: push feature/analytics (Supabase schema defined)
            → B and C agree on incident schema on a call. No merge yet.

HOUR 8 ─── Member B merges feature/backend-swarm → dev
            Reason: API endpoint stubs are ready so Member A can start integration.
            Commands (Member B runs):
            git checkout dev
            git merge feature/backend-swarm
            git push origin dev
            git checkout feature/backend-swarm  ← Go back to your branch

HOUR 8 ─── Member A pulls dev into feature/client-app
            git fetch origin
            git merge origin/dev
            Now Member A can see the API endpoint signatures.

HOUR 14 ── Member A merges feature/client-app → dev (first pass)
            Reason: Voice recorder + ZKP wallet ready for Member B to test with.
            Same merge commands as above (Member A runs).

HOUR 18 ── Member C merges feature/analytics → dev (first pass)
            Reason: Supabase tables are live. Member B can now write incident logs.

HOUR 22 ── CHECKPOINT 2 (All 3 together — Integration Test)
            ALL 3 merge their feature branches → dev
            Run the full end-to-end demo flow.
            Fix bugs on your own branches, commit, push.

HOUR 23 ── Final Polish
            All 3 merge feature branches → dev one last time.
            Team lead (Member B) merges dev → main.
            git checkout main
            git merge dev
            git push origin main
            Tag the release: git tag v1.0-demo && git push origin v1.0-demo

HOUR 24 ── Demo from main branch only. Do NOT push any new commits to main.
```

---

### 8.6 How to Handle Merge Conflicts

Conflicts will only realistically happen at integration checkpoints. Here is how to resolve them:

```bash
# When you run git merge origin/dev and see conflicts:
# Git will mark conflicted files like this:
# <<<<<<< HEAD
# your code
# =======
# their code
# >>>>>>> origin/dev

# Step 1: Open the conflicted file in your editor
# Step 2: Keep the correct version (usually keep BOTH if they are different features)
# Step 3: Delete the <<<, ===, >>> markers
# Step 4: Save and commit:
git add .
git commit -m "fix: resolve merge conflict in agent_swarm.py"
git push origin your-branch-name
```

**The golden rule to avoid conflicts:** Members A, B, and C should NEVER edit the same file. The folder ownership is absolute:
- Only Member A touches `/app/`
- Only Member B touches `/server/`
- Only Member C touches `/dashboard/` and `/data/`
- `requirements.txt` and `README.md` → coordinate on a call before editing.

---

### 8.7 Shared Files That ALL 3 Must Coordinate On

These files are shared between modules. Assign one owner and notify others before editing:

| File | Owner | Others Must Do |
|:---|:---|:---|
| `requirements.txt` | Member B | Notify B before adding Python packages |
| `package.json` | Member A | Notify A before adding JS packages |
| `README.md` | All | Each writes their own section; merge at Hour 22 |
| `.env.example` | Member B | B adds all API keys; others copy the template |
| `data/legal_knowledge_graph.json` | Member B | Read-only for A and C |
| `data/karnataka_district_graph.json` | Member C | Read-only for B |

---

### 8.8 Environment Variables (.env) Setup

Member B creates `.env.example` and commits it. Everyone copies it as `.env` locally (`.env` is gitignored):

```bash
# .env.example (commit this)
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
TWILIO_SID=your_twilio_sid
TWILIO_AUTH=your_twilio_auth
BACKEND_URL=http://localhost:8000
```

```bash
# Each member runs locally (DO NOT commit .env)
cp .env.example .env
# Then fill in the actual values
```

Make sure `.gitignore` contains:
```
.env
__pycache__/
node_modules/
*.pyc
.DS_Store
```

---

### 8.9 Complete Git Command Reference Card

Print this out during the hackathon:

```bash
# Check what branch you are on
git branch

# See what files you have changed
git status

# Save all your changes with a message
git add . && git commit -m "feat(your-scope): description"

# Push your work to GitHub
git push origin your-branch-name

# Get latest changes from dev (run every 2-3 hours)
git fetch origin && git merge origin/dev

# See recent commit history
git log --oneline -10

# Undo last commit but keep the code changes
git reset --soft HEAD~1

# See difference between your branch and dev
git diff origin/dev..HEAD --stat
```

---

## PART 9: MEMBER RESPONSIBILITIES (Full Ownership Guide)

Each member has **primary responsibilities** (things only they build), **shared responsibilities** (things they contribute to together), and **quality expectations** (what a finished piece looks like for judging).

---

### 👤 MEMBER A — Frontend & Client Safety Engineer

#### Primary Responsibilities
You own the **entire user-facing experience**. If a judge picks up the phone and interacts with CIVIC-SHIELD, everything they see and touch is your work.

| Responsibility | Description | Definition of Done |
|:---|:---|:---|
| **Decoy App Shell** | Build a fully working recipe/calendar app that convincingly looks like a real utility app. Not a placeholder — real content, real UI. | Opens cleanly, has 2-3 navigable screens, looks like a real app a judge wouldn't question. |
| **3-Finger Gesture Unlock** | Implement multi-touch detection. 3 fingers held for 2.5 seconds transitions to CIVIC-SHIELD secure mode. | Works consistently on an actual device/emulator. No accidental triggers. |
| **Shake-to-Wipe** | Subscribe to accelerometer. Magnitude > 16.5 m/s² triggers instant mode reset and cache clear. | Shake test works. Secure mode disappears within 300ms of shake. |
| **Voice Recorder UI** | Record audio, display waveform, send to backend `/process-voice` endpoint. | Audio is recorded, displayed visually, sent and acknowledged by backend. |
| **ZKP Wallet & QR Generator** | Generate Pedersen commitment from user income + blinding factor. Display as scannable QR code. | QR code generated, displays commitment hash, Member B's verifier confirms it offline. |
| **Code Word Engine (Client)** | Wire the on-device sentence-transformer similarity check to the live transcription output. | "Order food" / "ಊಟ ಆರ್ಡರ್" triggers silent alert mode correctly. |
| **AST Threat UI** | Display real-time threat status indicator when backend `/detect-threat` returns a positive flag. | Alert banner appears within 2 seconds of threat detection. |
| **Overall UX Polish** | Transitions, loading states, error handling, color scheme, font choices. | App feels premium, not like a student prototype. Judges will see this. |

#### Shared Responsibilities
- **With Member B:** Agree on the exact JSON format of the voice payload sent from client to backend by Hour 6.
- **With Member B:** Test the full client → backend → response round trip at Hour 22.
- **Demo Rehearsal:** Operate the phone during the live demo. You control the device on stage.

#### What Judges Will Evaluate You On
- Does the decoy app look convincing?
- Is the 3-finger gesture reliable or does it sometimes fail?
- Is the ZKP QR code actually verifiable (not just an image)?
- Does the app feel polished or like a rushed prototype?

#### Pitfalls to Avoid
- Do NOT skip the decoy app. A blank white screen with a "decoy" label is not acceptable.
- Do NOT hardcode the ZKP values. The user must be able to enter their income and generate a real commitment.
- Do NOT use placeholder screens for voice recording. It must actually record.

---

### 👤 MEMBER B — Backend & Agent Swarm Engineer

#### Primary Responsibilities
You own the **entire intelligence layer**. Every decision the system makes about legal matching, document generation, and routing goes through your code. You are also the **integration hub** — both Member A and Member C depend on your API endpoints and database schema.

| Responsibility | Description | Definition of Done |
|:---|:---|:---|
| **FastAPI Server Setup** | Set up the FastAPI server with CORS enabled. Define all endpoint stubs (empty but typed) by Hour 4. | `GET /health` returns 200. All endpoints are defined and documented in a README. |
| **Phonetic Soundex Parser** | Build the Indian phonetic mapping + Levenshtein distance matching against the legal registry. | "Guru Laxmy" resolves to "Gruha Lakshmi" with confidence > 0.75. |
| **Legal Knowledge Graph** | Define the full JSON graph of protective acts (SC/ST Act, PWDV Act, POSH Act, MNREGA) and welfare schemes. Write the traversal function. | Given incident type "spousal violence", traversal returns PWDV Act Section 3, IPC 498A, relief types, and authority details within 100ms. |
| **LangGraph Agent Swarm** | Build the full 5-node StateGraph: Triage → Narrative → Evidence → Routing → Empathy. | A voice input reaches the swarm and exits as a PDF complaint path, evidence checklist, next actions, and empathy message. |
| **Gemini API Integration** | Wire Gemini 2.0 Flash to the swarm agents. Prompt must return structured text/JSON as expected by the Swarm State. | Swarm generates a valid narrative, evidence list, and empathy message for any voice input. |
| **PDF Complaint Builder** | Generate a legally formatted PDF using `reportlab` or `fpdf2`. Include citizen pseudonym, incident details, law sections, authority name, and submission date. | PDF opens correctly, looks professional, has all required fields filled. |
| **AST Threat Detector API** | Load the HuggingFace AST model. Expose `/detect-threat` endpoint that accepts audio bytes and returns threat labels + probabilities. | Audio of a scream returns `is_threat: true` with `Scream` probability > 0.65. |
| **ZKP Verifier Endpoint** | Expose `/verify-zkp` endpoint. Take commitment + proof object, verify Pedersen commitment and range bound. | Member A's QR commitment passes verification. A modified value fails. |
| **Supabase Incident Logger** | After each complaint is processed, log anonymized incident metadata (type, district, timestamp, law matched) to Supabase. | Member C's dashboard shows new incidents appearing in the DB within 5 seconds. |
| **`.env.example` file** | Create and commit the environment template with all required keys. | All 3 members can configure their local environments from this file. |

#### Shared Responsibilities
- **With Member A:** Define voice payload JSON schema (Hour 6). Provide working API stubs (Hour 8).
- **With Member C:** Define Supabase incident table schema (Hour 4 Checkpoint). Ensure logs are written in the agreed format.
- **API Documentation:** Maintain a simple `API.md` file listing all endpoints, request formats, and response formats so Member A and C can work independently.

#### What Judges Will Evaluate You On
- Does the LangGraph swarm actually run through all 5 agents, or does it short-circuit?
- Is the legal graph deterministic (same input always gives same legal output)?
- Does the PDF look legally credible?
- Can you explain every agent's role and state transition if asked?

#### Pitfalls to Avoid
- Do NOT use a single huge LLM prompt that does everything. Each agent must have a specific, narrow responsibility.
- Do NOT let Gemini make legal decisions without the Knowledge Graph as a guard. LLMs hallucinate legal sections.
- Do NOT forget CORS configuration. Member A's frontend will fail to connect without it.

---

### 👤 MEMBER C — Analytics & Dashboard Engineer

#### Primary Responsibilities
You own the **data aggregation, anomaly intelligence, and visualization layer**. Your work is what separates CIVIC-SHIELD from a basic complaint app. When a judge asks "what happens at scale?", your dashboard is the answer.

| Responsibility | Description | Definition of Done |
|:---|:---|:---|
| **Supabase Database Setup** | Create the `civic_incidents` table with correct schema. Share credentials and schema with Member B by Hour 4. | Table exists in Supabase. Member B can write rows to it. |
| **Karnataka District Graph** | Build the `karnataka_district_graph.json` file with district nodes and geographical edge connections. | Graph has all 31 Karnataka districts as nodes with correct border adjacencies as edges. |
| **Synthetic Data Seeder** | Write `scripts/seed_synthetic_data.py` to pre-populate the graph with realistic historical incident distributions. | Script runs and inserts 200+ synthetic incidents spread across 31 districts with realistic weightings. |
| **Differential Privacy Engine** | Implement the Laplace noise injector. Input: raw district counts. Output: noised counts safe for public display. | District count of 1 is reliably masked. District count of 50 remains approximately correct (±5). |
| **T-GAT Model** | Build the GATConv + GRU PyTorch model. Train on the synthetic graph. Save weights as `tgat_weights.pt`. | Model scores an anomaly probability for each district node. High-incident districts score > 0.75. |
| **Graph Builder** | Write `server/graph_builder.py` that reads from Supabase, builds the live PyG graph object, and feeds it to the T-GAT model. | Runs on demand and returns updated anomaly scores within 10 seconds. |
| **Anomaly Alert API** | Expose `/anomaly-scores` endpoint that returns per-district anomaly probability scores. | Returns JSON like `{"Bidar": 0.82, "Raichur": 0.71, ...}` based on current DB state. |
| **React + D3.js Dashboard** | Build the NGO command center map. Show Karnataka districts colored by anomaly severity. Display DP-noised incident counts on hover. | Map loads, districts are colored correctly by risk tier (green/yellow/red), hover shows count. |
| **Live Update Mechanism** | Dashboard polls `/anomaly-scores` every 30 seconds and re-renders the map. | During the demo, injecting a synthetic spike into Supabase causes the map to update live. |
| **Demo Data Injection Script** | Write `scripts/inject_demo_spike.py` that inserts 15 incidents into Bidar district within seconds, causing a live anomaly spike on stage. | Running the script during the demo causes Bidar to turn red on the map within 60 seconds. |

#### Shared Responsibilities
- **With Member B:** Agree on the `civic_incidents` table schema at Hour 4. This is your most critical dependency.
- **Dashboard API contract:** Share the `/anomaly-scores` endpoint format with Member B so he knows what the analytics server expects.
- **Demo Rehearsal:** You operate the laptop showing the NGO dashboard on stage. Practice the data injection script so it runs smoothly during the demo.

#### What Judges Will Evaluate You On
- Is the T-GAT model actually trained, or just instantiated with random weights?
- Does the Differential Privacy genuinely mask individual data (can they reverse-engineer a single incident from the dashboard)?
- Does the map update live during the demo or is it a static screenshot?
- Can you explain what GATConv attention weights mean when asked?

#### Pitfalls to Avoid
- Do NOT show random anomaly scores that never change. The live update during the demo is critical for impact.
- Do NOT use a basic choropleth map with hardcoded colors. The colors must be driven by actual model output.
- Do NOT forget to train the model before the demo. Untrained models output near-random scores.
- Do NOT skip the privacy explanation. Judges will ask how you protect individual reporters. Know the ε=1.0 Laplace mechanism cold.

---

## PART 10: SHARED TEAM RESPONSIBILITIES

These responsibilities belong to the entire team, not any single member:

| Responsibility | Who Leads | What It Involves |
|:---|:---|:---|
| **Pitch Deck** | All 3 equally | 8-10 slides: Problem, Solution, Architecture, Innovations, Demo, Real-World Impact, Team. Prepare together. |
| **Demo Rehearsal** | All 3 | Practice the 90-second flow at Hour 22 and Hour 23. Each person must know exactly what they are doing on stage. |
| **Q&A Preparation** | All 3 | Each member prepares answers for questions about their own module. See the Q&A defense guide in the implementation plan. |
| **README.md** | All 3 | Each writes the section about their own module. Member B merges at Hour 22. |
| **API.md** | Member B | Documents all endpoints. A and C review and confirm their usage is correct. |
| **Video Demo (if required)** | Member A records | Member A records screen + audio demo. Others review and approve. |

---

## PART 11: COMPLETE FILE STRUCTURE

The repo is a **monorepo** — one GitHub repo, two deployable units: `frontend/` and `backend/`.

```
civic-shield/  (Awaaz/)
│
├── 📄 README.md                              ← All 3. Merged at Hour 22.
├── 📄 API.md                                 ← Member B. All endpoint contracts.
├── 📄 .gitignore                             ← Member B. Created at Hour 0.
│
├── 📁 frontend/                              ← Deploys to VERCEL
│   ├── 📄 package.json                       ← Member A. All JS dependencies.
│   ├── 📄 vite.config.js                     ← Member A. Dev server + proxy to backend.
│   ├── 📄 vercel.json                        ← Member A. SPA rewrite rules for Vercel.
│   ├── 📄 .env.example                       ← Member A. VITE_BACKEND_URL etc.
│   ├── 📁 public/
│   │   ├── 📄 index.html                     ← Member A. HTML entry point.
│   │   └── 📄 recipe_data.json               ← Member A. Decoy app static data.
│   └── 📁 src/
│       ├── 📁 app/                           ← Member A owns everything here
│       │   ├── 📄 App.js                     ← Root entry. Renders ShadowWrapper.
│       │   ├── 📄 ShadowWrapper.js           ← Decoy/real mode toggle. Gesture + accelerometer.
│       │   ├── 📄 DecoyApp.js                ← Fully working recipe/calendar decoy shell.
│       │   ├── 📄 CivicShieldApp.js          ← Secure app root (loads after 3-finger unlock).
│       │   ├── 📄 VoiceRecorder.js           ← Records audio, waveform, sends to backend.
│       │   ├── 📄 ZKPWallet.js               ← Pedersen commitment generator + QR output.
│       │   ├── 📄 zkp_auth.js                ← Core ZKP crypto logic (SHA-256 commitments).
│       │   ├── 📄 CodeWordEngine.js          ← On-device MiniLM code word trigger matcher.
│       │   ├── 📄 ThreatMonitor.js           ← Polls /detect-threat, shows alert UI.
│       │   ├── 📄 ReportScreen.js            ← Main report filing screen.
│       │   └── 📄 ConfirmationScreen.js      ← Shows law matched, PDF download, routing.
│       └── 📁 dashboard/                     ← Member C owns everything here
│           ├── 📄 App.jsx                    ← React root for NGO command center.
│           ├── 📄 HeatmapLayer.js            ← D3.js Karnataka district heatmap.
│           ├── 📄 AnomalyAlert.js            ← Displays T-GAT anomaly scores per district.
│           ├── 📄 DistrictTooltip.js         ← Hover tooltip: DP-noised count + score.
│           ├── 📄 LiveUpdater.js             ← Polls /anomaly-scores every 30s.
│           └── 📁 assets/
│               └── 📄 karnataka_geojson.json ← Karnataka district boundary GeoJSON.
│
└── 📁 backend/                               ← Deploys to RENDER
    ├── 📄 requirements.txt                   ← Member B. All Python dependencies.
    ├── 📄 render.yaml                        ← Member B. Render deployment config.
    ├── 📄 Procfile                           ← Member B. uvicorn start command.
    ├── 📄 .env.example                       ← Member B. All API keys template.
    ├── 📁 server/                            ← Member B owns everything here
    │   ├── 📄 main.py                        ← FastAPI app. All endpoints + CORS.
    │   ├── 📄 phonetic_parser.py             ← Indian Soundex + Levenshtein resolver.
    │   ├── 📄 legal_graph.py                 ← Legal graph loader + traversal engine.
    │   ├── 📄 agent_swarm.py                 ← LangGraph StateGraph: 5 agents.
    │   ├── 📄 threat_detector.py             ← AST model + /detect-threat handler.
    │   ├── 📄 zkp_verifier.py                ← Pedersen commitment verifier.
    │   ├── 📄 pdf_builder.py                 ← Legal complaint PDF generator.
    │   ├── 📄 supabase_client.py             ← Supabase connection + incident logger.
    │   ├── 📄 graph_builder.py               ← Reads Supabase → builds PyG graph.
    │   └── 📁 tests/                         ← Member B
    │       ├── 📄 test_phonetics.py
    │       ├── 📄 test_legal_graph.py
    │       ├── 📄 test_agent_swarm.py
    │       ├── 📄 test_zkp.py
    │       └── 📄 test_threat_detector.py
    ├── 📁 analytics/                         ← Member C owns everything here
    │   ├── 📄 tgat_anomaly.py                ← T-GAT model (GATConv + GRU) + training.
    │   ├── 📄 privacy_heatmap.py             ← Laplace noise DP engine.
    │   ├── 📄 graph_builder.py               ← Supabase → PyG graph builder.
    │   ├── 📄 anomaly_api.py                 ← FastAPI sub-app: /anomaly-scores.
    │   └── 📄 tgat_weights.pt                ← Trained model weights (after training).
    ├── 📁 data/                              ← Shared. B owns legal graph, C owns district.
    │   ├── 📄 legal_knowledge_graph.json     ← Member B.
    │   ├── 📄 karnataka_district_graph.json  ← Member C.
    │   └── 📄 scheme_registry.json          ← Member B.
    └── 📁 scripts/                           ← Member C
        ├── 📄 seed_synthetic_data.py
        └── 📄 inject_demo_spike.py
```

---

### File Ownership Quick Reference

| File | Owner | Created By Hour |
|:---|:---|:---|
| `frontend/src/app/ShadowWrapper.js` | Member A | Hour 8 |
| `frontend/src/app/DecoyApp.js` | Member A | Hour 4 |
| `frontend/src/app/ZKPWallet.js` | Member A | Hour 16 |
| `frontend/src/app/VoiceRecorder.js` | Member A | Hour 10 |
| `frontend/src/app/CodeWordEngine.js` | Member A | Hour 12 |
| `frontend/src/dashboard/HeatmapLayer.js` | Member C | Hour 20 |
| `frontend/src/dashboard/AnomalyAlert.js` | Member C | Hour 20 |
| `backend/server/main.py` (stubs) | Member B | Hour 4 |
| `backend/server/legal_graph.py` | Member B | Hour 10 |
| `backend/server/agent_swarm.py` | Member B | Hour 14 |
| `backend/server/phonetic_parser.py` | Member B | Hour 8 |
| `backend/server/threat_detector.py` | Member B | Hour 18 |
| `backend/server/pdf_builder.py` | Member B | Hour 16 |
| `backend/data/legal_knowledge_graph.json` | Member B | Hour 8 |
| `backend/analytics/tgat_anomaly.py` | Member C | Hour 16 |
| `backend/analytics/privacy_heatmap.py` | Member C | Hour 10 |
| `backend/analytics/graph_builder.py` | Member C | Hour 12 |
| `backend/data/karnataka_district_graph.json` | Member C | Hour 6 |
| `backend/scripts/seed_synthetic_data.py` | Member C | Hour 8 |
| `backend/scripts/inject_demo_spike.py` | Member C | Hour 20 |
| `backend/.env.example` | Member B | Hour 0 |
| `backend/requirements.txt` | Member B | Hour 0 |
| `frontend/.env.example` | Member A | Hour 0 |
| `frontend/package.json` | Member A | Hour 0 |
| `README.md` | All 3 | Merged Hour 22 |

---

## PART 12: DEPLOYMENT GUIDE (How to Go Live)

### 12.1 Services Used & Why

| Service | What It Hosts | Cost | URL After Deploy |
|:---|:---|:---|:---|
| **Vercel** | `frontend/` — React app + NGO dashboard | Free | `civic-shield.vercel.app` |
| **Render** | `backend/` — FastAPI + analytics engine | Free | `civic-shield-backend.onrender.com` |
| **Supabase** | PostgreSQL database (incident logs) | Free | Dashboard at `supabase.com` |

---

### 12.2 Step 1 — Supabase Setup (Member C, Hour 0-4)

1. Go to [supabase.com](https://supabase.com) → New Project → Name it `civic-shield`
2. Open **SQL Editor** and run:
```sql
CREATE TABLE civic_incidents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  incident_type TEXT NOT NULL,
  district TEXT NOT NULL,
  taluk TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  severity FLOAT,
  law_matched TEXT,
  pseudonym TEXT
);
```
3. Go to **Settings → API** → Copy `Project URL` and `anon public key`
4. Share both with Member B immediately (they need it for `.env`)

---

### 12.3 Step 2 — Backend on Render (Member B, Hour 23)

```bash
# 1. Make sure backend/ is pushed to GitHub
git add backend/
git commit -m "feat(backend): production-ready backend"
git push origin main

# 2. Go to render.com → New → Web Service
# 3. Connect your GitHub repo
# 4. Set these settings:
#    Root Directory : backend
#    Build Command  : pip install -r requirements.txt
#    Start Command  : uvicorn server.main:app --host 0.0.0.0 --port $PORT
#    Instance Type  : Free

# 5. Add Environment Variables in Render dashboard:
#    GEMINI_API_KEY      = your key
#    SUPABASE_URL        = from Member C
#    SUPABASE_ANON_KEY   = from Member C
#    FRONTEND_URL        = https://civic-shield.vercel.app

# 6. Click Deploy. Render auto-reads render.yaml too.
# 7. Note down the URL: https://civic-shield-backend.onrender.com
```

> ⚠️ Render free tier **spins down after 15 mins of inactivity**. For the demo, open the backend URL in a browser 5 minutes before presenting to wake it up.

---

### 12.4 Step 3 — Frontend on Vercel (Member A, Hour 23)

```bash
# 1. Make sure frontend/ is pushed to GitHub
git add frontend/
git commit -m "feat(client): production-ready frontend"
git push origin main

# 2. Go to vercel.com → New Project → Import GitHub repo
# 3. Set these settings:
#    Framework Preset : Vite
#    Root Directory   : frontend
#    Build Command    : npm run build
#    Output Directory : dist

# 4. Add Environment Variables in Vercel dashboard:
#    VITE_BACKEND_URL      = https://civic-shield-backend.onrender.com
#    VITE_SUPABASE_URL     = from Member C
#    VITE_SUPABASE_ANON_KEY = from Member C

# 5. Click Deploy.
# 6. Your app is live at: https://civic-shield.vercel.app
```

---

### 12.5 Local Development Setup (All 3 Members)

Each member runs their part locally during development:

**Member B — Run backend locally:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # Fill in your actual keys
uvicorn server.main:app --reload --port 8000
# Backend running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Member A — Run frontend locally:**
```bash
cd frontend
npm install
cp .env.example .env            # Set VITE_BACKEND_URL=http://localhost:8000
npm run dev
# Frontend running at http://localhost:3000
# Proxy in vite.config.js auto-routes /api → localhost:8000
```

**Member C — Run dashboard locally:**
```bash
# Dashboard is part of frontend — same command as Member A
# For analytics engine (Python):
cd backend
python analytics/tgat_anomaly.py   # Train model
python analytics/anomaly_api.py    # Run analytics server on port 8001
```

---

### 12.6 The Connection Point (How Frontend Talks to Backend)

This is the only thing that connects Member A's and Member B's work:

```javascript
// In frontend/.env
VITE_BACKEND_URL=https://civic-shield-backend.onrender.com

// In frontend/src/app/VoiceRecorder.js (Member A)
const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/process-voice`, {
  method: 'POST',
  body: formData
})
```

```javascript
// In frontend/src/dashboard/LiveUpdater.js (Member C)
const scores = await fetch(`${import.meta.env.VITE_BACKEND_URL}/anomaly-scores`)
```

**Locally:** `VITE_BACKEND_URL=http://localhost:8000`  
**In production:** `VITE_BACKEND_URL=https://civic-shield-backend.onrender.com`  
Change only this one variable to switch between local and deployed.

---

### 12.7 Pre-Demo Deployment Checklist (Hour 23)

```
☐ Supabase table created and seeded with synthetic data (Member C)
☐ Backend deployed on Render, /health endpoint returns 200 (Member B)
☐ Frontend deployed on Vercel, app loads without console errors (Member A)
☐ VITE_BACKEND_URL on Vercel points to Render URL (Member A)
☐ FRONTEND_URL on Render points to Vercel URL (Member B)
☐ T-GAT weights file (tgat_weights.pt) committed to backend/ (Member C)
☐ inject_demo_spike.py tested and confirmed to update dashboard (Member C)
☐ Full 90-second demo rehearsed end-to-end (All 3)
☐ Render backend woken up 5 mins before demo (Member B)
```
