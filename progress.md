# Disha AI — Progress Log (Agent Swarm Build)

> Tracks how much of `plan.md` is done. Step IDs match `plan.md` exactly (`P.Part.Step`).
> Also records the pre-existing baseline (everything built before this plan started), so progress is read against reality, not assumptions.

Last updated: 2026-10-18 · Plan version tracked: 0.1

---

## 1. Baseline — already built before this plan (not part of this plan's scope)

Carried over from `PROJECT_STATE.md` / `STATUS.md` / `docs/IMPLEMENTATION_AUDIT.md` as of the last verified run (2026-10-17):

| Area | State |
|---|---|
| Contracts (Pydantic v2, OpenAPI, generated TS types) | Done, verified |
| Deterministic 9-signal scoring engine | Done, verified (`test_golden.py` bit-for-bit) |
| V1–V9 claim verifier + evidence bundle | Done, verified (21/21 adversarial eval, 0 leaked claims) |
| Deterministic fallback narrator | Done, verified |
| FastAPI endpoints (`/health`, `/meta`, `/analyses`, `/compare`, `/chat`, `/trust/stats`) | Done, verified |
| Next.js frontend (`/`, `/explore`, `/trust`) | Done, verified in browser |
| Backend tests | 24/24 passing |
| Frontend build | Passing (6 ESLint errors outstanding, tracked in `docs/IMPLEMENTATION_AUDIT.md` TASK-01, out of scope here) |
| Public deployment (Render/Vercel) | Not done, out of scope here |
| Multi-agent structure | **Not started — this is what `plan.md` adds** |
| Gemma 4 / Sarvam integration | Not started, out of scope (Track 2/O1 chosen as primary; see Decision Log) |
| Local PostgreSQL + PostGIS data layer | **Not started — this is what `plan.md` Phase D adds** (scope confirmed 2026-10-18, see D-06/D-07/D-08) |

---

## 2. Plan progress — `plan.md` steps

| Step ID | Description | Owner | Status | Notes |
|---|---|---|---|---|
| 0.1 | Owner approves `AgentMessage` schema | M | **Not started** | Blocking all of Phase 1+ |
| 0.2 | Owner confirms 4-agent split | M | **Not started** | |
| 0.3 | Owner decides trace-log route | M | **Not started** | [ASK] open |
| 0.4 | Owner decides branch vs. main (local only) | Shared | **Not started** | [ASK] open |
| D.1 | Create `docker-compose.yml` (postgis/postgis:16-3.4, local only) | D | Not started | New file, not an existing-file edit |
| D.2 | Owner approves exact DDL in `plan.md` §6.1 (**G-DB**) | D | **Not started** | Blocking D.3+ |
| D.3 | Install Alembic + SQLAlchemy 2.0 async, add to `requirements.txt` | D | Not started | |
| D.4 | Write initial migration from approved DDL | D | Not started | |
| D.5 | `docker compose up -d` + `alembic upgrade head` (**G-DB — ask immediately before running**) | D | Not started | |
| D.6 | One-time script: load `data/snapshots/blr.json` into `cities`/`h3_cells`/`pois`/`cell_signals` | D | Not started | |
| D.7 | Idempotency test: re-running the loader twice produces identical row counts | D | Not started | |
| D.8 | Update `apps/api/app/data/loader.py` (or add a DB-backed loader alongside it) to read from Postgres (**G-EDIT**) | D | Not started | Snapshot JSON kept as offline/dev fallback unless told otherwise |
| D.9 | Confirm `test_golden.py` still produces bit-for-bit identical scores against DB-backed data | D | Not started | Regression gate before Phase 2 proceeds |
| 1.1.1 | Create `agents/contracts.py` | M | Not started | |
| 1.1.2 | Create `agents/orchestrator.py` | M | Not started | |
| 1.1.3 | Orchestrator no-op unit test | M | Not started | |
| 1.1.4 | No router wired yet (additive-only checkpoint) | M | Not started | |
| 2.1.1 | Scoring Agent wrapper | D | Not started | |
| 2.1.2 | Scoring Agent regression test vs. `test_golden.py` | D | Not started | |
| 3.1.1 | Narrator Agent wrapper | M | Not started | |
| 3.1.2 | Narrator Agent test with `FakeLLMAdapter` | M | Not started | |
| 4.1.1 | Verifier Agent wrapper | M | Not started | |
| 4.1.2 | Verifier Agent regression test vs. `test_verifier.py` | M | Not started | |
| 5.1.1 | Wire `routers/chat.py` to Orchestrator (**G-EDIT**) | M | Not started | |
| 5.1.2 | Orchestrator sequencing logic | M | Not started | |
| 5.1.3 | Integration test: full trace, expected hand-off order | M | Not started | |
| 5.1.4 | Contract regression check (byte-identical response) | M | Not started | |
| 6.1.1 | Decide trace exposure route (**[ASK]**) | M | Not started | Same as 0.3 |
| 6.1.2 | Implement trace route | M | Not started | |
| 6.1.3 | Frontend trace panel (**G-EDIT**) | M | Not started | |
| 7.1.1 | Full backend pytest re-run (24/24 + new) | Shared | Not started | |
| 7.1.2 | Adversarial eval re-run (21/21) | Shared | Not started | |
| 7.1.3 | ruff re-check | Shared | Not started | |
| 7.1.4 | Frontend build re-check | Shared | Not started | |
| 8.1.1 | Append agent-swarm section to `docs/BLUEPRINT.md` | Shared | **Done** | Appended 2026-10-18, existing content untouched |
| 8.1.2 | Update `docs/DEMO.md` | Shared | Not started | |
| 8.1.3 | Update `PROJECT_STATE.md` / `STATUS.md` | Shared | Not started | |

**Summary:** 1 of 36 plan steps done (documentation only). All code steps (Phase D, 1–7) await the Phase 0 sign-offs and the Phase D DDL approval (D.2) below before starting, per plan rule 6 (nothing assumed).

---

## 3. Decision Log

| ID | Question | Status | Answer |
|---|---|---|---|
| D-01 | Which track/problem-statement is primary? | **Answered** | Track 2, O1 (Autonomous Agent Swarms), with the existing O3 trust/verification work carried over as the swarm's internal accountability layer. |
| D-02 | Agent runtime: in-process (same FastAPI process) or separate services? | **Answered** | In-process, per owner's effort/risk preference discussed before this plan — no Nasiko or separate deployment. |
| D-03 | Exact `AgentMessage` schema | **Open [ASK]** | Proposed in `plan.md` §4.2, awaiting owner sign-off (step 0.1). |
| D-04 | Exact trace-log exposure route/shape | **Open [ASK]** | Awaiting owner decision (step 0.3 / 6.1.1). |
| D-05 | Work on a new branch or directly on local `main`? | **Open [ASK]** | Awaiting owner decision (step 0.4). No push either way per plan rule 5. |
| D-06 | What should local Postgres store? | **Answered** | Full data layer migration (cities, H3 cells, POIs, signals) — not just agent trace logs. The JSON snapshot becomes the migration source, kept as an offline fallback. |
| D-07 | Plain Postgres or PostGIS? | **Answered** | PostGIS, installed from the start (`postgis/postgis:16-3.4`), for future geometry operations even though current scoring only needs precomputed H3 indices. |
| D-08 | How is Postgres run locally? | **Answered** | Docker container via `docker compose`, not a native Windows install. |
| D-09 | Exact DDL for `cities`/`h3_cells`/`pois`/`cell_signals`/`agent_runs` | **Open [ASK]** | Proposed in `plan.md` §6.1, awaiting owner sign-off (step D.2) before any migration is applied. |

---

## 4. Handoffs

Used when one person needs a change in an area owned by the other (see §5.1 for ownership). Empty until the first cross-boundary request happens.

| From | To | File/Area | Reason |
|---|---|---|---|
| — | — | — | — |

---

## 5. Work split — Person D / Person M

**Revision 0.3 (2026-10-18):** Work is split between two people working the same plan in parallel. "Folder" here means ownership zones over the existing tree, not a physical copy of the repo — splitting the FastAPI app into separate physical folders would break the existing contracts in `contracts/openapi.json`. If a literal separate `person_D/` / `person_M/` directory pair is actually wanted instead, say so and this section gets redone.

### 5.1 Ownership

| Owner | Owns | Phases |
|---|---|---|
| **Person D** (Data) | `docker-compose.yml`, `apps/api/app/db/**` (new), Alembic migrations, `apps/api/app/data/**`, `apps/api/app/agents/scoring_agent.py` | Phase D (Data foundation), Phase 2 (Scoring Agent) |
| **Person M** (Multi-agent) | `apps/api/app/agents/contracts.py`, `apps/api/app/agents/orchestrator.py`, `apps/api/app/agents/narrator_agent.py`, `apps/api/app/agents/verifier_agent.py`, `apps/api/app/routers/chat.py` (**G-EDIT**), the frontend trace panel under `apps/web/src` | Phase 0 (contracts), Phase 1 (Orchestrator), Phase 3 (Narrator Agent), Phase 4 (Verifier Agent), Phase 5 (wiring), Phase 6 (observability) |
| **Shared** | `plan.md`, `progress.md` (targeted edits to own rows only, never a full rewrite), test suite re-runs | Phase 7 (tests/regression), Phase 8 (docs) |

### 5.2 Contract between the two tracks

The boundary is the `AgentMessage` envelope (`plan.md` §4.2) plus the Scoring Agent's output schema. Person M's Orchestrator/Narrator/Verifier agents only ever see the Scoring Agent's typed result — never the database, never the loader internals. This means Person M's work (Phases 0, 1, 3, 4, 5, 6) can proceed **before** Phase D finishes, against the current JSON-snapshot-backed Scoring Agent, and switches transparently to the DB-backed one once Person D's Phase D lands — no change needed on Person M's side if the Scoring Agent's output shape doesn't change.

### 5.3 Coordination rules

1. One owner per file/area above. To change something outside your own area, add a row to the Handoffs table (§4) and let its owner make the change.
2. Git: local commits only (plan rule 5), no push. Each person stages only their own paths (never `git add -A`), and prefixes commit subjects with `[D]` or `[M]`.
3. Tests: no network/DB calls in default test runs for Person M's agents (mock the Scoring Agent's output exactly as `FakeLLMAdapter` already mocks the LLM). Person D's DB tests use the `integration` marker and need Docker running.
4. Database: only Person D ever runs `docker compose up` / `alembic upgrade head` / applies migrations (gate G-DB stays owned by Person D; Person M never opens a DB connection directly).
5. Decisions and blockers: either person may ask the owner, recorded in the Decision Log (§3).

## 6. Change log

| Date | Change | Approved by |
|---|---|---|
| 2026-10-18 | `plan.md` and `progress.md` created; `docs/BLUEPRINT.md` appended with the agent-swarm section (new content only, nothing existing altered) | Owner (requested this session) |
| 2026-10-18 | Scope expanded to full PostgreSQL + PostGIS data foundation (Phase D added); schema drafted in `plan.md` §6.1, awaiting DDL sign-off (D-09) | Owner |
| 2026-10-18 | Work split into Person D / Person M ownership zones (§5); step table given an Owner column | Owner |
