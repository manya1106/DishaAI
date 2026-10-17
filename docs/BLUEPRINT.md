# Disha AI — Hackday Build Blueprint

*Greenfield plan · Track 2 (Best Open-Source AI Project) · Problem statement O3 — Trustworthy and Verifiable AI · Prepared for Manya*

**How to read this:** [DECIDED] = committed choice. [VERIFY] = depends on something I can’t confirm from here (model names, quotas, platform limits, hackathon rules), and comes with a check you can run. [ASSUMPTION] = my guess; change it if it’s wrong.

**Time budget [ASSUMPTION]:** Tonight until 12:00 AM; Tomorrow 9:00 AM–3:30 PM submission. Window roughly 7-8 hours total focused dev time.

**Heads-up on the architecture doc:** It names only three of the nine signals (competition, gap opportunity, rent efficiency). I define the other six in section D.

**Repository:** `https://github.com/manya1106/DishaAI.git`

---

## A. Executive recommendation

**Primary track:** Track 2 — Best Open-Source AI Project. **Primary problem statement:** O3 — Trustworthy and Verifiable AI. [DECIDED]

### Why O3 fits Disha AI

The deterministic engine computes the numbers, an LLM only narrates them, and a guardrail refuses to state numbers that aren’t in the data. Every AI sentence is decomposed into claims, each claim must cite evidence IDs, and a verifier checks numbers, names, ranks and strength/weakness direction against the computed data before the user sees anything. When verification fails, the app degrades to deterministic answers instead of showing unverified text.

---

## B. Core Architecture & Requirements

1. **Frontend**: Next.js 14+ (App Router, TypeScript, Tailwind CSS, Lucide icons, MapLibre GL).
2. **Backend**: FastAPI (Python 3.11+), Pydantic v2, Uvicorn, H3 geospatial indexing.
3. **Data**: Precomputed snapshot of Bengaluru (with synthetic/osm coverage options), H3 resolution 8 cells (~0.7 km² each), 9 signals with deterministic percentile normalisation.
4. **Scoring Engine**:
   - `competition_density` (measured, lower is better)
   - `gap_opportunity` (estimated, higher is better)
   - `footfall_anchors` (estimated, higher is better)
   - `transit_access` (measured, higher is better)
   - `complementary_mix` (measured, higher is better)
   - `residential_catchment` (estimated, higher is better)
   - `daytime_population` (estimated, higher is better)
   - `road_accessibility` (measured, higher is better)
   - `rent_efficiency` (heuristic, higher is better)
5. **AI Verifier (V1-V9)**:
   - Strict sentence-to-claim schema.
   - Evidence ID grounding.
   - Numeric tolerance matching.
   - Location name and rank checks.
   - Polarity check (strength vs weakness).
   - Forbidden topics (revenue/unsupported currency figures).
   - Graceful repair retry and fallback to deterministic narrator.
6. **Trust Page (`/trust`)**:
   - Pipeline explanation, provenance definitions, real evaluation metrics from `eval_trust.py`.
