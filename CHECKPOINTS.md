# Disha AI — Chronological Checkpoint History

This document serves as an immutable, verifiable ledger of project milestones, tests executed, Git commits, and state transitions to ensure cross-conversation continuity.

---

## Checkpoint 001: Initial Bootstrap & Contract Freeze
- **Date & Time:** 2026-10-17 20:05 IST
- **Commit Hash:** `563ad6c`
- **Git Branch:** `main`
- **Git Tag:** `contracts-v1`
- **Working Tree:** Clean
- **Objectives:**
  - Initialize Git repository and link to `https://github.com/manya1106/DishaAI.git`.
  - Establish directory structure (`apps/web`, `apps/api`, `contracts`, `scripts`, `docs`).
  - Create Pydantic v2 schemas and export `contracts/openapi.json`.
  - Generate TypeScript API definitions (`apps/web/src/types/api.ts`).
  - Generate and validate 7 schema-compliant mock fixtures (`contracts/fixtures/`).
- **Commands Executed & Verified:**
  - `python scripts/export_openapi.py` (Generated 43KB OpenAPI spec).
  - `python scripts/generate_fixtures.py` (Produced 7 fixture files).
  - `python scripts/validate_fixtures.py` (All 7 fixtures passed schema validation).
  - `cd apps/web && npm run gen:types && npm run build` (Generated types and built default template).
- **Known Limitations at this Milestone:**
  - Endpoints were stubs returning 501 or mock fixtures.
  - No real scoring engine or AI verifier logic attached yet.
- **Handoff Target:** Milestone M1 & M2 (Engine and Verifier implementation).

---

## Checkpoint 002: Vertical Slice Implementation & Local Verification
- **Date & Time:** 2026-10-17 20:28 IST
- **Commit Hash:** `2747c50`
- **Git Branch:** `main`
- **Git Tag:** `contracts-v1` (ancestor)
- **Working Tree:** Clean
- **Objectives:**
  - Implement 9-signal pure functions, relative percentile normalisation, and tie-breaking engine.
  - Generate 417-cell Bengaluru H3 snapshot with POIs and heuristic rent tiers.
  - Implement V1–V9 claim verifier, deterministic fallback narrator, and chat orchestrator.
  - Build Next.js frontend pages (`/`, `/explore`, `/trust`) with MapLibre GL map, H3 choropleth heatmap layer, ranked cards, report drawer, compare view, and verified chat panel with claim chips.
  - Implement 21-case adversarial evaluation suite (`scripts/eval_trust.py`).
  - Create Dockerfile and `smoke_public.sh`.
- **Commands Executed & Verified:**
  - `pytest apps/api/tests/ -v` (24/24 tests passed in 0.27s).
  - `ruff check apps/api/` (All checks passed).
  - `python scripts/eval_trust.py` (21/21 cases passed, 0 leaked claims, 100% trap refusal).
  - `cd apps/web && npm run build` (Next.js compiled in 291ms).
  - `git push origin main` (Pushed to GitHub repository).
- **Known Limitations at this Milestone:**
  - Deployment to Render and Vercel remains unverified until public hosting projects are linked by human owner.
  - PostgreSQL (Neon) connection is optional; running in-memory trace store.
- **Handoff Target:** Cross-conversation persistence and deployment execution.

---

## Checkpoint 003: Checkpoint & Memory Architecture Established
- **Date & Time:** 2026-10-17 20:34 IST
- **Commit Hash:** `9e6b062` (and tracking `main`)
- **Git Branch:** `main`
- **Working Tree:** Clean (all memory and governance docs staged and committed)
- **Objectives:**
  - Establish cross-conversation memory protocol and handoff guides.
  - Record authoritative test verification logs.
  - Clarify manual human deployment actions.
- **Commands Executed & Verified:**
  - Pytest re-run: 24 passed in 0.32s.
  - Ruff check: All checks passed.
  - Web build: Next.js 16 compiled in 366ms.
  - Validate fixtures: 7/7 fixtures validated against schemas.
- **Handoff Target:** Public deployment linking on Render and Vercel.

---

## Checkpoint 004: MapLibre GL v6 Web Worker Loading & Map Lifecycle in Turbopack
- **Date & Time:** 2026-10-17 21:02 IST
- **Commit Hash:** `d5934e8` (and tracking `main`)
- **Git Branch:** `main`
- **Working Tree:** `apps/web/src/components/MapComponent.tsx`, `apps/web/package.json`, `apps/web/public/maplibre-gl-worker.mjs`, `PROJECT_STATE.md`, `STATUS.md`, `HANDOFF.md`
- **Root Cause Identified:**
  - In MapLibre GL v6, `defaultWorkerUrl()` uses relative path against `import.meta.url`. Under Next.js Turbopack, this resolved to `/_next/static/chunks/maplibre-gl-worker.mjs` which returned 404 Not Found.
  - Because vector tiles and GeoJSON require the web worker to decode, the worker error caused the map to remain blank white.
  - Additionally, markers and heatmap effects were firing before the map fired `"load"`, leaving `mapRef.current` null during initial render.
- **Fix Implemented:**
  - Worker file copied to `apps/web/public/maplibre-gl-worker.mjs` and configured via `maplibregl.config.WORKER_URL = "/maplibre-gl-worker.mjs"`.
  - Added `postinstall` cross-platform script in `apps/web/package.json` to keep worker synchronized.
  - Added `isMapLoaded` state in `MapComponent.tsx` to synchronize marker and heatmap rendering upon the `"load"` event.
- **Commands Executed & Verified:**
  - `cd apps/web && npm run build` (Static pages built cleanly in 1161ms).
  - Browser verification on `localhost:3000/explore`: Confirmed Carto basemap tiles, H3 hexagons, and numbered markers (#1–#10) render with 0 console errors.
  - `pytest apps/api/tests/ -v` (24/24 passed in 0.31s).
  - `ruff check apps/api/` (All checks passed).
  - `python scripts/eval_trust.py` (21/21 passed, 0 leaked claims).
- **Handoff Target:** Public cloud deployment linking on Render and Vercel.

---

## Checkpoint 005: Comprehensive Implementation Audit & Submission Readiness
- **Date & Time:** 2026-10-17 22:42 IST
- **Commit Hash:** `6673c1f` (and tracking `main`)
- **Git Branch:** `main`
- **Working Tree:** `docs/IMPLEMENTATION_AUDIT.md`, `CHECKPOINTS.md`, `STATUS.md`, `PROJECT_STATE.md`, `HANDOFF.md`
- **Audit Findings:**
  - 24/28 requirements **VERIFIED COMPLETE** (85.7%).
  - 1 requirement **IMPLEMENTED, NOT VERIFIED** (Hosted LLM live execution with Groq API key).
  - 2 requirements **PARTIALLY IMPLEMENTED** (Frontend ESLint cleanliness with 6 errors; chat rate limiting middleware).
  - 1 requirement **BLOCKED** on human manual action (Render and Vercel cloud project linking).
  - Map blank canvas and worker loading defects confirmed resolved via commit `d5934e8`.
  - Zero hardcoded API keys or secret leaks.
  - Overall weighted completion: **93.0%**.
- **Next Priority Action:** Fix 6 ESLint errors in `apps/web` (TASK-01) and link cloud deployment dashboards (TASK-02, TASK-03).

---

## Checkpoint 006: Local PostgreSQL + PostGIS Foundation & Scoring Agent (Phase D & Phase 2)
- **Date & Time:** 2026-10-18 11:05 IST
- **Commit Hash:** `7a130c7`
- **Git Branch:** `main`
- **Working Tree:** `person_D/**`, `progress.md`, `PROJECT_STATE.md`, `STATUS.md`, `HANDOFF.md`, `CHECKPOINTS.md`
- **Objectives:**
  - Stand up local PostgreSQL 16 + PostGIS 3.4 container (`disha_postgis` on port 5432).
  - Setup SQLAlchemy 2.0 (asyncpg/psycopg) and Alembic migrations.
  - Implement DDL for `cities`, `h3_cells`, `pois`, `cell_signals`, `agent_runs`.
  - Ingest 417 Bengaluru H3 cells and 2,592 POIs into spatial tables idempotently.
  - Implement `DatabaseLoader` in `person_D/loader.py` with snapshot fallback.
  - Implement Autonomous `ScoringAgent` in `person_D/scoring_agent.py` for Phase 2.
- **Commands Executed & Verified:**
  - `cd person_D && docker compose up -d` (Container `disha_postgis` healthy).
  - `alembic upgrade head` (Applied revision `001_initial_schema`).
  - `python person_D/scripts/load_snapshot_to_db.py` (Migrated 1 city, 417 cells, 2592 POIs).
  - `python person_D/scripts/verify_db.py` (Passed all PostGIS geometry and health checks).
  - `PYTHONPATH=. pytest person_D/tests/ -v` (3/3 tests passed in 2.98s).
  - `pytest apps/api/tests/ -v` (24/24 tests passed in 0.30s).
  - `python scripts/eval_trust.py` (21/21 adversarial cases passed, 0 leaked claims).
  - `ruff check person_D/ apps/api/` (All checks passed).
  - `cd apps/web && npm run build` (Next.js compiled in 408ms).
- **Handoff Target:** Person M (Multi-Agent framework: Orchestrator, Narrator, Verifier, and wiring).

---

## Checkpoint 007: Reconciliation of independent parallel work (branch divergence)

- **Date & Time:** 2026-10-18
- **Commit Hash:** this merge commit
- **Git Branch:** `main`
- **Context:** Checkpoint 006 above (`person_D/`, Manya Kaushik) was pushed to `origin/main` independently of, and concurrently with, a separately-integrated Phase D/2 implementation and a full Phase 0/1/3/4/5/6/7 agent-swarm build (Orchestrator, Narrator Agent, Verifier Agent, Scoring Agent) done in this working tree. `main` and `origin/main` had diverged (7 local commits vs. 1 remote commit).
- **What each side had:**
  - `origin/main` (`person_D/`, Checkpoint 006): migrates the existing 417-cell JSON snapshot into Postgres; standalone, not imported by `apps/api`.
  - This tree: real OSM data for all of Bengaluru (1,630 H3 cells, 1,382 eligible, 36,411 POIs) ingested into `apps/api/app/db/`, actually wired into the running app via `DATA_MODE=postgres`; plus the full agent swarm with an observability route/panel.
- **Resolution:** Merged `origin/main` in (commit `17564a5` preserved in history, Manya's authorship intact — not discarded). Kept the integrated, real-data implementation as the active one. `person_D/` remains in the tree, dormant, not imported anywhere; its removal is left as a joint decision, not made unilaterally here. Full details in `progress.md` Decision Log entry D-13.
- **Verified after merge:** 37/37 backend tests, 21/21 adversarial eval (0 leaked claims), ruff clean, `npm run build` green.
- **Known issue carried over, not yet fixed in `person_D/`:** `person_D/loader.py`'s `asyncio.run()` call would raise inside FastAPI's already-running event loop and get silently swallowed by a broad `except Exception  # noqa: BLE001` — the same bug this session's `apps/api/app/data/db_loader.py` hit and fixed via a thread-pool bridge. Worth fixing in `person_D/` too if it stays in use.
- **Next Priority Action:** Phase 8 — rewrite `PROJECT_STATE.md`, `STATUS.md`, `HANDOFF.md`, `docs/DEMO.md` to describe the reconciled, finished system (currently flagged stale at the top of each rather than rewritten, to keep this checkpoint's scope to reconciliation only). Decide `person_D/`'s fate with Manya.


