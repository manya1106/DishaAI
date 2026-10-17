# Disha AI — Architectural Decisions Log

## Decision 1: Target Track & Problem Statement
- **Track:** Track 2 — Best Open-Source AI Project.
- **Problem Statement:** O3 — Trustworthy and Verifiable AI.
- **Rationale:** Focus on provable truth. The scoring engine calculates numbers deterministically from OpenStreetMap data and heuristic rent tiers; an open-weight LLM only narrates the findings. Every claim is verified against calculated evidence.

## Decision 2: Spatial Representation
- **Grid:** Uber H3 hexagonal spatial index at Resolution 8 (~0.73 km² per hexagon, edge length ~461m).
- **Rationale:** Hexagons maintain uniform neighbour distances (unlike square grids). Cell ID is self-contained and compact.

## Decision 3: The Nine Signals & Weights
- 1. `competition_density` (measured, lower is better)
- 2. `gap_opportunity` (estimated, higher is better)
- 3. `footfall_anchors` (estimated, higher is better)
- 4. `transit_access` (measured, higher is better)
- 5. `complementary_mix` (measured, higher is better)
- 6. `residential_catchment` (estimated, higher is better)
- 7. `daytime_population` (estimated, higher is better)
- 8. `road_accessibility` (measured, higher is better)
- 9. `rent_efficiency` (heuristic, higher is better)

## Decision 4: Rent Representation
- **Policy:** Never fabricate rupee figures (e.g. ₹85,000/mo). Rent is represented strictly as a heuristic tier (1 to 5) with an honest provenance label: `heuristic` ("team-assigned, unverified").

## Decision 5: AI Verification Strategy
- Every AI response is decomposed into single-sentence blocks with cited `evidence_ids`.
- Verifier rules V1–V9 execute in deterministic code before the user sees the response.
- If unverified claims exceed 50% or the LLM is unavailable, degrade gracefully to the deterministic narrator.
