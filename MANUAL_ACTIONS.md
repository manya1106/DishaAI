# Manual Actions Required from Human Project Owner

| # | Action | Reason | Exact Steps | Required Value | Where to Obtain | Status | Verification |
|---|---|---|---|---|---|---|---|
| 1 | Push code to GitHub repository | Allow remote tracking and deployment integration (Vercel/Render) | Run `git push -u origin main` once initial commit is prepared | Git push authorization | GitHub CLI / SSH keys / PAT | **Ready for user** (once initial baseline commit is made) | `git status` shows branch up to date with `origin/main` |
| 2 | LLM Provider API Key (Optional for hosted LLM) | Enable live open-weight LLM responses in addition to the deterministic engine | Add `LLM_API_KEY` to `.env` or Render environment | `LLM_API_KEY`, `LLM_BASE_URL` (Groq/OpenRouter/HuggingFace) | Free-tier provider dashboard | **Optional** (system functions fully with built-in deterministic narrator if omitted) | Backend `/health` reports `llm: configured` |
| 3 | Render / Vercel Project Linking | Deploy the application live to public HTTPS URLs | Connect GitHub repo `manya1106/DishaAI` on Vercel (for `apps/web`) and Render (for `apps/api`) | Vercel & Render project setups | Vercel dashboard & Render dashboard | **Upcoming** (milestone M5) | Public URLs return 200 OK |
