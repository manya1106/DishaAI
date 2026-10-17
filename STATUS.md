# Disha AI — Build Status

**Last Updated:** Phase E (Full Stack Complete & Ready for Public Deployment)

### 1. What Currently Works
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
  - 24/24 backend tests passing (`pytest tests/ -v`).
  - Codebase linted and clean (`ruff check .`).
  - Next.js production build succeeding (`npm run build`).
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
1. Push latest code to GitHub repository `manya1106/DishaAI`.
2. Connect repository to Vercel (Frontend) and Render (Backend) per `docs/DEPLOY.md`.
3. Run `scripts/smoke_public.sh` against the live URLs.

### 5. Next Three Highest-Priority Actions
1. Push current complete codebase to `origin main`.
2. Owner creates Render web service and Vercel project using instructions in `docs/DEPLOY.md`.
3. Verify public URLs with automated smoke script.
