# AGENTS.md — Non-Negotiable Project Rules & Role Boundaries

## Core Rules for All Work

1. **Read `docs/BLUEPRINT.md`** before making architectural changes.
2. **Deterministic scoring is the single source of truth**: The AI does not compute scores or invent rankings; it strictly narrates the calculated evidence bundle.
3. **Contracts are sacred**: Only Lead/Architect updates `contracts/` and `apps/api/app/schemas/`. Other components consume generated TypeScript types or Pydantic models.
4. **Data honesty**: Never fabricate real-world outcomes, rupee rents, or fake footfall numbers. Every data point and signal carries an explicit provenance tag (`measured`, `estimated`, `heuristic`, `simulated`, `unavailable`).
5. **No secret leaks**: Never commit API keys or credentials. Use `.env.example` for template variables.
6. **Graceful degradation**:
   - If DB is unavailable, store traces in-memory without breaking requests.
   - If LLM is unavailable or unconfigured, use deterministic fallback.
   - If external OSM fails, use local verified snapshot/synthetic fixture with `simulated` label.
7. **Verification over generation**: All LLM claims must pass verifier rules V1–V9. Unverified claims are excised; failing responses degrade to deterministic narrative.
8. **Definition of Done**: Code is tested with unit tests, runs locally without crashes, passes contract checks, and has clear verification output.

## File Ownership
- **Lead / Architect**: `contracts/**`, `apps/api/app/schemas/**`, `docs/**`, `AGENTS.md`, `.env.example`, `Makefile`
- **Frontend**: `apps/web/**` (except generated `src/types/api.ts`)
- **Backend & Data**: `apps/api/app/{main,config,logging,errors}.py`, `apps/api/app/scoring/**`, `apps/api/app/data/**`, `apps/api/app/routers/**` (except chat/trust), `apps/api/app/db/**`
- **AI & Trust**: `apps/api/app/ai/**`, `apps/api/app/routers/{chat,trust}.py`, `scripts/{check_llm,eval_trust}.py`, `data/eval/**`
- **QA & Deployment**: `apps/web/e2e/**`, `apps/api/tests/**`, `apps/api/Dockerfile`, `scripts/smoke_public.sh`, `README.md`, `docs/DEPLOY.md`
