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

- **Agent Swarm (`apps/api/app/agents/`):** Orchestrator, Scoring Agent, Narrator Agent, Verifier Agent — all built, wrapping pre-existing unchanged internals, all with dedicated tests. `ai/chat.py` sequences them per chat request and logs every hand-off; `GET /api/v1/trust/agent-trace/{trace_id}` and a frontend "Agent Trace" panel expose the sequence.
- **Data Layer (`apps/api/app/db/`):** PostGIS 16-3.4 container (`disha_ai_postgres`) healthy on port 5432. Alembic migration `426fd558779a` applied. **Real OpenStreetMap data for all of Bengaluru** ingested (`scripts/ingest_osm_bengaluru.py`): 1,630 H3 cells (1,382 eligible), 36,411 real POIs — not the old 417-cell synthetic-ish snapshot. `DATA_MODE=postgres` switches the loader transparently, with automatic JSON-snapshot fallback.
  - A second, independent Phase D attempt exists at `person_D/` (Manya Kaushik — migrates the *old* snapshot into its own Postgres container, not imported by `apps/api`). Reconciled in, not discarded; see `PROJECT_STATE.md` §2 and `progress.md` D-13. Its removal is an open joint decision.
- **Backend (`apps/api`):** FastAPI server, 37/37 passing pytest tests (12 new for agents, 25 pre-existing), 9-signal scoring engine unchanged, claim verifier (V1–V9) unchanged — now invoked via agents; 21/21 adversarial eval cases pass with **0 leaked claims** and **100% trap refusal rate**, re-verified against the real Postgres data.
- **Frontend (`apps/web`):** Unchanged structure (`/`, `/explore`, `/trust`), plus the new Agent Trace toggle in the Ask AI chat panel. `npm run build` green; `npm run lint` at the pre-existing 6 errors/1110 warnings baseline, unchanged.
- **Repository:** Remote tracked at `https://github.com/manya1106/DishaAI.git`. Tag `contracts-v1` frozen at `563ad6c`. `main` at `cc09b2e`.

---

## 3. What Remains Incomplete or Unverified

- **Public Hosting Deployment:** Code is ready via `apps/api/Dockerfile` (Render) and Next.js native build (Vercel). Public URLs are **UNVERIFIED** until the human owner links the GitHub repository on Render and Vercel dashboards. Once live, test with `bash scripts/smoke_public.sh <web_url> <api_url>`.
- **Chat rate limiting:** `RATE_LIMIT_CHAT_PER_MIN` is configured but not enforced in `apps/api/app/routers/chat.py`.
- **Live hosted LLM:** no `LLM_API_KEY` configured in this environment; only the deterministic fallback path has been exercised end-to-end.
- **Frontend ESLint:** 6 pre-existing errors not yet fixed (`MapComponent.tsx`, `explore/page.tsx`, `trust/page.tsx`).
- **`person_D/`'s fate:** keep dormant for reference, or remove — a decision for the project owner and Manya together.

---

## 4. Relevant File Map

| Purpose | Relevant Paths |
|---|---|
| **API Schemas & Contracts** | `apps/api/app/schemas/**`, `contracts/openapi.json`, `apps/web/src/types/api.ts` |
| **Agent Swarm** | `apps/api/app/agents/{contracts,orchestrator,scoring_agent,narrator_agent,verifier_agent}.py` |
| **Scoring Engine** | `apps/api/app/scoring/signals.py`, `engine.py`, `explain.py`, `configs/*.yaml` |
| **Geospatial Data (Postgres, active)** | `apps/api/app/db/{base,models}.py`, `apps/api/app/data/db_loader.py`, `scripts/ingest_osm_bengaluru.py`, `apps/api/migrations/` |
| **Geospatial Data (JSON fallback)** | `apps/api/app/data/loader.py`, `snapshots/blr.json`, `rent_tiers.csv` |
| **Geospatial Data (dormant, person_D's attempt)** | `person_D/**` — not imported by `apps/api`, see §2 above |
| **AI Verifier & Chat** | `apps/api/app/ai/verifier.py`, `chat.py`, `fallback.py`, `evidence.py`, `prompts.py` |
| **API Routers** | `apps/api/app/routers/health.py`, `meta.py`, `analyses.py`, `chat.py`, `trust.py` |
| **Frontend UI** | `apps/web/src/app/page.tsx`, `explore/page.tsx`, `trust/page.tsx`, `components/**` (incl. Agent Trace panel in `ChatPanel.tsx`) |
| **Tests & Evals** | `apps/api/tests/**` (incl. `tests/agents/`), `scripts/eval_trust.py`, `scripts/smoke_public.sh` |
| **Documentation** | `docs/DEPLOY.md`, `docs/DEMO.md`, `docs/BLUEPRINT.md`, `plan.md`, `progress.md`, `README.md` |

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
# Terminal 0: Postgres (first time: docker compose up -d from repo root)
docker compose ps   # confirm disha_ai_postgres is healthy

# Terminal 1: Backend (needs apps/api/.env with DATABASE_URL, DATA_MODE=postgres)
cd apps/api && uvicorn app.main:app --port 8000

# Terminal 2: Frontend
cd apps/web && npm run dev
```

If Postgres isn't running, the app still works — `DATA_MODE` falls back to the JSON snapshot automatically.

### To Verify Integrity
```bash
cd apps/api && python -m pytest tests/ -v && python -m ruff check app/ && cd ../.. && python scripts/eval_trust.py && cd apps/web && npm run build
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
