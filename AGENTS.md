# AGENTS.md — Non-Negotiable Project Rules & Role Boundaries

> **CRITICAL INSTRUCTION FOR ALL AGENTS & NEW CONVERSATIONS:**  
> Assume every new session starts with **zero context**. Before editing any code or making assumptions, you MUST follow the **Mandatory New-Conversation Protocol** defined below.

---

## 1. Core Rules for All Work

1. **Read `docs/BLUEPRINT.md`** before making architectural changes.
2. **Deterministic scoring is the single source of truth**: The AI does not compute scores or invent rankings; it strictly narrates the calculated evidence bundle.
3. **Contracts are sacred**: Only Lead/Architect updates `contracts/` and `apps/api/app/schemas/`. Other components consume generated TypeScript types (`apps/web/src/types/api.ts`) or Pydantic models.
4. **Data honesty**: Never fabricate real-world outcomes, rupee rents, or fake footfall numbers. Every data point and signal carries an explicit provenance tag (`measured`, `estimated`, `heuristic`, `simulated`, `unavailable`).
5. **No secret leaks**: Never commit API keys or credentials. Use `.env.example` for template variables.
6. **Graceful degradation**:
   - If DB is unavailable, store traces in-memory without breaking requests.
   - If LLM is unavailable or unconfigured, use deterministic fallback.
   - If external OSM fails, use local verified snapshot/synthetic fixture with `simulated` label.
7. **Verification over generation**: All LLM claims must pass verifier rules V1–V9. Unverified claims are excised; failing responses degrade to deterministic narrative.
8. **Definition of Done**: Code is tested with unit tests, runs locally without crashes, passes contract checks, and has clear verification output.
9. **Never hallucinate status**: Distinguish strictly between `Implemented`, `Tested`, `Verified end-to-end`, `Unverified`, and `Blocked`. Never invent test results or pretend code works without running actual commands.

---

## 2. File Ownership & Boundaries

- **Lead / Architect**: `contracts/**`, `apps/api/app/schemas/**`, `docs/**`, `AGENTS.md`, `PROJECT_STATE.md`, `STATUS.md`, `DECISIONS.md`, `CHECKPOINTS.md`, `HANDOFF.md`, `MANUAL_ACTIONS.md`, `.env.example`, `Makefile`
- **Frontend**: `apps/web/**` (except generated `src/types/api.ts`)
- **Backend & Data**: `apps/api/app/{main,config,logging,errors}.py`, `apps/api/app/scoring/**`, `apps/api/app/data/**`, `apps/api/app/routers/**` (except chat/trust), `apps/api/app/db/**`
- **AI & Trust**: `apps/api/app/ai/**`, `apps/api/app/routers/{chat,trust}.py`, `scripts/{check_llm,eval_trust}.py`, `apps/api/app/data/eval/**`
- **QA & Deployment**: `apps/web/e2e/**`, `apps/api/tests/**`, `apps/api/Dockerfile`, `scripts/smoke_public.sh`, `README.md`, `docs/DEPLOY.md`

---

## 3. Mandatory New-Conversation Protocol

Whenever an agent or conversation begins fresh:
1. **Inspect Before Acting**:
   - Run `git status`, `git branch -a`, `git log -n 5 --oneline`, and `git tag -l`.
   - Inspect the actual filesystem and active files instead of trusting chat memory.
2. **Read Authoritative State**:
   - Read `AGENTS.md`, `PROJECT_STATE.md`, `HANDOFF.md`, `STATUS.md`, and the latest entry in `CHECKPOINTS.md`.
3. **Establish Baseline Understanding**:
   - Formulate a brief internal summary: current verified state, current assigned task, any discrepancies observed between code and documentation.
   - If documentation conflicts with actual code or test output, investigate and update documentation to match reality.
4. **Preserve User Changes**:
   - Never reset, force-push, or discard uncommitted working-tree changes without explicit authorization.

---

## 4. Checkpoint & Memory Requirements

Every meaningful milestone requires an explicit checkpoint entry:
- Before risky architectural changes or dependency upgrades.
- After implementing or integrating a complete vertical slice.
- After executing test suites.
- Before preparing for deployment.
- Before ending a work session.

**Checkpoint Procedure**:
1. Run real verification commands (e.g. `pytest`, `npm run build`, `ruff check`).
2. Record the exact real outcome (pass/fail, counts, timing).
3. Update `PROJECT_STATE.md`, `STATUS.md`, and `HANDOFF.md`.
4. Append an entry to `CHECKPOINTS.md` with commit hash, branch, files touched, real test outputs, known limitations, and next steps.
5. Create a clean Git commit when appropriate.
