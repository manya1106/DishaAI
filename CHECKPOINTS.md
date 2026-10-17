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
