# Disha AI — Build Status

**Last Updated:** Agent Swarm + Real-Data Postgres Foundation Complete (Phases 0–7 of `plan.md`)

### 1. What Currently Works
- **Agent Swarm (`apps/api/app/agents/`):**
  - **Orchestrator** — dispatches Scoring/Narrator/Verifier agents, logs every hand-off to an in-memory `TraceStore`.
  - **Scoring Agent** — wraps the deterministic 9-signal engine + data loader, unchanged internals.
  - **Narrator Agent** — wraps the LLM adapter + deterministic fallback narrator, unchanged internals.
  - **Verifier Agent** — wraps the evidence bundle builder + V1–V9 claim verifier, unchanged internals.
  - `ai/chat.py` sequences these three per request; trace exposed via `GET /api/v1/trust/agent-trace/{trace_id}` and a "Agent Trace" panel in the frontend chat UI.
- **PostgreSQL + PostGIS Data Layer (`apps/api/app/db/`):**
  - Docker container `disha_ai_postgres` running PostGIS 16-3.4, healthy on port 5432.
  - Alembic migration `426fd558779a` applied (`cities`, `h3_cells`, `pois`, `agent_runs`).
  - **Real OpenStreetMap data for all of Bengaluru** ingested via `scripts/ingest_osm_bengaluru.py`: 1,630 H3 res-8 cells (1,382 eligible), 36,411 real POIs with real `osm_id`s — not the old 417-cell synthetic-ish snapshot.
  - `DATA_MODE=postgres` switches the existing loader transparently; automatic fallback to the JSON snapshot if Postgres is unreachable.
  - A second, independent Phase D attempt (`person_D/`, Manya Kaushik — migrates the old snapshot into its own Postgres container) was reconciled in rather than discarded; not imported by the running app. See `PROJECT_STATE.md` §2.
- **FastAPI Backend (`apps/api`):**
  - `/health`, `/api/v1/meta`, `POST /api/v1/analyses`, `GET /api/v1/analyses/{id}/locations/{id}`, `POST /api/v1/analyses/{id}/compare`, `POST /api/v1/analyses/{id}/chat`, `GET /api/v1/trust/stats`, `GET /api/v1/trust/agent-trace/{trace_id}` — all unchanged in external contract except the last, which is new.
- **Deterministic 9-Signal Scoring Pipeline:** unchanged — percentile normalization, inverse ranking for competition, missing-data renormalisation, tie-breaking, golden reproducibility — now computed over real data.
- **AI Claim Verifier (Rules V1–V9):** unchanged — rejects ungrounded numbers, unknown locations, polarity mismatches, forbidden speculative currency figures; 100% refusal rate on speculative traps; now invoked via the Verifier Agent rather than called directly.
- **Next.js Frontend (`apps/web`):** unchanged in structure (landing `/`, `/explore`, `/trust`), plus the new Agent Trace toggle in the chat panel.
- **Testing & Quality:**
  - 37/37 backend tests passing (`pytest apps/api/tests/ -v`) — 12 new (agents), 25 pre-existing, against live Postgres data.
  - Codebase linted and clean (`ruff check apps/api/app person_D`).
  - Next.js production build succeeding (`npm run build`); `npm run lint` unchanged at 6 pre-existing errors, 1110 warnings.
  - 21/21 adversarial evaluation cases passing with 0 leaked unsupported claims, re-verified against real Postgres data.
- **Deployment Assets:** `apps/api/Dockerfile`, `scripts/smoke_public.sh`, `docs/DEPLOY.md`, `docs/DEMO.md` (updated for the agent-swarm/real-data demo script).

### 2. What Is Being Implemented / Deployment Status
- Public deployment linking on Vercel and Render — not started.

### 3. What Is Blocked
- None technically. One open decision: `person_D/`'s final disposition (keep dormant for reference, or remove) — a joint call with Manya, not made unilaterally.

### 4. What Remains Before Final Submission
1. Fix 6 pre-existing Next.js ESLint errors in `apps/web` (`npm run lint`).
2. Connect repository to Vercel (Frontend) and Render (Backend) per `docs/DEPLOY.md`.
3. Run `scripts/smoke_public.sh` against the live public URLs.
4. Enforce the already-configured chat rate limit (`RATE_LIMIT_CHAT_PER_MIN`) in `apps/api/app/routers/chat.py` — configured but not wired.
5. (Optional) Configure a hosted `LLM_API_KEY` (e.g. Groq) and verify the live LLM path end-to-end; currently only exercised via the deterministic fallback.
6. Decide `person_D/`'s fate with Manya.

### 5. Next Three Highest-Priority Actions
1. Fix the 6 frontend ESLint errors in `apps/web`.
2. Project owner links Render web service and Vercel project per `docs/DEPLOY.md`.
3. Verify public URLs with `scripts/smoke_public.sh`.
