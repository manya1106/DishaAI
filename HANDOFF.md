# Disha AI — Agent & Conversation Handoff Guide

> **MANDATORY FOR NEXT AGENT OR NEW CONVERSATION:**  
> Read this document completely BEFORE taking any action or touching any files. Do NOT rebuild what already exists.

---

## 1. What to Read First (In Exact Order)
1. [`AGENTS.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/AGENTS.md) — Permanent project rules, file boundaries, and new-conversation protocol.
2. [`PROJECT_STATE.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/PROJECT_STATE.md) — Authoritative matrix of implemented, tested, and verified components.
3. [`STATUS.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/STATUS.md) — Immediate status dashboard, next priority actions, and blockers.
4. [`MANUAL_ACTIONS.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/MANUAL_ACTIONS.md) — Actions requiring human project owner intervention.
5. [`CHECKPOINTS.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/CHECKPOINTS.md) — Most recent verified checkpoint entry.

---

## 2. What Works & What Has Actually Been Verified

- **Data Layer (`person_D`):**
  - PostGIS 16-3.4 container (`disha_postgis`) healthy on port 5432.
  - Alembic migrations applied revision `001_initial_schema`.
  - Ingestion loaded 1 City (`blr`), 417 H3 Res-8 cells, and 2,592 POIs with spatial coordinates.
  - `DatabaseLoader` and `ScoringAgent` passing 3/3 dedicated pytest tests.
  - Bit-for-bit mathematical scoring parity verified against snapshot.
- **Backend (`apps/api`):** 
  - Complete FastAPI server running locally on Python 3.11 with 24 passing pytest tests.
  - 9-signal relative percentile scoring engine with tie-breaking and golden test reproducibility.
  - Snapshot loader serving 417 Bengaluru H3 cells from memory.
  - Claim verifier (Rules V1–V9) executing in pure code; 21/21 adversarial eval cases passed with **0 leaked claims** and **100% trap refusal rate**.
- **Frontend (`apps/web`):**
  - Next.js 16 App Router application compiling in <400ms without errors.
  - MapLibre GL map with Carto basemap and H3 hex choropleth layer (Worker loaded from `/maplibre-gl-worker.mjs`, verified end-to-end with zero console errors).
  - Numbered top 10 location markers synchronized with ranked card list.
  - Multi-tab right drawer with Location Report (9 signal bars, explicit provenance badges, raw OSM evidence table), Compare View (side-by-side signal deltas), and Ask AI (verified single-sentence blocks, claim chips, and evidence drawer).
  - `/trust` page displaying real evaluation statistics, V1–V9 pipeline rules, and data provenance guide.
- **Repository:**
  - Remote tracked at `https://github.com/manya1106/DishaAI.git`.
  - Tag `contracts-v1` frozen at `563ad6c`.
  - Working tree clean.

---

## 3. What Remains Incomplete or Unverified

- **Public Hosting Deployment:**
  - Code is ready for deployment via `apps/api/Dockerfile` (Render) and Next.js native build (Vercel).
  - Public URLs are **UNVERIFIED** until the human owner links the GitHub repository on Render and Vercel dashboards.
  - Once live, the public URLs must be tested with `bash scripts/smoke_public.sh <web_url> <api_url>`.

---

## 4. Relevant File Map

| Purpose | Relevant Paths |
|---|---|
| **API Schemas & Contracts** | `apps/api/app/schemas/**`, `contracts/openapi.json`, `apps/web/src/types/api.ts` |
| **Scoring Engine** | `apps/api/app/scoring/signals.py`, `engine.py`, `explain.py`, `configs/*.yaml` |
| **Geospatial Data** | `apps/api/app/data/loader.py`, `snapshots/blr.json`, `rent_tiers.csv` |
| **AI Verifier & Chat** | `apps/api/app/ai/verifier.py`, `chat.py`, `fallback.py`, `evidence.py`, `prompts.py` |
| **API Routers** | `apps/api/app/routers/health.py`, `meta.py`, `analyses.py`, `chat.py`, `trust.py` |
| **Frontend UI** | `apps/web/src/app/page.tsx`, `explore/page.tsx`, `trust/page.tsx`, `components/**` |
| **Tests & Evals** | `apps/api/tests/**`, `scripts/eval_trust.py`, `scripts/smoke_public.sh` |
| **Documentation** | `docs/DEPLOY.md`, `docs/DEMO.md`, `docs/BLUEPRINT.md`, `README.md` |

---

## 5. What MUST NOT Be Changed

1. **Do NOT edit `contracts/` or `apps/api/app/schemas/`** without an explicit architecture change request. These define the frozen API contract.
2. **Do NOT hand-edit `apps/web/src/types/api.ts`**. It is auto-generated via `npm run gen:types`.
3. **Do NOT replace deterministic scoring with LLM-based calculations**. Decoupling scoring from narration is the core requirement of O3.
4. **Do NOT introduce fake rupee rent numbers or unverified footfall predictions**. Provenance honesty is non-negotiable.
5. **Do NOT discard uncommitted changes or force-push Git history**.

---

## 6. What Command or Task to Execute Next

### To Run Locally
```bash
# Terminal 1: Backend
cd apps/api && source .venv/bin/activate && uvicorn app.main:app --port 8000

# Terminal 2: Frontend
cd apps/web && npm run dev
```

### To Verify Integrity
```bash
source apps/api/.venv/bin/activate && pytest apps/api/tests/ -v && ruff check apps/api/ && cd apps/web && npm run build
```

### To Execute Public Deployment Verification
Once human owner provides public URLs:
```bash
bash scripts/smoke_public.sh https://<vercel-domain>.vercel.app https://<render-domain>.onrender.com
```

---

## 7. Manual Action Required from Project Owner

See [`MANUAL_ACTIONS.md`](file:///Users/manyakaushik1106/Desktop/GITHUB/DISHA_AI/MANUAL_ACTIONS.md):
- Action #2: Connect Render Web Service for backend (`apps/api`).
- Action #3: Connect Vercel Project for frontend (`apps/web`).
