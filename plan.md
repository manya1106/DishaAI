# Disha AI — Agent Swarm Build Plan

> Source of truth for *what the product already is*: `docs/BLUEPRINT.md` (architecture doc). Existing content there is not rewritten — this plan only adds a new section to it describing the change below.
> This file is the plan of changes for turning Disha AI's existing pipeline into an explicit, verifiable **agent swarm**, so the submission can credibly target **Track 2 / Problem Statement O1 — Autonomous Agent Swarms**, while keeping the already-built O3 (Trustworthy and Verifiable AI) work as the swarm's built-in accountability layer rather than a separate feature.
> Step IDs (`P.Part.Step`, e.g. `2.1.1`) are reused in `progress.md`, which tracks how much of this plan is done.
>
> Plan version: 0.1 · Created: 2026-10-18 · Status: Drafted, awaiting owner approval before any code changes begin.

---

## 1. Why this plan exists

Disha AI today (see `docs/BLUEPRINT.md`) is a single FastAPI process: a request comes in, a deterministic scoring engine computes signals, an LLM adapter narrates them, a rule-based verifier (V1–V9) checks the narration, and a fallback narrator kicks in if verification fails. This is correct, tested, and working — but it is **one process calling functions**, not agents collaborating. It does not yet support a credible "Autonomous Agent Swarms" (O1) claim.

This plan turns that same pipeline into **explicitly separated agents that pass typed messages to each other**, coordinated by an orchestrator, with every hand-off logged and traceable. Nothing about the deterministic scoring math, the verifier rules, or the frontend contracts changes — this is a structural decomposition of *how the existing steps talk to each other*, not a rewrite of what they compute.

**Primary track:** Track 2 — Best Open-Source AI Project.
**Primary problem statement:** O1 — Autonomous Agent Swarms.
**Carried-over differentiator:** the existing O3 trust/verification engine becomes the swarm's own internal accountability mechanism — a Verifier Agent that gates every other agent's output before it reaches the user. This is the thing most other agent-swarm entries will not have.

---

## 2. Working rules (set by the owner)

1. Without asking, not even a single letter of existing content is changed. Existing files (including `docs/BLUEPRINT.md`, all code under `apps/api/app` and `apps/web/src`) are never edited without explicit approval for that specific change.
2. No database change is made directly without asking first — not applicable to Phase 0–6 below (no DB touched), flagged again if it ever becomes relevant.
3. `plan.md` (this file) and `progress.md` are kept current as work proceeds.
4. Code quality stays production grade (standards in §5).
5. Nothing is pushed without asking. Local commits are fine.
6. Nothing is assumed. Wherever something is unspecified or blocked, ask.

---

## 3. Approval gates

Work stops and asks before any of these:

| Gate | Trigger |
|---|---|
| **G-EDIT** | Modifying any file that already exists and was not created under this plan. |
| **G-PUSH** | Any `git push`, remote creation, or publishing. Local commits do not need approval. |
| **G-DECIDE** | Any choice this plan leaves open (marked below as **[ASK]**). |
| **G-DEVIATE** | Any deviation from the existing scoring formulas, verifier rules (V1–V9), API contracts in `contracts/openapi.json`, or frontend-facing response shapes. The agent-swarm refactor must be invisible to `apps/web` unless explicitly approved otherwise. |

---

## 4. Target architecture

### 4.1 The four agents

| Agent | Wraps existing code | Responsibility |
|---|---|---|
| **Orchestrator** | New — replaces the direct call chain currently in `apps/api/app/routers/chat.py` / `ai/chat.py` | Receives the user's chat/report request, dispatches to Scoring → Verifier → Narrator in order, assembles the final response, logs every hand-off with a trace ID |
| **Scoring Agent** | `apps/api/app/scoring/engine.py`, `signals.py`, `explain.py` | Computes the 9-signal deterministic scores and per-signal contribution matrix for the requested zone(s); returns a typed result, no narration |
| **Verifier Agent** | `apps/api/app/ai/verifier.py`, `ai/evidence.py` | Builds the evidence bundle from the Scoring Agent's output; given a draft narration from the Narrator Agent, runs rules V1–V9; returns pass/fail + the list of valid claims, or a refusal |
| **Narrator Agent** | `apps/api/app/ai/chat.py`, `ai/adapter.py`, `ai/prompts.py`, `ai/fallback.py` | Given the Scoring Agent's evidence bundle, drafts a natural-language explanation (LLM or deterministic fallback); never sees unverified claims as final — only the Orchestrator decides what ships after the Verifier Agent's check |

### 4.2 Message contract

**[ASK]** Exact schema needs the owner's sign-off before Phase 1 starts. Proposed shape (Pydantic v2, new module `apps/api/app/agents/contracts.py`):

```python
class AgentMessage(BaseModel):
    trace_id: str          # one per end-user request, shared across all hand-offs
    sender: Literal["orchestrator", "scoring", "verifier", "narrator"]
    recipient: Literal["orchestrator", "scoring", "verifier", "narrator"]
    step: int               # ordinal within the trace, for readable logs
    payload: dict           # agent-specific typed payload, validated per-agent
    timestamp: datetime
```

Every hand-off is appended to an in-memory (and optionally persisted) `agent_runs` trace log, keyed by `trace_id`, so a judge can be shown the literal sequence of agent calls for a single request — this is the demo artifact that makes "autonomous agents collaborating" visible rather than asserted.

### 4.3 What does not change

- Scoring math, weights, percentile normalisation — untouched (`G-DEVIATE` applies to any proposed change).
- Verifier rules V1–V9 — untouched, just relocated behind an agent boundary.
- `contracts/openapi.json` and all `apps/web` consumption of the API — untouched. The agent swarm lives *inside* the existing `POST /analyses/{id}/chat` handler; the external contract is identical unless explicitly changed under G-DEVIATE.
- No new external services, no database, no paid dependency.

---

## 5. Production-grade standards (apply to every phase)

1. Full type hints; Pydantic v2 models at every agent boundary; mypy/ruff clean (match existing `ruff check apps/api/` baseline).
2. Every agent has unit tests with no network/LLM calls (mock the Narrator Agent's LLM call exactly as `FakeLLMAdapter` already does).
3. An integration test runs one full trace end-to-end (Orchestrator → Scoring → Narrator → Verifier → final response) and asserts the trace log has the expected hand-off sequence.
4. No bare `except`; existing error envelope (`apps/api/app/errors.py`) reused, not replaced.
5. Logging: every hand-off logged as structured JSON with `trace_id`, `sender`, `recipient`, `step`.
6. Backward compatibility: all 24 existing backend tests and the 21/21 adversarial trust eval must still pass unchanged after the refactor — this is the regression gate for every phase.
7. Small, reviewable local commits only (rule 5); nothing pushed without asking.

---

## 6. Phase overview

**Revision 0.2 (2026-10-18):** Owner decided to replace the JSON-snapshot data layer with real **local PostgreSQL + PostGIS** (Docker), not just for agent trace logs but as the full data foundation — matching the original architecture doc's intent. This inserts a new **Phase D** before the Scoring Agent can be wrapped, since it will read from the database instead of `apps/api/app/data/loader.py`'s snapshot JSON. See §6.1 for the schema proposal awaiting sign-off.

| # | Phase | Goal | Depends on | Output |
|---|---|---|---|---|
| 0 | Contracts & design sign-off | Agree `AgentMessage` schema, agent boundaries, trace log shape | none | Approved contract, no code yet |
| **D** | **Data foundation (PostgreSQL + PostGIS)** | **Stand up local Postgres+PostGIS via Docker, migrate the snapshot data into real tables, idempotent loaders** | **none (can run in parallel with Phase 1)** | **DB with cities/cells/POIs/signals, verified against the existing 417-cell snapshot** |
| 1 | Orchestrator skeleton | In-process dispatcher + trace logger, no behavior change yet | 0 | `apps/api/app/agents/orchestrator.py` passing a no-op trace |
| 2 | Scoring Agent | Wrap `scoring/engine.py` behind the agent boundary, **reading from Postgres instead of the JSON snapshot** | 1, D | Scoring Agent callable via `AgentMessage`, existing scoring tests still pass against DB-backed data |
| 3 | Narrator Agent | Wrap `ai/chat.py` + `ai/adapter.py` behind the agent boundary | 1 | Narrator Agent callable via `AgentMessage` |
| 4 | Verifier Agent | Wrap `ai/verifier.py` + `ai/evidence.py` behind the agent boundary | 2, 3 | Verifier Agent callable via `AgentMessage`, gates Narrator output |
| 5 | End-to-end wiring | Replace the direct call chain in `routers/chat.py` with Orchestrator dispatch | 2, 3, 4 | `POST /analyses/{id}/chat` unchanged externally, agent swarm internally |
| 6 | Observability surface | Agent trace log persisted to Postgres (`agent_runs` table, see §6.1); expose via a route + a small frontend panel showing the agent hand-off sequence for the demo | 5, D | Judge-visible proof of agent collaboration, backed by real DB rows |
| 7 | Tests & regression | Full backend suite + adversarial eval re-run, confirm zero regressions | 1–6 | 24/24 + 21/21 still green, plus new agent tests |
| 8 | Docs | Append the agent-swarm section to `docs/BLUEPRINT.md` (done, see below), update `docs/DEMO.md` script to showcase the trace view, update `PROJECT_STATE.md`/`STATUS.md` | 7 | Submission-ready docs |

### 6.1 Phase D — Data foundation: proposed schema (G-DB — not applied until approved)

**Infra:** new `docker-compose.yml` at repo root, one service: `postgis/postgis:16-3.4`, local only, port mapped to `5432` (checked against anything else on the machine first), volume for persistence, credentials via `.env` (not committed). `DATABASE_URL` in `.env.example` already has the right shape — no change needed there, just a value supplied locally.

**Migration tooling:** Alembic + SQLAlchemy 2.0 (async), matching the production-grade standards in §5 (full typing, no ORM magic hiding business logic — scoring math stays in pure Python, the DB is a data source, not a computation layer).

**Proposed tables** (draft — exact DDL shown for sign-off before `alembic upgrade head` is ever run):

```sql
-- cities: one row per city the snapshot covers
CREATE TABLE cities (
    id          SERIAL PRIMARY KEY,
    slug        TEXT UNIQUE NOT NULL,        -- e.g. 'blr'
    name        TEXT NOT NULL,
    boundary    GEOMETRY(POLYGON, 4326),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- h3_cells: one row per H3 res-8 cell (417 for Bengaluru today)
CREATE TABLE h3_cells (
    h3_index      TEXT PRIMARY KEY,
    city_id       INTEGER NOT NULL REFERENCES cities(id),
    centroid      GEOMETRY(POINT, 4326) NOT NULL,
    boundary      GEOMETRY(POLYGON, 4326) NOT NULL,
    locality_name TEXT
);

-- pois: raw OSM evidence rows, natural key for idempotent upsert
CREATE TABLE pois (
    id        SERIAL PRIMARY KEY,
    osm_type  TEXT NOT NULL,
    osm_id    BIGINT NOT NULL,
    h3_index  TEXT NOT NULL REFERENCES h3_cells(h3_index),
    category  TEXT NOT NULL,
    name      TEXT,
    tags      JSONB,
    geom      GEOMETRY(POINT, 4326),
    UNIQUE (osm_type, osm_id)
);

-- cell_signals: the 9 signals per cell, per category, per budget tier
CREATE TABLE cell_signals (
    h3_index     TEXT NOT NULL REFERENCES h3_cells(h3_index),
    category     TEXT NOT NULL,
    budget_tier  TEXT NOT NULL,
    signal_name  TEXT NOT NULL,              -- e.g. 'competition_density'
    raw_value    NUMERIC,
    percentile   NUMERIC,
    provenance   TEXT NOT NULL,              -- 'measured' | 'estimated' | 'heuristic' | 'unavailable'
    computed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (h3_index, category, budget_tier, signal_name)
);

-- agent_runs: the trace log for Phase 6 observability
CREATE TABLE agent_runs (
    id          BIGSERIAL PRIMARY KEY,
    trace_id    TEXT NOT NULL,
    step        INTEGER NOT NULL,
    sender      TEXT NOT NULL,
    recipient   TEXT NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_agent_runs_trace ON agent_runs (trace_id, step);
```

**Idempotency:** `pois` upserts on `(osm_type, osm_id)`; `h3_cells` upserts on `h3_index`; `cell_signals` upserts on its composite key — re-running the loader for the same city never duplicates rows, matching §5.5 of the production standards.

**Migration path for existing data:** a one-time script reads the current `apps/api/app/data/snapshots/blr.json` and inserts it into the new tables — this is the bridge so nothing about the 417-cell Bengaluru dataset is lost or re-fetched from OSM.

**Not changed:** `apps/api/app/scoring/signals.py`'s actual math is untouched — only where its *inputs* come from changes (DB query instead of JSON file read).

---

## Phase 0: Contracts & design sign-off

**Goal:** lock the `AgentMessage` schema and agent responsibilities before any code is written.
**Exit criteria:** owner approves the schema in §4.2, the four agent boundaries in §4.1, and the trace-log route question in Phase 6.

- **0.1** Owner reviews and approves (or amends) the `AgentMessage` schema above.
- **0.2** Owner confirms the four-agent split matches intent (no fifth agent, no merge of Verifier into Orchestrator).
- **0.3** Owner decides the trace-log exposure route name/shape for Phase 6 (**[ASK]**).
- **0.4** Owner confirms: agent work happens on a new branch/working-tree area, or directly on `main` locally (no push either way) — **[ASK]**.

---

## Phase 1: Orchestrator skeleton

- **1.1.1** Create `apps/api/app/agents/__init__.py`, `apps/api/app/agents/contracts.py` (the `AgentMessage` model + an `AgentTrace` log model).
- **1.1.2** Create `apps/api/app/agents/orchestrator.py`: an `Orchestrator` class with a `dispatch(message: AgentMessage) -> AgentMessage` method and an in-memory trace store keyed by `trace_id`.
- **1.1.3** Unit tests: dispatching a no-op message records one trace entry with the correct ordinal.
- **1.1.4** No existing router wired yet — this phase is additive only, zero behavior change to any endpoint.

## Phase 2: Scoring Agent

- **2.1.1** Create `apps/api/app/agents/scoring_agent.py`: a thin wrapper class whose `handle(message)` calls `scoring/engine.py` unchanged and returns the result inside an `AgentMessage` payload.
- **2.1.2** Unit test: Scoring Agent output for a known fixture matches the existing `test_golden.py` expected values bit-for-bit (regression gate).

## Phase 3: Narrator Agent

- **3.1.1** Create `apps/api/app/agents/narrator_agent.py`: wraps `ai/chat.py` + `ai/adapter.py` + `ai/fallback.py`, unchanged internals, returns a draft narration (not yet verified) inside an `AgentMessage`.
- **3.1.2** Unit test with `FakeLLMAdapter` (already exists) confirms Narrator Agent draft output matches current direct-call behavior.

## Phase 4: Verifier Agent

- **4.1.1** Create `apps/api/app/agents/verifier_agent.py`: wraps `ai/verifier.py` + `ai/evidence.py`; `handle(message)` takes the Scoring Agent's evidence bundle and the Narrator Agent's draft, runs V1–V9, returns pass/claims or a refusal.
- **4.1.2** Unit tests: all 9 existing verifier-rule tests (`test_verifier.py`) still pass when invoked through the agent wrapper, unchanged assertions.

## Phase 5: End-to-end wiring

- **5.1.1** Modify `apps/api/app/routers/chat.py` (**G-EDIT — ask first**) to dispatch through `Orchestrator` instead of calling `ai/chat.py` directly.
- **5.1.2** `Orchestrator.handle_chat_request(...)` sequences: Scoring Agent → Narrator Agent → Verifier Agent → (pass: return narration; fail: fall back to deterministic narrator, same as today).
- **5.1.3** Integration test: one full request produces an `AgentMessage` trace of exactly 3 hand-offs (or 4 on fallback) in the expected order.
- **5.1.4** Confirm `POST /analyses/{id}/chat` response shape is byte-identical to pre-refactor for the same input (contract regression check).

## Phase 6: Observability surface

- **6.1.1** **[ASK]** Decide and approve the trace exposure route (new endpoint vs. reusing `/trust/stats`).
- **6.1.2** Add the approved route returning the trace log for a given `trace_id`.
- **6.1.3** **(G-EDIT — ask first)** Add a small panel to the frontend (`/trust` page or a new section) rendering the agent hand-off sequence for the last chat request — this is the visible "agents collaborating" proof for judges.

## Phase 7: Tests & regression

- **7.1.1** Run full `pytest apps/api/tests/ -v` — must stay 24/24 (plus new agent tests, net increase only).
- **7.1.2** Run `python scripts/eval_trust.py` — must stay 21/21, 0 leaked claims.
- **7.1.3** Run `ruff check apps/api/` — must stay clean.
- **7.1.4** Run `cd apps/web && npm run build` — must stay green (no contract changes expected to touch it).

## Phase 8: Docs

- **8.1.1** Append the agent-swarm architecture section to `docs/BLUEPRINT.md` (see draft below — appended now as an addition, existing content untouched).
- **8.1.2** Update `docs/DEMO.md` demo script to walk through the trace view.
- **8.1.3** Update `PROJECT_STATE.md` / `STATUS.md` feature matrices once Phase 7 is green.

---

## 7. Out of scope for this plan

- Any change to scoring formulas, weights, or signal definitions.
- Any change to verifier rules V1–V9 logic (only their packaging into an agent).
- Any new external service, database, or paid dependency.
- Nasiko or any other external agent-runtime platform — these agents are in-process Python objects, not separately deployed services. (A separate-services version remains possible later but is not part of this plan.)
- Track 1 (Gemma 4) or Track 3 (Sarvam) work.

## 8. Change control

Any change to this plan is made only with the owner's approval and recorded in the change log at the end of `progress.md`.

---

## 9. UI contrast / "drowsy" fix pass (2026-10-18)

### 9.1 Why

The `/explore` result page reads flat and sleepy. Root cause: translucent `bg-white/50`–`bg-white/70` + near-invisible `/8`–`/12` opacity borders on interior cards. Against the `#F6F1E7` cream background these near-white panels have < 2:1 contrast — they vanish. The reference bar is the Nasiko Buildathon's result page: `bg-white rounded-2xl shadow-sm border border-neutral-100` — pure white, real 1px border, visible shadow.

### 9.2 Previous session (already applied — do not re-apply)

| File | Change |
|---|---|
| `globals.css` | `.glass-panel` / `.glass-panel-elevated` / `.glass-dropdown` switched from translucent to solid `#fffdf9`/`#fffefb` with real borders and shadows |
| `RankedList.tsx` | Cards changed to `bg-white border-[#15130F]/15 shadow-sm`; score-bar (██) added below each ranked zone |
| `explore/page.tsx` KPI strip | Switched to `bg-white rounded-xl border border-[#15130F]/15 shadow-sm grid … divide-x` — solid stat tile row |

### 9.3 This session — components still using translucent surfaces

| Component | Drowsy elements | Fix |
|---|---|---|
| `CompareView.tsx` | Score cards `bg-white/50 border-[#15130F]/10`; signal-delta rows same; score row bg `bg-[#15130F]/4` | → `bg-white border-[#15130F]/12 shadow-sm` on cards; `bg-[#15130F]/5` row bg |
| `LocationReport.tsx` | Signal-bar cards `bg-white/50 border-[#15130F]/10`; strengths card `bg-white/50 border-[#2F6E4E]/20`; limitations card `bg-white/50 border-[#A6693B]/20`; evidence table container `bg-white/50 border-[#15130F]/10` | → `bg-white` on all, keep coloured borders |
| `ChatPanel.tsx` | Prompt pills `bg-white/50`; agent-trace badge `bg-white/60`; agent-trace chip `bg-white/70`; claim chip `bg-white/70` | → `bg-white` throughout |
| `trust/page.tsx` | Live-health bar `bg-white/50`; all four provenance cards `bg-white/50`; limitations section `bg-white/50`; first KPI card uses `glass-panel` (already solid via CSS) | → `bg-white` on all `bg-white/50` surfaces |

### 9.4 Rules for this pass (same as §2)

- No letter changed that isn't listed above.
- No database change.
- No logic change — styling only.
- Build must stay green (no new TS/lint errors introduced).
- Local commit after build confirmed; no push.
