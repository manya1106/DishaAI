# Disha AI — Deployment Guide

This guide details how to deploy Disha AI to public HTTPS endpoints on **Render** (Backend) and **Vercel** (Frontend).

---

## 1. Architecture Overview

```text
 Browser (User)
       │
       ▼ HTTPS
 Vercel (Next.js Frontend)
   • Route: /
   • Route: /explore
   • Route: /trust
   • Client config: NEXT_PUBLIC_API_URL
       │
       ▼ HTTPS REST API (CORS enabled)
 Render (FastAPI Backend)
   • GET  /health
   • GET  /api/v1/meta
   • POST /api/v1/analyses
   • POST /api/v1/analyses/{id}/chat
   • GET  /api/v1/trust/stats
   • Data: Built-in Bengaluru OpenStreetMap Snapshot (in-memory)
   • Engine: Deterministic 9-Signal Scoring & V1-V9 Claim Verifier
```

---

## 2. Deploying the Backend (Render)

1. **Create Web Service**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New + > Web Service**.
   - Connect GitHub repository: `https://github.com/manya1106/DishaAI`.
2. **Build Configuration**:
   - **Name:** `disha-api` (or similar)
   - **Root Directory:** `apps/api`
   - **Environment:** `Python` (or `Docker`)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
3. **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `APP_ENV` | `production` | Production environment flag |
   | `DATA_MODE` | `snapshot` | Uses verified Bengaluru snapshot |
   | `CORS_ORIGINS` | `https://<your-vercel-domain>.vercel.app,http://localhost:3000` | Allowed web origins |
   | `LLM_ENABLED` | `false` (or `true`) | Set to `true` if supplying an LLM key |
   | `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint |
   | `LLM_API_KEY` | *(optional)* | Provider key if LLM enabled |
   | `LLM_MODEL` | `llama-3.1-8b-instant` | Model identifier |
4. **Deploy**:
   - Click **Create Web Service**.
   - Once deployed, test in browser: `https://<your-service>.onrender.com/health` (should return `{"status":"ok",...}`).

---

## 3. Deploying the Frontend (Vercel)

1. **Import Project**:
   - Go to [vercel.com/new](https://vercel.com/new).
   - Select repository `manya1106/DishaAI`.
2. **Configure Project**:
   - **Project Name:** `disha-ai`
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click **Edit** and set to `apps/web`.
3. **Environment Variables**:
   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://<your-render-service>.onrender.com` |
   | `NEXT_PUBLIC_API_MOCK` | `0` |
4. **Deploy**:
   - Click **Deploy**.
   - Once completed, Vercel gives you a public domain (e.g. `https://disha-ai.vercel.app`).
5. **Update CORS on Render**:
   - Copy your Vercel domain and update `CORS_ORIGINS` on Render:
     `CORS_ORIGINS=https://disha-ai.vercel.app,http://localhost:3000`
   - Save changes on Render.

---

## 4. Verifying Public Deployment

Run the automated smoke test suite:
```bash
bash scripts/smoke_public.sh https://disha-ai.vercel.app https://disha-api.onrender.com
```

Checks verified:
- [x] `/health` returns status: ok
- [x] `/api/v1/meta` loads categories and Bengaluru coordinates
- [x] `POST /api/v1/analyses` computes 10 locations with 9 signals
- [x] Speculative trap question refused (`refused_insufficient_data`)
- [x] CORS headers permit Vercel origin
- [x] No secrets present in source code or repository
