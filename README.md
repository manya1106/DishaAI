# Disha AI (दिशा) — Verifiable Location Intelligence

[![MIT License](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](apps/api)
[![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg)](apps/web)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](apps/api)
[![H3](https://img.shields.io/badge/Uber%20H3-Res%208-orange.svg)](apps/api)

> **Hackathon Submission:** Track 2 — Best Open-Source AI Project  
> **Problem Statement:** O3 — Trustworthy and Verifiable AI  
> **Repository:** [https://github.com/manya1106/DishaAI](https://github.com/manya1106/DishaAI)

---

## 1. Executive Summary

Retail and hospitality business owners typically choose commercial locations based on intuition, expensive brokers, or unverified generative AI chatbots that hallucinate plausible-sounding rent and footfall metrics.

**Disha AI** is an open-source, verifiable location intelligence platform that transforms open geospatial data into mathematically grounded site selection recommendations. Built from first principles to eradicate generative hallucinations, Disha AI decouples deterministic computation from natural language narration:

1. **Deterministic 9-Signal Engine:** Computes percentile-normalized relative rankings across urban cells using Uber H3 spatial indexing.
2. **Evidence-Grounded AI Narrator:** An open-weight language model explains the results, but **never** invents or calculates scores.
3. **V1–V9 Claim Verifier:** Every generated sentence is decomposed into claims and verified against raw data records before display.
4. **Transparent Provenance:** All metrics carry explicit classes (`measured`, `estimated`, `heuristic`, `unavailable`), refusing to fabricate private commercial leases or rupee figures.

---

## 2. Architecture & Data Flow

```text
 Browser: Next.js on Vercel   (/explore, /trust)
   Config: NEXT_PUBLIC_API_URL  (No secrets in client bundle)
        │
        ▼ HTTPS REST API (CORS enabled)
 FastAPI on Render
   ├── /health                              (Service & data health status)
   ├── /api/v1/meta                         (City bboxes, category taxonomies, default weights)
   ├── /api/v1/analyses                     (POST: compute 9-signal relative rankings)
   ├── /api/v1/analyses/{id}/locations/{id} (GET: single location report & evidence table)
   ├── /api/v1/analyses/{id}/compare        (POST: side-by-side location deltas)
   ├── /api/v1/analyses/{id}/chat           (POST: verified natural language narration)
   └── /api/v1/trust/stats                  (GET: live and adversarial evaluation metrics)
        │
        ├── In-Memory Snapshot Loader: 417 H3 Res-8 cells across Bengaluru (OpenStreetMap)
        ├── Deterministic Scoring Pipeline: 9 signals, relative percentiles, tie-breakers
        ├── Evidence Builder: Slim EvidenceBundle with stable aliases (ev_001...)
        └── AI Verification Engine:
              Prompt -> Open-Weight LLM -> Parse -> Verifier (V1–V9) -> Fallback Narrator
```

---

## 3. The Nine Location Signals

Scores are calculated as **relative percentiles (0 to 100)** across all eligible cells in the urban grid:

| # | Signal ID | Raw Input / Proxy | Direction | Provenance Class |
|---|---|---|---|---|
| 1 | `competition_density` | Count of direct competitor POIs in neighbourhood | Lower is better | `measured` |
| 2 | `gap_opportunity` | Demand proxy (anchors + residential) ÷ (competitors + 1) | Higher is better | `estimated` |
| 3 | `footfall_anchors` | Proximity to malls, colleges, tech parks, markets, hospitals | Higher is better | `estimated` |
| 4 | `transit_access` | Bus stop and metro entrance accessibility | Higher is better | `measured` |
| 5 | `complementary_mix` | Count of category-specific synergetic commercial venues | Higher is better | `measured` |
| 6 | `residential_catchment` | Mapped apartment buildings and residential landuse proxy | Higher is better | `estimated` |
| 7 | `daytime_population` | Offices, commercial buildings, and college daytime counts | Higher is better | `estimated` |
| 8 | `road_accessibility` | Primary/secondary road network length + junction count | Higher is better | `measured` |
| 9 | `rent_efficiency` | Heuristic rent tier (1-5) alignment with budget ceiling | Higher is better | `heuristic` |

---

## 4. The V1–V9 Claim Verification Pipeline

Before any natural language response reaches the user, it must pass 9 code-level verification rules:

* **V1 — Schema Validity:** Output strictly matches single-sentence block and claim schemas.
* **V2 — Evidence Citation:** Every claim must cite valid evidence IDs from the active bundle.
* **V3 — Numeric Consistency:** Numbers in text must match cited values within tolerance (0.15).
* **V4 — Entity Grounding:** All locations and ranks mentioned must exist in the analysis set.
* **V5 — Rank & Comparison Validity:** Recomputed deltas must match the claimed direction.
* **V6 — Polarity Consistency:** Strength claims require score >= 50.0; weaknesses <= 45.0.
* **V7 — Forbidden Topics:** Unsubstantiated currency (₹, INR), revenue, or profit figures are rejected.
* **V8 — Uncited Numbers:** Any sentence containing numbers without accompanying claims is excised.
* **V9 — Integrity Threshold:** If >50% of statements fail verification, degraded to deterministic fallback.

---

## 5. Measured Trust & Adversarial Evaluation

Tested against 21 adversarial cases (including speculative traps, hallucination lures, nonexistent locations, and prompt injection attempts):

| Metric | Target | Measured Result |
|---|---|---|
| **Leaked Unsupported Claims** | **0** | **0 (Zero leaks)** |
| **Speculative Trap Refusal Rate** | **>= 90%** | **100.0%** |
| **Answer Rate on Valid Qs** | **>= 90%** | **100.0%** |
| **P50 Latency (Local)** | **< 500 ms** | **< 10 ms** |
| **Deterministic Golden Match** | **100%** | **100% (Bit-for-bit identical)** |

---

## 6. Running Locally in < 5 Minutes

### Prerequisites
- Node.js 20+ and npm 10+
- Python 3.11+
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/manya1106/DishaAI.git
cd DishaAI
```

### Step 2: Start Backend (FastAPI)
```bash
cd apps/api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Backend is running at `http://localhost:8000` (Healthcheck: `http://localhost:8000/health`).*

### Step 3: Start Frontend (Next.js)
In a second terminal:
```bash
cd apps/web
npm install
npm run dev
```
*Frontend is running at `http://localhost:3000`.*

---

## 7. Running Tests & Evaluations

Run the full Python test suite (scoring, verifier V1-V9, integration):
```bash
cd apps/api && source .venv/bin/activate
pytest tests/ -v
ruff check .
```

Run the trust evaluation over the 21 adversarial cases:
```bash
python scripts/eval_trust.py
```

Run the production smoke test:
```bash
bash scripts/smoke_public.sh http://localhost:3000 http://localhost:8000
```

---

## 8. Deployment

- **Backend (Render):** Dockerfile provided at `apps/api/Dockerfile`. See [`docs/DEPLOY.md`](docs/DEPLOY.md) for step-by-step instructions.
- **Frontend (Vercel):** Native Next.js App Router deployment. Configure `NEXT_PUBLIC_API_URL` to point to the Render backend.

---

## 9. Data Attribution & License

- **Data Attribution:** Built on OpenStreetMap data: © OpenStreetMap contributors ([ODbL](https://www.openstreetmap.org/copyright)).
- **License:** Released under the [MIT License](LICENSE).
