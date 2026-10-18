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

---

## C. Addendum — Agent Swarm Redesign (2026-10-18)

*Appended without altering sections A–B above. Full plan and rollout tracking live in `plan.md` / `progress.md` at the repo root.*

**Revised primary problem statement:** Track 2 — Best Open-Source AI Project, **O1 — Autonomous Agent Swarms**, chosen over continuing with O3 alone because:
- O1 is judged to have the least hype-driven crowding of the three tracks at this event (unlike the Gemma 4 and Sarvam tracks, which are expected to draw volume purely from sponsor visibility).
- The existing O3 trust/verification engineering (section B.5 above) becomes the swarm's internal accountability layer rather than a separate feature — most agent-swarm entries will not have a dedicated agent that can refuse another agent's output.
- The change is structural, not a rewrite: the same scoring math, the same verifier rules (V1–V9), and the same external API contracts are reused unchanged, just re-packaged behind explicit agent boundaries with logged hand-offs.

**The four agents** (see `plan.md` §4 for full detail):

| Agent | Wraps | Role |
|---|---|---|
| Orchestrator | New | Dispatches a request through the other three agents in order, logs every hand-off with a trace ID |
| Scoring Agent | `scoring/engine.py`, `signals.py`, `explain.py` | Computes the 9-signal deterministic result |
| Narrator Agent | `ai/chat.py`, `ai/adapter.py`, `ai/fallback.py` | Drafts a natural-language explanation from the Scoring Agent's evidence |
| Verifier Agent | `ai/verifier.py`, `ai/evidence.py` | Runs rules V1–V9 against the Narrator Agent's draft before anything reaches the user |

Agents run in-process (no Nasiko, no separate deployment, no new infrastructure) and communicate via a typed `AgentMessage` envelope with a shared `trace_id` per request, so the hand-off sequence can be shown live to judges as proof of autonomous collaboration — not just asserted.

**Explicitly unchanged by this addendum:** scoring formulas and weights, verifier rule logic, the `contracts/openapi.json` external API shape, and all O3-related claims in section A above remain true — O3 compliance is preserved as a property of the swarm, not removed.
