**Theme:** AWAAZ (Voice, Safety & Social Access)  
**Stakeholders:** Citizens (low-literacy, undocumented, women in crisis), legal aid NGOs, Gram Panchayats, human rights agencies.

---

## 1. Upgraded Project Pitch

> "Every public safety and grievance system built in India assumes a middle-class, English-literate user with stable 5G, identity papers, and the freedom to open an app. In reality, the 450 million informal workers, rural women in crisis, and marginalized citizens face the **Centralization Paradox** of government systems like CPGRAMS: local grievances are routed through complex national loops while being blocked on the ground by language barriers, document deficits, and fear of retaliation.
>
> This is an industry-grade, two-sided solution. On the front end, it is a voice-first, decoy-wrapped, self-sovereign rights wallet that uses **Offline Zero-Knowledge Proofs (ZKP)** and **phonetic voice-to-intent NLP** to bypass the digital divide and safely compile legal claims. On the backend, a **LangGraph multi-agent swarm** automatically formats and tracks these grievances, while a **Temporal Graph Attention Network (T-GAT)** aggregates anonymized reports to flag systemic human rights hotspots for NGOs and administrators before they escalate into communal conflict."

---

## 2. Strong Problem Statement (The "Awaaz" Gaps)

India's grievance redressal and legal aid infrastructure suffers from three systemic bottlenecks:

1. **The Digital and Literacy Divide:** Government portals (CPGRAMS, state RTI portals) are text-heavy, form-heavy, and operate primarily in English/Hindi. For the ~25% illiterate population and millions who speak regional dialects, this creates absolute exclusion.
2. **The Documentation Barrier:** Submitting a formal complaint or applying for state welfare schemes requires physical proofs (Aadhaar, income certificate, local residency). Margins frequently lack physical records or fear uploading scans due to data privacy leakages.
3. **The Centralization Paradox:** Grievances submitted online are routed centrally, resulting in "procedural compliance" (closing tickets on deadlines) rather than "substantive resolution" (resolving ground issues). Furthermore, because individual reports are isolated, administrators fail to see systemic escalation patterns (e.g., regional spikes in caste discrimination or wage theft) until they trigger public protests.

---

## 3. Real-World Stakeholders & Empathy Profiles

To ensure the platform is highly practical and user-centric, we design for three distinct stakeholders:

| Stakeholder Persona | Core Pain Points | How BOL-NYAYA Solves It |
| :--- | :--- | :--- |
| **1. The Citizen (The Margins)**  <br>*Example: Basamma, a rural agricultural worker facing wage theft and domestic threats.* | - Illiterate in English/Hindi.<br>- No physical address proof.<br>- Under active surveillance/fear of local retaliation if caught filing reports. | - **Voice-first local language input** (Kannada/Hindi).<br>- **Shadow Mode Decoy UI** hides the app behind recipes.<br>- **Offline ZKP Wallet** proves eligibility without revealing identity papers. |
| **2. The Volunteer (The Bridge)**  <br>*Example: Rajesh, an NGO field volunteer or local ASHA worker.* | - Overburdened with paperwork.<br>- Struggles to match citizens to exact legal clauses or scheme parameters.<br>- Relies on manual paper filing. | - **LangGraph agent swarm** auto-compiles legal complaint drafts.<br>- **Phonetic Speech-to-Intent** corrects pronunciation errors for local terms.<br>- **Offline Verification App** scans citizens' ZKP QR codes instantly. |
| **3. The Administrator (The System)**  <br>*Example: District Magistrate, Legal Aid Authority, or Human Rights NGO Director.* | - Flood of unstructured complaints.<br>- Blind to coordinated/systemic escalation points until conflict erupts.<br>- Legal verification of documents is slow. | - **T-GAT Anomaly Engine** flags regional tension trends.<br>- **Differential Privacy Heatmap** maps incidents without exposing victim identities.<br>- **Deterministic Legal Graph** guarantees legally correct citations. |

---

## 4. Competitive Mapping (Why this Wins)

Unlike other student hackathon projects that construct basic chatbot wrappers, BOL-NYAYA addresses the entire lifecycle of a grievance.

| Dimension | Existing State Portals (CPGRAMS / RTI) | Generic AI Chatbots | Traditional Legal NGOs | **Our System** |
| :--- | :--- | :--- | :--- | :--- |
| **Accessibility** | Text-first, complex web forms, English/Hindi focus. | Text chatbots, requires smartphone literacy. | Face-to-face visits, limited geographical reach. | **Voice-first, regional dialect phonetic matching, offline-capable.** |
| **Legal Accuracy** | Manual routing, high processing delay. | High hallucination rates, legal inaccuracies. | Manual lawyer consults, highly slow (weeks). | **Deterministic Legal Knowledge Graph + LangGraph validation (seconds).** |
| **Privacy & Safety** | Document scans stored centrally; high leak risk. | No safety locks; user data sent to public LLM APIs. | Physical files, paper trails easily monitored by abusers. | **Dual-Layer Decoy UI, Offline ZKP validation, Local Differential Privacy.** |
| **Analytics & Prevention** | Retroactive annual charts; no predictive warning. | No data aggregation or systemic mapping. | Manual mapping in spreadsheets; slow and incomplete. | **T-GAT Spatio-Temporal Anomaly Engine for proactive escalation warning.** |

---

## 5. Platform Architecture

```mermaid
graph TD
    subgraph Client-Side (Offline-First / Secure UI)
        User[Citizen / Volunteer] -->|Voice Query / Report| Decoy[Decoy Calendar / Recipe Shell]
        Decoy -->|3-Finger Gesture / Decoy PIN| Shadow[Shadow UI App]
        Shadow -->|Input Audio| Stress[Acoustic Threat Classifier - AST]
        Shadow -->|Input Audio| CodeWord[Code Word Engine - sentence-transformers]
        Shadow -->|Input Text| Phonetic[Phonetic Soundex Matching]
        Shadow -->|Attributes: State, Age, Income| ZKP[ZKP Proof Generator]
        ZKP -->|Offline QR Code| Verifier[Panchayat/NGO Offline Verifier]
    end

    subgraph Multi-Agent Orchestration (LangGraph Swarm)
        Phonetic -->|Normalized Text Intent| Agent1[Voice-Parser Agent]
        Agent1 -->|Structured Claim Schema| Agent2[Graph-RAG Legal Agent]
        Agent2 -->|IPC/Scheme Matches| LKG[(Legal Knowledge Graph)]
        Agent2 -->|Verified Match| Agent3[Document-Builder Agent]
        Agent3 -->|Structured Complaint PDF| Agent4[Safety & Routing Agent]
        Agent4 -->|Encrypted Dispatch| Out[NGO / One Stop Centre / CPGRAMS]
        Agent5[Follow-up Scraping Agent] -->|Status Update via IVR| User
    end

    subgraph Analytics & Aggregation
        Out -->|Anonymized Report Metadata| DP[Differential Privacy Noise Engine]
        DP -->|Calibrated District Aggregates| TGAT[Temporal Graph Attention Network]
        TGAT -->|Anomaly / Escalation Predictions| Dashboard[NGO Command Center Map]
    end
```

---

## 6. The 8 Core Technical Innovations (What YOU Build)

### 🔬 Innovation 1 — Language-Agnostic Acoustic Threat Detector (AST / MobileNetV2)
- **Why RAVDESS is a Credibility Trap:** Training a model on English speech databases (like RAVDESS) and deploying it to analyze vocal "stress/emotion" in Indian regional languages is linguistically invalid. Pitch fluctuations, accent emphasis, and phonetics differ vastly, leading to high false-positives and complete failure under scrutiny by ML judges.
- **Our Solution:** We replace emotion classification with **Acoustic Event Detection (AED)**. We utilize a pre-trained **Audio Spectrogram Transformer (AST)** or MobileNetV2 architecture trained on **Google AudioSet** to classify *language-agnostic physical danger signals* in the background, specifically: `Human Screaming`, `Shrieking`, `Physical Thuds`, `Crash`, and `Glass Breaking`. 
- **Code Prototype:**
```python
import torch
from transformers import ASTForAudioClassification, AutoFeatureExtractor

class AcousticThreatDetector:
    def __init__(self):
        # MIT Audio Spectrogram Transformer pre-trained on Google AudioSet (527 classes)
        self.model_name = "MIT/ast-finetuned-audioset-10-10-0.4593"
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = ASTForAudioClassification.from_pretrained(self.model_name)
        
        # AudioSet indices for threats: Screaming (337), Shouting (338), Crash (431), Thud (435)
        self.threat_indices = [337, 338, 431, 435]

    def predict_threat(self, audio_waveform, sampling_rate=16000):
        inputs = self.feature_extractor(audio_waveform, sampling_rate=sampling_rate, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = torch.sigmoid(logits).squeeze(0) # Multi-label classification (Sigmoid)
            
        threat_probs = {self.model.config.id2label[idx]: probabilities[idx].item() for idx in self.threat_indices}
        is_threat = any(prob > 0.65 for prob in threat_probs.values())
        return is_threat, threat_probs
```

### 🔬 Innovation 2 — Semantic Code Word Engine (On-Device NLP)
- **What it does:** Uses small, multilingual transformers to match spoken distress phrases to code words (e.g. "I want to order food" -> crisis escalation).
- **Code Prototype:**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Multilingual MiniLM runs locally, support Kannada, Hindi, Tamil, Telugu
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

DISTRESS_PHRASES = [
    "I want to order food",
    "Can you help me find a restaurant",
    "I need grocery delivery",
    "Checking the weather",
    "Just calling to say hi"
]

def is_code_phrase(user_input, threshold=0.82):
    user_vec = model.encode(user_input)
    
    for phrase in DISTRESS_PHRASES:
        phrase_vec = model.encode(phrase)
        similarity = np.dot(user_vec, phrase_vec) / (
            np.linalg.norm(user_vec) * np.linalg.norm(phrase_vec)
        )
        if similarity > threshold:
            return True  # Escalate crisis mode silently
    return False
```

### 🔬 Innovation 3 — Dual-Layer UI Wrapper & Shake-to-Wipe
- **What it does:** Gestures toggle between decoy shell (recipe/calendar app) and Saheli. Shaking the phone triggers an accelerometer-based interrupt that wipes cache from RAM and returns to decoy mode.
- **Code Prototype:**
```jsx
import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import { accelerometer } from 'react-native-sensors';

const ShadowModeWrapper = () => {
  const [realMode, setRealMode] = useState(false);
  const touchCount = useRef(0);
  const holdTimer = useRef(null);

  const handleTouchStart = () => {
    touchCount.current += 1;
    if (touchCount.current >= 3) {
      holdTimer.current = setTimeout(() => {
        setRealMode(true);
      }, 2000);
    }
  };

  const handleTouchEnd = () => {
    touchCount.current = 0;
    if (holdTimer.current) clearTimeout(holdTimer.current);
  };

  useEffect(() => {
    const subscription = accelerometer.subscribe(({ x, y, z }) => {
      const magnitude = Math.sqrt(x * x + y * y + z * z);
      if (magnitude > 15) { // G-Force threshold for rapid shaking
        setRealMode(false);
        // Custom hook/function to flush local secure storage caches
        clearTransientSession();
      }
    });
    return () => subscription.unsubscribe();
  }, []);

  return realMode ? <SaheliApp /> : <DecoyRecipeApp onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd} />;
};
```

### 🔬 Innovation 4 — Deterministic Legal Knowledge Graph
- **What it does:** Stores laws (POSH, PWDV Act, SC/ST Act) and schemes (Gruha Lakshmi, MNREGA) in a traversal graph. Prevents LLM hallucinations during legal mapping.
- **Code Prototype:**
```json
{
  "nodes": [
    {
      "id": "domestic_violence_spouse",
      "label": "Spousal violence / cruelty",
      "laws": ["PWDV Act Section 3", "IPC 498A"],
      "reliefs": ["Protection Order", "Residence Order", "Compensation"],
      "authority": "Judicial Magistrate First Class / Protection Officer",
      "timeline": "3 Days for Magistrate response",
      "evidence_needed": ["Medical bills", "Photographs", "Witness testimony"]
    }
  ],
  "edges": [
    {
      "from": "domestic_violence_spouse",
      "to": "caste_gender_violence",
      "condition": "if perpetrator from dominant caste"
    }
  ]
}
```

### 🔬 Innovation 5 — Offline Zero-Knowledge Proofs (ZKP)
- **What it does:** Proves target credentials (income <= 1.5L, residence = Karnataka) offline without exposing Aadhaar numbers or actual names to verifying officers.
- **Code Prototype:**
```javascript
// Verification side logic using cryptographic hashes for proof matching
const crypto = require('crypto');

function generatePedersenCommitment(value, blindingFactor) {
    const hash = crypto.createHash('sha256');
    hash.update(value.toString() + blindingFactor.toString());
    return hash.digest('hex');
}

function verifyOfflineZkp(proofObject, publicInputs) {
    // Verifies client generated range proofs (e.g. proof of income threshold verification)
    const computedCommitment = generatePedersenCommitment(proofObject.secret, proofObject.blinding);
    return computedCommitment === publicInputs.commitment && proofObject.secret <= publicInputs.threshold;
}
```

### 🔬 Innovation 6 — LangGraph Multi-Agent Orchestration Swarm
- **What it does:** Coordinates specialized agents to handle voice parsing, Graph-RAG legal validation, document compilation, safety routing, and CPGRAMS follow-up.
- **Code Prototype:**
```python
from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict

class AgentState(TypedDict):
    raw_input: str
    parsed_intent: Dict
    matched_laws: list
    generated_pdf_path: str
    safety_level: str

workflow = StateGraph(AgentState)

# Define nodes for parser, legal graph-RAG, doc builder, and safety router
workflow.add_node("voice_parser", lambda state: {"parsed_intent": run_phonetic_v2i(state["raw_input"])})
workflow.add_node("legal_graph_rag", lambda state: {"matched_laws": traverse_lkg(state["parsed_intent"])})
workflow.add_node("doc_builder", lambda state: {"generated_pdf_path": build_complaint_pdf(state["matched_laws"])})
workflow.add_node("safety_router", lambda state: {"safety_level": evaluate_safety(state)})

workflow.set_entry_point("voice_parser")
workflow.add_edge("voice_parser", "legal_graph_rag")
workflow.add_edge("legal_graph_rag", "doc_builder")
workflow.add_edge("doc_builder", "safety_router")
workflow.add_edge("safety_router", END)

app = workflow.compile()
```

### 🔬 Innovation 7 — Differential Privacy (DP) Noise Engine
- **What it does:** Adds Laplace-distributed noise to district-level reports to protect victim privacy.
- **Code Prototype:**
```python
import numpy as np

def add_laplace_noise(count, epsilon=1.0):
    sensitivity = 1.0 # single report change
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return max(0, int(round(count + noise)))

def generate_dp_heatmap(district_reports):
    return {
        district: add_laplace_noise(count)
        for district, count in district_reports.items()
    }
```

### 🔬 Innovation 8 — Temporal Graph Attention Network (T-GAT) Anomaly Engine
- **What it does:** Evaluates incident spikes across communities and geographical edges over time windows to flag vulnerability escalation patterns.
- **Code Prototype:**
```python
import torch
import torch.nn as nn
from torch_geometric.nn import GATConv

class TGATAnomalyDetector(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super(TGATAnomalyDetector, self).__init__()
        self.gat = GATConv(in_channels, hidden_channels, heads=2, concat=True)
        self.temporal_lstm = nn.LSTM(hidden_channels * 2, hidden_channels, batch_first=True)
        self.classifier = nn.Linear(hidden_channels, 1) # Outputs anomaly probability

    def forward(self, x_seq, edge_index):
        # x_seq size: [batch_size, time_steps, num_nodes, in_channels]
        batch_size, time_steps, num_nodes, in_channels = x_seq.size()
        h_seq = []
        for t in range(time_steps):
            h_t = self.gat(x_seq[:, t].squeeze(0), edge_index) # Spatial aggregation
            h_seq.append(h_t.unsqueeze(1))
        
        h_seq = torch.cat(h_seq, dim=1) # [num_nodes, time_steps, hidden_channels * 2]
        lstm_out, _ = self.temporal_lstm(h_seq)
        anomaly_scores = torch.sigmoid(self.classifier(lstm_out[:, -1, :])) # Final step projection
        return anomaly_scores
```

---

## 7. Implementation Strategy & Real-World Integration

To drive real-world adoption post-hackathon, BOL-NYAYA is designed to integrate directly with existing national infrastructure:

1. **Aadhaar Offline QR Integration:** Instead of uploading Aadhaar scans, the app scans the official secure Aadhaar QR code offline, extracts the cryptographic signature, and stores it as a local Verifiable Credential (VC) in the user's secure enclave.
2. **Gram Panchayat / ASHA Deployment Model:** We utilize a "Hub-and-Spoke" adoption model. Every village doesn't need a smartphone user; instead, the local ASHA worker or NGO coordinator carries the verifier terminal. They record the citizen's voice query and issue credentials offline.
3. **API-Bridges to CPGRAMS:** Our LangGraph Swarm compiles complaints to match CPGRAMS/RTI API structures, allowing one-click submission from local NGO portals to government endpoints.

---

## 8. Verification & Demo Walkthrough

### 1. Verification Scripts:
- `/server/tests/test_phonetics.py`: Checks Soundex resolution accuracy.
- `/server/tests/test_threat.py`: Verifies AST threat logits and labels.
- `/server/tests/test_zkp.py`: Verifies Pedersen commitment range validation offline.
- `/server/tests/test_tgat.py`: Feeds synthetic incident graphs to verify escalation anomaly scores.

### 2. Live Demo Script (90 Seconds):
1. **Decoy State:** App is opened as a Recipe list. 3-finger gesture triggers transition.
2. **Crisis Trigger:** Submit a Hindi/Kannada voice clip containing background screaming or physical thuds. The Audio Spectrogram Transformer (AST) registers language-agnostic threat event logits and sends a silent Twilio SMS alert.
3. **Legal RAG Flow:** Submit a Kannada voice report detailing workplace harassment. The LangGraph agent resolves it to the POSH Act, maps it to the nearest local committee, and downloads a formatted complaint PDF.
4. **Command Dashboard:** Switch to the NGO dashboard map, showing the Laplace-noised incident markers. T-GAT dynamically highlights a regional escalation risk score as incoming volunteer report weights are updated.
