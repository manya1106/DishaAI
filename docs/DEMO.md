# Disha AI — Judging Demonstration Script (2:30 Walkthrough)

**Track:** Track 2 — Best Open-Source AI Project  
**Problem Statement:** O3 — Trustworthy and Verifiable AI  
**Demo URL:** Local: `http://localhost:3000` | Public: Vercel / Render

---

## Preparation Checklist
- [ ] Ensure backend is warmed up (`curl http://localhost:8000/health`).
- [ ] Open app in clean browser window at `http://localhost:3000/`.
- [ ] Keep trap test text ready: *"What is the exact monthly rent in rupees for #1?"*

---

## Timed Walkthrough

### 0:00–0:25 | The Problem & The Solution (Landing Page)
- **Do:** Stay on the landing page `/`.
- **Show:** The hero title, 3 Trust Pillars, and live metrics (0 leaked claims, 100% trap refusal).
- **Say:**
  > *"When entrepreneurs choose a business location today, they rely on gut feel or generative AI chatbots that hallucinate plausible-sounding rent and footfall numbers. Disha AI treats verifiable truth as an architectural primitive: our 9-signal engine calculates all scores deterministically from open data, and our AI is bounded strictly to narrating proven facts."*

### 0:25–0:55 | Deterministic Scoring & Synchronized Hex Heatmap (`/explore`)
- **Do:** Click **Launch Bengaluru Demo**. Choose **Café**, **Standard Budget**, click **Analyze**.
- **Show:**
  - MapLibre GL map with H3 hexagonal choropleth heatmap.
  - 10 numbered markers.
  - Left-hand ranked list.
  - Data honesty banner at bottom (*OpenStreetMap Snapshot, Heuristic Tiers*).
- **Say:**
  > *"Notice that scores are relative percentiles across Bengaluru urban cells. Clicking marker #1 flies to the Indiranagar corridor, highlights the ranked card, and opens the location report in real-time."*

### 0:55–1:25 | Transparent Provenance & Location Report
- **Do:** Review the Report tab for Location #1.
- **Show:**
  - 9 signal bars (competition density, gap opportunity, daytime population, transit access, etc.).
  - Explicit Provenance tags on every bar: `[measured]`, `[estimated]`, `[heuristic]`.
  - Strengths and limitations.
  - Collapsible **Raw OpenStreetMap Evidence Table** showing exact row IDs and counts.
- **Say:**
  > *"Every single signal has an explicit provenance tag. Direct counts from OSM are labelled measured; derived demand ratios are labelled estimated; rent feasibility is labelled heuristic. We never pretend unverified estimates are real market data."*

### 1:25–1:55 | Verified AI Chat & Interactive Evidence Drawer
- **Do:** Switch to the **Ask AI** tab. Click the suggested prompt: *"Why is #1 ahead of #2?"*
- **Show:**
  - Assistant response rendered as single-sentence blocks.
  - Green shield badge: `Verified (X/X claims)`.
  - Click on a **Claim Chip** (e.g. `[Score]`, `[Comparison]`).
  - The **Evidence Drawer** slides open, displaying the exact raw data row and citation record.
- **Say:**
  > *"Our AI doesn't calculate the score; it narrates the evidence bundle. Every sentence is split into claims, checked by our code-level verifier rules V1 through V9, and proven. When I click a claim chip, the Evidence Drawer shows the exact underlying data record."*

### 1:55–2:15 | The Trap Test: Refusal of Speculative Data
- **Do:** Click the trap prompt: *"What is the exact monthly rent in rupees for #1?"*
- **Show:**
  - The AI immediately refuses: `Refused (Insufficient Data)`.
  - Honest message explaining that Disha AI does not scrape private commercial leases and only tracks relative heuristic rent tiers.
- **Say:**
  > *"A standard LLM would invent ₹85,000/month without hesitation. Disha AI recognizes private financial data that doesn't exist in our verified snapshot and executes an honest refusal."*

### 2:15–2:30 | Trust Page & Open-Source Artifacts (`/trust`)
- **Do:** Navigate to `/trust`.
- **Show:**
  - Live evaluation metrics table (21 adversarial cases evaluated, 0 leaked claims).
  - V1–V9 verification pipeline diagram.
  - MIT License and GitHub repo link.
- **Say:**
  > *"Everything is open-source under the MIT license with a modular, swappable LLM adapter. That is Disha AI: verifiable, honest, and grounded location intelligence."*
