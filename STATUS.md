# Disha AI — Build Status

**Last Updated:** Phase D & Phase 2 Complete (PostGIS Data Foundation & Autonomous Scoring Agent)

### 1. What Currently Works
- **PostgreSQL + PostGIS Data Layer (`person_D`):**
  - Docker container `disha_postgis` running PostGIS 16-3.4 healthy on port 5432.
  - Alembic migrations applied revision `001_initial_schema` (`cities`, `h3_cells`, `pois`, `cell_signals`, `agent_runs`).
  - Ingestion script loaded 1 City (`blr`), 417 H3 Res-8 cells with GeoJSON polygon geometries, and 2,592 POIs with spatial coordinates.
  - `DatabaseLoader` with automatic fallback to JSON snapshot when DB is unavailable.
  - Bit-for-bit mathematical scoring parity verified against original snapshot.
- **Autonomous Scoring Agent (`person_D/scoring_agent.py`):**
  - Phase 2 agent wrapper executing deterministic scoring and building grounded evidence bundles.
  - Reproduces golden test rankings bit-for-bit.
- **FastAPI Backend (`apps/api`):**
  - `/health` endpoint returning system, data mode, db, and llm status.
  - `/api/v1/meta` serving city boundaries, category taxonomies, default weights, and attribution.
  - `POST /api/v1/analyses` computing 9-signal relative percentile rankings across 417 Bengaluru H3 cells.
  - `GET /api/v1/analyses/{id}/locations/{id}` serving detailed location reports with 9 signals and raw evidence items.
  - `POST /api/v1/analyses/{id}/compare` calculating per-signal score differentials and winning leaders.
  - `POST /api/v1/analyses/{id}/chat` orchestrating verified natural language explanations.
  - `GET /api/v1/trust/stats` serving live stats and latest adversarial evaluation run metrics.
- **Deterministic 9-Signal Scoring Pipeline:**
  - Percentile normalization (0-100), inverse ranking for competition, missing-data renormalisation, and tie-breaking.
  - Golden ranking test passing with bit-for-bit reproducibility.
- **AI Claim Verifier (Rules V1–V9):**
  - Rejects ungrounded numbers, unknown locations, polarity mismatches, and forbidden speculative currency figures.
  - Deterministic fallback narrator for offline or failed verification modes.
  - 100% refusal rate on speculative rupee rent / revenue traps.
- **Next.js Frontend (`apps/web`):**
  - Landing page (`/`) with problem statement O3 overview, trust pillars, and live metrics.
  - Interactive exploration page (`/explore`):
    - Top bar with city, category, and budget selectors + AI mode toggle.
    - MapLibre GL map with H3 hex choropleth heatmap and numbered markers (#1 to #10).
    - Ranked locations list with rank chips, score rings, and synchronized selection.
    - Report Drawer with 9 signal bars, explicit provenance badges, strengths, and raw evidence table.
    - Compare tab for 2-3 locations with per-signal winning badges.
    - Verified Ask AI chat with claim chips, verification badges, and click-to-open Evidence Drawer.
    - Data honesty footer banner with OSM attribution and simulated fixture tags.
  - Trust page (`/trust`) with evaluation results table, verification pipeline diagram, and limitations.
- **Testing & Quality:**
  - 3/3 `person_D` tests passing (`pytest person_D/tests/ -v`).
  - 24/24 backend tests passing (`pytest apps/api/tests/ -v`).
  - Codebase linted and clean (`ruff check person_D/ apps/api/`).
  - Next.js production build succeeding (`npm run build`).
  - MapLibre GL v6 worker loading verified end-to-end in browser with zero console errors.
  - 21/21 adversarial evaluation cases passing with 0 leaked unsupported claims.
- **Deployment Assets:**
  - `apps/api/Dockerfile` for containerized hosting.
  - `scripts/smoke_public.sh` automated production verification script.
  - `docs/DEPLOY.md` and `docs/DEMO.md`.

### 2. What Is Being Implemented / Deployment Status
- Public deployment linking on Vercel and Render.

### 3. What Is Blocked
- None.

### 4. What Remains Before Final Submission
1. Fix 6 Next.js ESLint errors in `apps/web` (`npm run lint`) to achieve clean frontend code quality.
2. Connect repository to Vercel (Frontend) and Render (Backend) per `docs/DEPLOY.md`.
3. Run `scripts/smoke_public.sh` against the live public URLs.
4. (Optional) Add in-memory rate limiting to `POST /api/v1/analyses/{id}/chat` and configure hosted `LLM_API_KEY`.

### 5. Next Three Highest-Priority Actions
1. Fix the 6 frontend ESLint errors in `apps/web` (TASK-01 in `docs/IMPLEMENTATION_AUDIT.md`).
2. Project owner links Render web service and Vercel project using instructions in `docs/DEPLOY.md` (TASK-02 & TASK-03).
3. Verify public URLs with automated smoke script `scripts/smoke_public.sh` (TASK-04).
