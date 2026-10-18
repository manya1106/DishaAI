# Disha AI — Judging Demonstration Script (3:00 Walkthrough)

**Track:** Track 2 — Best Open-Source AI Project
**Primary Problem Statement:** O1 — Autonomous Agent Swarms
**Carried-over differentiator:** O3 — Trustworthy and Verifiable AI (the swarm's own internal accountability layer — see `docs/BLUEPRINT.md` §C)
**Demo URL:** Local: `http://localhost:3000` | Public: Vercel / Render (pending link, see `docs/DEPLOY.md`)

---

## Preparation Checklist
- [ ] Postgres running: `docker compose up -d` (repo root), confirm healthy: `docker compose ps`.
- [ ] Backend warmed up (`curl http://localhost:8000/health` → `"data_mode": "postgres"`).
- [ ] Open app in a clean browser window at `http://localhost:3000/`.
- [ ] Keep trap test text ready: *"What is the exact monthly rent in rupees for #1?"*
- [ ] Keep a follow-up question ready to trigger an LLM/deterministic hand-off for the Agent Trace beat: *"Why is #1 ranked at the top?"*

---

## Timed Walkthrough

### 0:00–0:20 | The Problem & The Solution (Landing Page)
- **Do:** Stay on the landing page `/`.
- **Show:** The hero title, 3 Trust Pillars, and live metrics (0 leaked claims, 100% trap refusal).
- **Say:**
  > *"When entrepreneurs choose a business location today, they rely on gut feel or generative AI chatbots that hallucinate plausible-sounding rent and footfall numbers. Disha AI is an autonomous agent swarm — a Scoring Agent, a Narrator Agent, and a Verifier Agent, coordinated by an Orchestrator — where one agent's job is to refuse another agent's output if it isn't grounded. Nothing reaches the user unchecked."*

### 0:20–0:50 | Deterministic Scoring Over Real Data (`/explore`)
- **Do:** Click **Launch Bengaluru Demo**. Choose **Café**, **Standard Budget**, click **Analyze**.
- **Show:**
  - MapLibre GL map with H3 hexagonal choropleth heatmap, now covering **all of Bengaluru**, not just the central core.
  - 10 numbered markers, drawn from real OpenStreetMap data (1,630 H3 cells, 1,382 eligible, 36,000+ real points of interest with real OSM IDs).
  - Left-hand ranked list.
  - Data honesty banner at bottom (OpenStreetMap, real POIs, heuristic rent tiers).
- **Say:**
  > *"This isn't a toy snapshot — it's a live PostGIS database seeded from a real OpenStreetMap pull of greater Bengaluru. Scores are relative percentiles across every eligible cell. Clicking a marker flies to that zone, highlights the ranked card, and opens the location report in real time."*

### 0:50–1:15 | Transparent Provenance & Location Report
- **Do:** Review the Report tab for Location #1.
- **Show:**
  - 9 signal bars (competition density, gap opportunity, daytime population, transit access, etc.).
  - Explicit provenance tags on every bar: `[measured]`, `[estimated]`, `[heuristic]`.
  - Strengths and limitations.
  - Collapsible raw OpenStreetMap evidence table showing exact row IDs and counts.
- **Say:**
  > *"Every signal has an explicit provenance tag. Direct counts from OSM are labelled measured; derived demand ratios are labelled estimated; rent feasibility is labelled heuristic. The Scoring Agent that computed this never talks to the LLM at all — it's pure deterministic math."*

### 1:15–1:50 | Verified AI Chat & the Agent Trace (the O1 moment)
- **Do:** Switch to the **Ask AI** tab. Ask: *"Why is #1 ranked at the top?"*
- **Show:**
  - Assistant response rendered as single-sentence blocks with a green `Verified` badge.
  - Click the new **Agent Trace** toggle next to the badge.
  - The hand-off sequence expands inline: `verifier(build_bundle) → narrator(draft) → verifier(check)` — the literal Orchestrator dispatch log for this exact request.
- **Say:**
  > *"This is the swarm working, not a diagram of it. The Orchestrator asked the Verifier Agent to build the grounding bundle, asked the Narrator Agent to draft an explanation from it, then sent that draft back to the Verifier Agent before anything reached you. You're looking at the actual trace, not a mockup."*

### 1:50–2:10 | Interactive Evidence Drawer
- **Do:** Click a **Claim Chip** on the response (e.g. `[Score]`, `[Comparison]`).
- **Show:** The Evidence Drawer slides open, displaying the exact raw data row and citation record.
- **Say:**
  > *"Every sentence is split into claims, checked by code-level verifier rules V1 through V9, and traceable to one exact evidence row. Click any claim, see the number it came from."*

### 2:10–2:35 | The Trap Test: Refusal of Speculative Data
- **Do:** Click the trap prompt: *"What is the exact monthly rent in rupees for #1?"*
- **Show:**
  - The AI immediately refuses: `Refused (Insufficient Data)`.
  - Honest message explaining that Disha AI does not scrape private commercial leases and only tracks relative heuristic rent tiers.
  - Open the Agent Trace for this response too — it's a single `verifier` hand-off, because the refusal short-circuits before the Narrator Agent is even invoked.
- **Say:**
  > *"A standard LLM would invent ₹85,000/month without hesitation. Here, the Orchestrator refuses before the Narrator Agent is ever dispatched — you can see that in the trace: it never even got the chance to draft a hallucination."*

### 2:35–3:00 | Trust Page & Open-Source Artifacts (`/trust`)
- **Do:** Navigate to `/trust`.
- **Show:**
  - Live evaluation metrics table (21 adversarial cases evaluated, 0 leaked claims).
  - V1–V9 verification pipeline diagram.
  - MIT License and GitHub repo link.
- **Say:**
  > *"Everything is open-source under the MIT license, with a modular, swappable LLM adapter and four agents you can inspect individually. That's Disha AI: an autonomous swarm that polices itself, grounded in real geospatial data."*
