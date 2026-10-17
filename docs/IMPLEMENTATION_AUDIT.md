# Disha AI — Comprehensive Implementation Audit & Submission Readiness

**Audit Date:** 2026-10-17  
**Auditor:** Lead Engineer  
**Repository:** `https://github.com/manya1106/DishaAI.git`  
**Git Branch:** `main`  
**Current HEAD Commit:** `dd1cc1b`  
**Latest Git Tag:** `contracts-v1` (at `563ad6c`)  
**Working Tree Status:** Clean  
**Track:** Track 2 — Best Open-Source AI Project  
**Problem Statement:** O3 — Trustworthy and Verifiable AI  

---

## 1. Executive Summary

A comprehensive, evidence-based audit was conducted across the entire Disha AI codebase, including the FastAPI backend, pure-Python deterministic 9-signal scoring engine, V1–V9 claim verification engine, Next.js 16 frontend, OpenStreetMap data snapshot, automated test suites, and deployment assets.

### High-Level Verdict
- **Core Architecture & Problem Statement O3 Compliance:** **VERIFIED COMPLETE**.
  - Scoring is decoupled completely from LLM narration.
  - Scores are bit-for-bit reproducible (`test_golden.py`).
  - Claim verifier rules V1–V9 execute in pure Python; 21/21 adversarial test cases passed with **0 leaked claims** and **100% trap refusal rate** on speculative financial figures.
- **Backend Functionality:** **VERIFIED COMPLETE** (24/24 unit & integration tests passing in 0.31s; all 7 contract fixtures valid; all REST endpoints functional).
- **Frontend Map & UI:** **VERIFIED COMPLETE** with recent fix. The previous blank white map canvas and Turbopack Web Worker error have been diagnosed and resolved via commit `d5934e8`. The MapLibre map renders Carto tiles, H3 hex heatmap layers, and interactive #1–#10 markers with zero console errors.
- **Frontend Code Quality:** **PARTIALLY IMPLEMENTED**. While `npm run build` compiles 6 static pages cleanly in ~1.1s, `npm run lint` identifies 6 ESLint errors (synchronous `setState` in effects and `any` types).
- **Public Cloud Deployment:** **BLOCKED ON MANUAL ACTION**. Deployment configurations (`Dockerfile`, `docs/DEPLOY.md`, `smoke_public.sh`) are complete, but public hosting on Render and Vercel requires the project owner to link the GitHub repository in the cloud dashboards.

---

## 2. Audit Scope & Exact Commands Executed

Every claim in this audit was verified by running commands directly on the environment:

| Category | Command Executed | Real Outcome | Evidence Reference |
|---|---|---|---|
| **Git Baseline** | `git status && git branch -a && git log -n 5 --oneline && git tag -l` | Clean working tree; `main` tracking `origin/main`; tag `contracts-v1` verified | Terminal stdout |
| **Backend Tests** | `source apps/api/.venv/bin/activate && pytest apps/api/tests/ -v` | **24 passed in 0.31s** (0 failures, 1 warning) | Pytest stdout |
| **Backend Linter** | `ruff check apps/api/` | **All checks passed!** (0 errors) | Ruff stdout |
| **Fixture Validation** | `python scripts/validate_fixtures.py` | **7/7 fixtures validated** against Pydantic schemas | Script stdout |
| **Trust Evaluation** | `python scripts/eval_trust.py` | **21/21 cases passed**, 0 leaked claims, 100% refusal rate | Latest run JSON |
| **API Health & Meta** | `curl -s http://localhost:8000/health` & `/api/v1/meta` | Both returned HTTP 200 with schema-compliant payloads | Terminal stdout |
| **Scoring & Compare** | `curl -X POST http://localhost:8000/api/v1/analyses` & `.../compare` | Top 10 zones calculated; 9 signals; deltas evaluated | Terminal stdout |
| **Verified Chat Refusal** | `curl -X POST http://localhost:8000/api/v1/analyses/{id}/chat` | Rupee rent query rejected with `refused_insufficient_data` | Terminal stdout |
| **Smoke Suite** | `bash scripts/smoke_public.sh http://localhost:3000 http://localhost:8000` | **6/6 smoke checks passed** | Smoke script stdout |
| **Frontend Routes** | `curl http://localhost:3000/`, `/explore`, `/trust` | All 3 pages returned HTTP 200 (HTML > 20KB each) | Terminal stdout |
| **Worker File Serving** | `curl -I http://localhost:3000/maplibre-gl-worker.mjs` | **HTTP 200 OK** (Content-Length: 508,314 bytes) | HTTP header stdout |
| **Frontend Build** | `cd apps/web && npm run build` | **Compiled successfully in 1161ms** (6 static pages) | Next.js build stdout |
| **Frontend Linter** | `cd apps/web && npm run lint` | **Failed with 6 errors**, 1110 warnings | ESLint stdout |
| **Secret Scan** | `git grep -i -E "api_key\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]"` | **0 secrets detected** across all tracked files | Git grep stdout |

---

## 3. Requirement-by-Requirement Status Table

Strict Status Labels:
- `VERIFIED COMPLETE`: Implementation inspected and required behavior successfully tested.
- `IMPLEMENTED, NOT VERIFIED`: Code exists, but required behavior has not been confirmed.
- `PARTIALLY IMPLEMENTED`: Some requirements work, others are missing or broken.
- `NOT IMPLEMENTED`: The required functionality is absent.
- `BLOCKED`: Verification or implementation requires a missing external action or credential.
- `NOT APPLICABLE`: Not applicable to this architecture.

| # | Requirement / Component | Blueprint / Contract Spec | Status | Verification Evidence & Notes |
|---|---|---|---|---|
| **1** | **Frozen Contracts & Schemas** | Pydantic v2 schemas (`apps/api/app/schemas/`), `contracts/openapi.json` | **VERIFIED COMPLETE** | `scripts/validate_fixtures.py` verified 7/7 fixtures; OpenAPI spec generated. |
| **2** | **Generated TypeScript Types** | `apps/web/src/types/api.ts` | **VERIFIED COMPLETE** | Generated from OpenAPI spec via `npm run gen:types`. |
| **3** | **FastAPI Core & Lifespan** | Health check, CORS, lifespan, request ID middleware | **VERIFIED COMPLETE** | `GET /health` returned `{"status":"ok",...}`. Request IDs injected in headers. |
| **4** | **Bengaluru Geospatial Dataset** | 417 H3 Resolution-8 cells covering central Bengaluru with POIs | **VERIFIED COMPLETE** | `snapshots/blr.json` loaded at boot; 417 cells with real features. |
| **5** | **9-Signal Deterministic Pipeline** | 9 signals (competition, gap, anchors, transit, mix, residential, daytime, road, rent) | **VERIFIED COMPLETE** | 8 scoring unit tests passed in 0.16s (`test_signals.py`, `test_normalise.py`). |
| **6** | **Golden Ranking Reproducibility** | Bit-for-bit identical ranking across runs | **VERIFIED COMPLETE** | `test_golden.py` passed with exact score assertions. |
| **7** | **Missing Data Renormalisation** | Graceful weight adjustment when signals are unavailable | **VERIFIED COMPLETE** | `test_missing.py` passed; weights renormalise to 100%. |
| **8** | **Analysis Creation Endpoint** | `POST /api/v1/analyses` returning top 10 zones + GeoJSON heatmap | **VERIFIED COMPLETE** | Verified via curl and pytest; returns 10 locations with 9 signals and polygon boundaries. |
| **9** | **Location Report Endpoint** | `GET /api/v1/analyses/{id}/locations/{id}` | **VERIFIED COMPLETE** | Verified via curl; returns 9 signal bars and 9 raw OSM evidence items with explicit provenance. |
| **10** | **Location Comparison Endpoint** | `POST /api/v1/analyses/{id}/compare` | **VERIFIED COMPLETE** | Verified via curl; returns side-by-side scores, leader pills, and delta explanations. |
| **11** | **Stateless Analysis Token** | Base64url encoded `analysis_id` allowing cold-start recomputation | **VERIFIED COMPLETE** | Any endpoint recomputes instantaneously from token without database dependency. |
| **12** | **Evidence Bundle Construction** | Strict grounding dictionary with entity & numeric lookups | **VERIFIED COMPLETE** | `apps/api/app/ai/evidence.py` verified; extracts allowed numbers and evidence IDs. |
| **13** | **Verifier Rules V1–V9** | Sentence-to-claim schema, numeric matching, polarity, topics | **VERIFIED COMPLETE** | `test_verifier.py` passed 9 verifier table tests in 0.05s. |
| **14** | **Speculative Trap Refusal** | 100% rejection of rupee rent / revenue hallucinations | **VERIFIED COMPLETE** | `test_trap_question_refusal` passed; returns `refused_insufficient_data`. |
| **15** | **Deterministic Fallback Narrator** | Offline template generation when LLM is unconfigured or fails | **VERIFIED COMPLETE** | `test_deterministic_mode_flow` passed; generated grounded single-sentence blocks. |
| **16** | **Adversarial Trust Evaluation** | 21-case adversarial test suite (`scripts/eval_trust.py`) | **VERIFIED COMPLETE** | 21/21 passed, 0 leaked unsupported claims, 100% trap refusal. |
| **17** | **Hosted LLM Live Execution** | Live hosted open-weight model (`llama-3.1-8b-instant`) | **IMPLEMENTED, NOT VERIFIED** | Adapter code is complete; unverified live because `LLM_API_KEY` is not configured locally (system operates in deterministic fallback mode). |
| **18** | **API Rate Limiting** | Enforce request limits on chat endpoint | **PARTIALLY IMPLEMENTED** | `RATE_LIMIT_CHAT_PER_MIN: 20` defined in config, but enforcement middleware not wired in router. |
| **19** | **Landing Page (`/`)** | Hero, trust pillars, live eval metrics | **VERIFIED COMPLETE** | HTTP 200, static export compiled in 366ms, verified structure. |
| **20** | **Explore Page Controls** | City, Category, Budget Tier dropdowns, AI toggle | **VERIFIED COMPLETE** | Verified via browser and DOM; triggers interactive recomputation. |
| **21** | **MapLibre Basemap & H3 Heatmap** | Carto Positron basemap + H3 choropleth layer | **VERIFIED COMPLETE** | Worker bundling fixed in `d5934e8`; canvas and tiles verified live in browser. |
| **22** | **Ranked Location Markers (#1–#10)** | Numbered gradient marker pills synchronized with list | **VERIFIED COMPLETE** | Verified in browser screenshot; click synchronizes camera `flyTo`. |
| **23** | **Location Report Drawer** | 9 signal bars, explicit provenance badges, raw evidence | **VERIFIED COMPLETE** | Verified in browser screenshot; displays weights and contribution points. |
| **24** | **Compare View UI** | Multi-location selector and side-by-side signal delta bars | **VERIFIED COMPLETE** | Verified via DOM and API flow. |
| **25** | **Verified Ask AI Chat UI** | Block sentences, claim chips, evidence drawer link | **VERIFIED COMPLETE** | Verified via API chat integration and browser DOM. |
| **26** | **Trust Page (`/trust`)** | V1–V9 rules, evaluation metrics table, provenance guide | **VERIFIED COMPLETE** | HTTP 200, static export compiled cleanly. |
| **27** | **Frontend ESLint Cleanliness** | `npm run lint` clean run | **PARTIALLY IMPLEMENTED** | 6 errors reported: synchronous `setState` in effects and `any` types. |
| **28** | **Public Deployment (Render & Vercel)** | Live public HTTPS endpoints | **BLOCKED** | Deployment assets ready; blocked on manual account linking by human owner. |

---

## 4. Investigation of the Two Observed Defects

### Defect 1: Map Area Blank White
- **Status**: **RESOLVED & VERIFIED COMPLETE** (Commit `d5934e8`).
- **Root Cause**:
  1. MapLibre GL v6 uses `defaultWorkerUrl()` which calculates the worker path relative to `import.meta.url`.
  2. Next.js 16 with Turbopack bundled the module into a chunk directory. The browser looked for `http://localhost:3000/_next/static/chunks/maplibre-gl-worker.mjs`, which returned `404 Not Found`.
  3. Because vector tile decoding and GeoJSON polygon indexing require the Web Worker, the worker failure prevented tiles from rendering, leaving the canvas blank white.
  4. In addition, `mapRef.current` was assigned strictly inside `map.on("load", ...)`. Because the worker never loaded, the `"load"` event never fired, causing marker rendering effects to return early.
- **Fix Applied**:
  - Worker file copied to `apps/web/public/maplibre-gl-worker.mjs` and configured via `maplibregl.config.WORKER_URL = "/maplibre-gl-worker.mjs"`.
  - Added a cross-platform `postinstall` script in `package.json` to keep the public worker file synchronized.
  - Added `isMapLoaded` state in `MapComponent.tsx` to properly synchronize marker and heatmap rendering upon the `"load"` event.
- **Evidence**: Verified in live browser (`explore_verified_1792251006887.png`). Basemap tiles, H3 hexagons, and #1–#10 markers render with 0 console errors.

### Defect 2: "Worker failed to load. Check that the worker URL is correct."
- **Status**: **RESOLVED & VERIFIED COMPLETE** (Commit `d5934e8`).
- **Root Cause**: Direct symptom of Defect 1. MapLibre GL JS caught the Web Worker load failure and threw this exact error message in `WorkerPool.acquire`.
- **Fix Applied**: Same as Defect 1. Local worker is now served with HTTP 200 and Content-Type `application/javascript; charset=UTF-8`.
- **Evidence**: Inspected console logs on `localhost:3000/explore`; the worker error is completely gone.

---

## 5. Missing Functionality & Incomplete Requirements

1. **Frontend Linting Errors (6 Errors in `apps/web`)**:
   - `apps/web/src/components/MapComponent.tsx`: `renderHeatmapLayer` declared after use (`react-hooks/immutability`); 2 `any` type casts on GeoJSON setData.
   - `apps/web/src/app/explore/page.tsx`: synchronous `setState` inside `useEffect` during URL param sync; 1 `any` type cast.
   - `apps/web/src/app/trust/page.tsx`: synchronous `setState` inside `useEffect`.
2. **API Rate Limiting Enforcement**:
   - `RATE_LIMIT_CHAT_PER_MIN: 20` is configured in `apps/api/app/config.py`, but no middleware or dependency in `apps/api/app/routers/chat.py` currently throttles incoming requests.
3. **Public Deployment Verification**:
   - Public URLs on Render and Vercel are not yet active; awaiting project owner account setup.

---

## 6. Data Integrity & Trustworthy-AI Compliance (Problem Statement O3)

| O3 Requirement | Disha AI Implementation | Compliance Status |
|---|---|---|
| **Decoupled Scoring** | Pure Python math functions in `apps/api/app/scoring/signals.py`. LLM is not in the calculation loop. | **100% Compliant** |
| **Data Honesty & Provenance** | Every signal carries an explicit tag (`measured`, `estimated`, `heuristic`). Zero fake rupee lease agreements or fabricated footfall counts. | **100% Compliant** |
| **Deterministic Fallback** | When AI is disabled, offline, times out, or fails verification, system returns deterministic single-sentence blocks with citations. | **100% Compliant** |
| **Verifier Rules V1–V9** | Pure-code verifier checks schema, evidence IDs, number tolerances, entity names, ranks, strengths/weaknesses, and forbidden currency terms. | **100% Compliant** |
| **Refusal of Traps** | Refuses to estimate speculative rupee figures or out-of-scope regions with `refused_insufficient_data`. | **100% Compliant** (21/21 eval cases passed) |
| **Open-Weight Architecture** | Configured for `llama-3.1-8b-instant` via Groq/OpenAI-compatible adapter. | **100% Compliant** |

---

## 7. Prioritized Implementation Backlog

| Task ID | Priority | Description | Affected Files | Dependencies | Acceptance Criteria | Est. Effort | Manual Action? |
|---|---|---|---|---|---|---|---|
| **TASK-01** | **P1** | Fix 6 Next.js ESLint errors in `apps/web` | `apps/web/src/components/MapComponent.tsx`, `apps/web/src/app/explore/page.tsx`, `apps/web/src/app/trust/page.tsx` | None | `cd apps/web && npm run lint` passes with 0 errors | 15 mins | No |
| **TASK-02** | **P1** | Connect and deploy backend to Render | `apps/api/`, Render Dashboard | Human owner account | `curl https://<render-service>.onrender.com/health` returns HTTP 200 `status: ok` | 20 mins | **Yes** (Owner) |
| **TASK-03** | **P1** | Connect and deploy frontend to Vercel | `apps/web/`, Vercel Dashboard | TASK-02 (Render URL) | Vercel domain loads `/explore` and communicates with Render API | 15 mins | **Yes** (Owner) |
| **TASK-04** | **P1** | Run production smoke verification script | `scripts/smoke_public.sh` | TASK-02, TASK-03 | `bash scripts/smoke_public.sh <vercel_url> <render_url>` passes all 6 checks | 10 mins | No |
| **TASK-05** | **P2** | Add in-memory rate limiting to `/api/v1/analyses/{id}/chat` | `apps/api/app/routers/chat.py`, `apps/api/app/ai/chat.py` | None | Excess chat requests within 60s return HTTP 429 Too Many Requests | 20 mins | No |
| **TASK-06** | **P2** | Configure optional hosted LLM API key | Render Dashboard env vars (`LLM_API_KEY`, `LLM_ENABLED=true`) | Free Groq API key | `/health` returns `llm: configured` and AI chat returns `llm_verified` mode | 10 mins | Optional (Owner) |
| **TASK-07** | **P3** | Clean up unused icons in Navbar and RankedList | `apps/web/src/components/Navbar.tsx`, `RankedList.tsx` | None | ESLint warnings reduced | 5 mins | No |

---

## 8. Remaining Work Calculation & Timeline

### Requirements Status Breakdown (Total: 28)
- **VERIFIED COMPLETE:** 24 (85.7%)
- **IMPLEMENTED, NOT VERIFIED:** 1 (3.6%)
- **PARTIALLY IMPLEMENTED:** 2 (7.1%)
- **BLOCKED:** 1 (3.6%)
- **NOT IMPLEMENTED:** 0 (0.0%)

### Weighted Progress Calculation
Assigning standard engineering weights:
- **Core Architecture & Contracts (15%):** 100% complete $\to$ **15.0%**
- **Scoring Engine & Data Honesty (25%):** 100% complete $\to$ **25.0%**
- **AI Verifier & Trust Evaluation (25%):** 100% complete $\to$ **25.0%**
- **Frontend UI & Interactive Map (20%):** 95% complete (minor lint fixes pending) $\to$ **19.0%**
- **Deployment & Submission (15%):** 60% complete (scripts ready, awaiting cloud link) $\to$ **9.0%**
- **Overall Weighted Completion:** **93.0%**

### Task Counts by Priority
- **P0 (Blockers to Core Demo):** 0
- **P1 (Required for Submission):** 4 (ESLint fix, Render deploy, Vercel deploy, smoke test)
- **P2 (Reliability & Hosted LLM):** 2 (Rate limiter, LLM key)
- **P3 (Cosmetic Polish):** 1 (Unused icon imports)

### Realistic Remaining Effort Estimates
- **Implementation & Code Cleanup:** ~35 minutes (TASK-01, TASK-05, TASK-07)
- **Manual Cloud Setup (Project Owner):** ~35 minutes (TASK-02, TASK-03, TASK-06)
- **Integration & Smoke Verification:** ~10 minutes (TASK-04)
- **Total Remaining Time Range:** **1 hour 15 minutes to 1 hour 45 minutes**.

---

## 9. Submission Readiness Checklist

- [x] Working full-stack application running locally with API and frontend synchronized.
- [x] Zero invented footfall or rupee rental figures; strict data provenance badges displayed.
- [x] Deterministic scoring decoupled from natural language generation.
- [x] Code-level verification (V1–V9) active with 100% refusal rate on speculative trap questions.
- [x] Adversarial evaluation suite passing 21/21 cases with 0 leaked unsupported claims.
- [x] Map rendering verified live with Carto basemap, H3 hexagons, and numbered markers.
- [x] Zero hardcoded API keys or committed credentials in repository.
- [ ] Frontend ESLint passing without errors (`npm run lint`).
- [ ] Backend deployed to Render with live HTTPS URL.
- [ ] Frontend deployed to Vercel with live HTTPS URL.
- [ ] Production smoke script verified against live public URLs.
