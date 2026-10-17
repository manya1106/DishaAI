# Disha AI — Architectural Decisions Log

This document records the core architectural decisions, their rationales, and their implementation status for Disha AI.

---

## Decision 1: Target Track & Problem Statement
- **Track:** Track 2 — Best Open-Source AI Project
- **Problem Statement:** O3 — Trustworthy and Verifiable AI
- **Status:** **Committed & Implemented**
- **Rationale:** High-stakes business location decisions cannot rely on ungrounded generative LLM hallucinations. By decoupling deterministic scoring from narration and introducing a code-level verifier (Rules V1–V9), Disha AI delivers provable, cited truth.
- **Impact:** System separates mathematical ranking from natural language generation.

---

## Decision 2: Spatial Representation via Uber H3
- **Choice:** Uber H3 Hexagonal Hierarchical Spatial Index at Resolution 8 (~0.73 km² per hexagon, edge length ~461m).
- **Status:** **Committed & Implemented**
- **Rationale:** Hexagons maintain uniform distances between all 6 neighbours (unlike square grids where diagonal neighbours are further apart). H3 indices are compact 64-bit integers represented as strings (e.g. `8861892463fffff`), requiring no PostGIS extension for distance queries.
- **Impact:** Lightweight in-memory computation; 417 cells cover central Bengaluru.

---

## Decision 3: The Nine Location Signals & Weight Architecture
- **Choice:** Deterministic 9-signal pipeline across measured, estimated, and heuristic classes.
- **Status:** **Committed & Implemented**
- **Signals:**
  1. `competition_density` (measured, lower is better)
  2. `gap_opportunity` (estimated, higher is better)
  3. `footfall_anchors` (estimated, higher is better)
  4. `transit_access` (measured, higher is better)
  5. `complementary_mix` (measured, higher is better)
  6. `residential_catchment` (estimated, higher is better)
  7. `daytime_population` (estimated, higher is better)
  8. `road_accessibility` (measured, higher is better)
  9. `rent_efficiency` (heuristic, higher is better)
- **Rationale:** Captures both demand generators (daytime offices, residential, transit, anchors) and cost/saturation dampers (competitor density, rent feasibility).
- **Impact:** Transparent formula where user can inspect exact signal contribution points (`+X.X pts`).

---

## Decision 4: Honest Rent Representation Policy
- **Choice:** Never fabricate rupee lease figures (e.g. ₹85,000/mo). Represent rent strictly as a team-assigned heuristic tier (1 to 5) with an explicit `heuristic` provenance badge.
- **Status:** **Committed & Implemented**
- **Rationale:** Commercial lease prices in India are private and unstandardized. Fabricating fake rental figures violates data honesty and misleads entrepreneurs.
- **Impact:** If a user asks for exact rupee rent or revenue in chat, the system triggers `refused_insufficient_data` with an honest refusal.

---

## Decision 5: AI Verification Strategy (Rules V1–V9)
- **Choice:** Deterministic code-level verifier checking parsed LLM blocks before presentation.
- **Status:** **Committed & Implemented**
- **Rationale:** LLMs cannot be trusted to grade their own homework. Verification rules execute in pure Python using numerical tolerance and entity lookups against the pre-calculated evidence bundle.
- **Impact:** 0 leaked unsupported claims across 21 adversarial test cases.

---

## Decision 6: Stateless Analysis Architecture (`analysis_id`)
- **Choice:** `analysis_id` is the base64url encoding of the validated inputs JSON (`city_id`, `category_id`, `budget_tier`, `top_n`, `weight_overrides`).
- **Status:** **Committed & Implemented**
- **Rationale:** Free-tier hosting platforms (such as Render) sleep when inactive. In a stateless token architecture, any request containing an `analysis_id` can be recomputed instantaneously after server wake-up without requiring persistent database state.
- **Impact:** Zero database dependency on analysis, report, comparison, and chat paths.
