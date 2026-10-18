# Disha AI — Authoritative Project State

**Repository:** `https://github.com/manya1106/DishaAI.git`  
**Current Branch:** `main`  
**Current HEAD Commit:** `0f06e7b` (tracking `main`)  
**Latest Git Tag:** `contracts-v1` (at `563ad6c`)  
**Working Tree Status:** Clean  
**Inspection Date:** 2026-10-18  

---

## 1. Feature Status Matrix

| Component | Feature | Status | Verification Evidence / Command | Notes |
|---|---|---|---|---|
| **Contracts** | Pydantic v2 schemas (`apps/api/app/schemas/`) | **Verified end-to-end** | `python scripts/validate_fixtures.py` passed all 7 fixtures | Single source of truth |
| **Contracts** | OpenAPI specification (`contracts/openapi.json`) | **Verified end-to-end** | `python scripts/export_openapi.py` generated 43KB spec | Committed & tracked |
| **Contracts** | TypeScript API types (`apps/web/src/types/api.ts`) | **Verified end-to-end** | `npm run gen:types` in `apps/web` | Generated, never hand-edited |
| **Data Layer** | PostgreSQL + PostGIS Container | **Verified end-to-end** | Docker `postgis/postgis:16-3.4` healthy on port 5432 | Port 5432, PostGIS 3.4.3 extension |
| **Data Layer** | Alembic PostGIS Migrations | **Verified end-to-end** | `alembic upgrade head` applied revision `001_initial_schema` | cities, h3_cells, pois, cell_signals, agent_runs |
| **Data Layer** | Ingestion & Idempotency | **Verified end-to-end** | `pytest person_D/tests/test_db_idempotency.py` passed | 1 city, 417 H3 cells, 2592 POIs with spatial geom |
| **Data Layer** | DB Scoring Parity | **Verified end-to-end** | `pytest person_D/tests/test_db_scoring_parity.py` passed | Bit-for-bit identical golden scores to JSON snapshot |
| **Agent Swarm** | Autonomous Scoring Agent | **Verified end-to-end** | `pytest person_D/tests/test_scoring_agent.py` passed | Wraps engine & DB loader, returns evidence bundle |
| **Backend** | System Healthcheck (`GET /health`) | **Verified end-to-end** | `pytest tests/api/test_integration.py` (`test_health_endpoint`) | Reports status, version, data_mode, db, llm |
| **Backend** | Metadata Endpoint (`GET /api/v1/meta`) | **Verified end-to-end** | `pytest tests/api/test_integration.py` (`test_meta_endpoint`) | Cities, categories, budget tiers, signals, weights |
| **Backend** | Snapshot Data (`417 H3 Res 8 cells`) | **Verified end-to-end** | Loaded at boot via `apps/api/app/data/loader.py` | Built from OSM grid for central Bengaluru |
| **Backend** | 9-Signal Scoring Pipeline | **Verified end-to-end** | 8 scoring unit tests passed in 0.16s | Pure functions, percentile ranks, tie-breaks |
| **Backend** | Golden Ranking Reproducibility | **Verified end-to-end** | `test_golden.py` identical bit-for-bit runs | Cafe/Medium top 10 deterministic |
| **Backend** | Missing Data Renormalisation | **Verified end-to-end** | `test_missing.py` passed | Renormalises available weights to 100% |
| **Backend** | Analysis Endpoint (`POST /analyses`) | **Verified end-to-end** | `test_analyses_crud_flow` passed | Returns 10 ranked zones + GeoJSON heatmap |
| **Backend** | Report Endpoint (`GET /analyses/{id}/locations/{id}`) | **Verified end-to-end** | `test_analyses_crud_flow` passed | Returns 9 signal bars + raw OSM evidence rows |
| **Backend** | Compare Endpoint (`POST /analyses/{id}/compare`) | **Verified end-to-end** | `test_analyses_crud_flow` passed | Calculates per-signal deltas & winning badges |
| **AI & Trust** | Evidence Bundle Builder (`ev_001` aliases) | **Verified end-to-end** | Grounded in `apps/api/app/ai/evidence.py` | Extracts numbers, locations, allowed sets |
| **AI & Trust** | Claim Verifier Rules V1–V9 | **Verified end-to-end** | 9 verifier table tests passed in 0.05s | Code-level deterministic rules |
| **AI & Trust** | Speculative Trap Refusal | **Verified end-to-end** | `test_trap_question_refusal` passed | Returns `refused_insufficient_data` on rupee rent |
| **AI & Trust** | Deterministic Fallback Narrator | **Verified end-to-end** | `test_deterministic_mode_flow` passed | Verified blocks with claims and evidence IDs |
| **AI & Trust** | Adversarial Trust Evaluation | **Verified end-to-end** | `python scripts/eval_trust.py` (21/21 cases passed) | **0 leaked claims**, 100% trap refusal |
| **Frontend** | Landing Page (`/`) | **Tested** | `npm run build` compiled 6 static pages | Hero, 3 trust pillars, live eval metrics |
| **Frontend** | Explore Map (`/explore`) | **Verified end-to-end** | Browser verified with live backend | Selectors, MapLibre GL, ranked list, drawer, verified chat |
| **Frontend** | MapLibre H3 Choropleth + Numbered Markers | **Verified end-to-end** | Verified in browser (no console errors) | Carto basemap tiles, H3 hex fills, #1-#10 markers, click-to-fly |
| **Frontend** | Location Report Drawer | **Tested** | LocationReport component with 9 signal bars | Provenance tags (`measured`, `estimated`, `heuristic`) |
| **Frontend** | Compare View | **Tested** | CompareView component | Side-by-side deltas & winning leader pills |
| **Frontend** | Verified Ask AI Chat Panel | **Tested** | ChatPanel component | Claim chips, evidence drawer, refusal banner |
| **Frontend** | Trust Page (`/trust`) | **Tested** | `npm run build` compiled cleanly | Pipeline diagram, evaluation results, limitations |
| **Deployment** | Backend Dockerfile | **Implemented** | `apps/api/Dockerfile` present | Multi-stage slim Python 3.11 build |
| **Deployment** | Public Smoke Script | **Implemented** | `scripts/smoke_public.sh` executable | Health, meta, analysis, CORS, secret scan |
| **Deployment** | Render Web Service | **Unverified** | Awaiting manual project link on Render dashboard | Documented in `docs/DEPLOY.md` |
| **Deployment** | Vercel Web Deployment | **Unverified** | Awaiting manual project link on Vercel dashboard | Documented in `docs/DEPLOY.md` |

---

## 2. Verified Test Execution Log (Most Recent Real Run)

Run Command: `source apps/api/.venv/bin/activate && pytest apps/api/tests/ -v && ruff check apps/api/ && cd apps/web && npm run build`  
Executed At: 2026-10-17 20:33:15 IST  
Result: **100% PASSED**

### Pytest Breakdown (24/24 Passed in 0.32s)
```text
apps/api/tests/ai/test_chat_flow.py::test_trap_question_refusal PASSED
apps/api/tests/ai/test_chat_flow.py::test_deterministic_mode_flow PASSED
apps/api/tests/ai/test_chat_flow.py::test_compare_intent_flow PASSED
apps/api/tests/ai/test_verifier.py::test_v1_empty_output_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v2_unknown_evidence_id_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v3_invented_number_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v4_unknown_rank_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v5_contradictory_comparison_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v6_polarity_strength_on_weak_signal_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v7_forbidden_rupee_currency_fails PASSED
apps/api/tests/ai/test_verifier.py::test_v8_uncited_numbers_fails PASSED
apps/api/tests/ai/test_verifier.py::test_valid_response_passes PASSED
apps/api/tests/api/test_integration.py::test_health_endpoint PASSED
apps/api/tests/api/test_integration.py::test_meta_endpoint PASSED
apps/api/tests/api/test_integration.py::test_analyses_crud_flow PASSED
apps/api/tests/api/test_integration.py::test_trust_stats_endpoint PASSED
apps/api/tests/scoring/test_golden.py::test_golden_ranking_reproducibility PASSED
apps/api/tests/scoring/test_missing.py::test_missing_data_renormalisation PASSED
apps/api/tests/scoring/test_normalise.py::test_percentile_normalisation_ordering PASSED
apps/api/tests/scoring/test_normalise.py::test_percentile_normalisation_inversion PASSED
apps/api/tests/scoring/test_normalise.py::test_percentile_ties_receive_average PASSED
apps/api/tests/scoring/test_signals.py::test_competition_density PASSED
apps/api/tests/scoring/test_signals.py::test_gap_opportunity PASSED
apps/api/tests/scoring/test_rent_efficiency PASSED
```

### Ruff Linter Check
- Output: `All checks passed!`

### Next.js Production Build
- Route (app):
  - `○ /` (Static)
  - `○ /_not-found` (Static)
  - `○ /explore` (Static)
  - `○ /trust` (Static)
- Output: `✓ Compiled successfully in 366ms`

---

## 3. Known Limitations & Technical Constraints

1. **Relative Scores, Not Outcome Guarantees**: Scores represent relative percentile standings across the 417 eligible H3 cells in Bengaluru for that specific business category and budget tier. They do not predict rupee revenues or business survival probabilities.
2. **OpenStreetMap Coverage Density**: Coverage in certain outer ring areas is thinner than in CBD cores (e.g. Indiranagar, Koramangala). Low-coverage areas are honestly tagged with `medium` or `low` confidence.
3. **Rent Representation**: Rent is strictly a team-assigned heuristic tier (1 to 5) with an explicit `heuristic` provenance badge. Disha AI explicitly refuses to scrape or fabricate private rupee lease agreements.
4. **Hosted LLM Dependency**: If no `LLM_API_KEY` is provided, the system gracefully falls back to the built-in deterministic narrator (`ChatMode.DETERMINISTIC_FALLBACK` or `DETERMINISTIC_REQUESTED`), preserving 100% functionality.
5. **Database Readiness**: Traces are buffered in-memory (last 200). Connecting PostgreSQL (Neon) is supported via `DATABASE_URL` but is optional and never blocks startup or analysis paths.
