# Anantha Library – System Architecture (Final, Groq Edition)

**Version:** 2.1  
**Date:** May 21, 2026  
**Status:** Frozen – no changes without written approval

## 1. High‑Level Overview

Anantha Library is a spiritual web application that provides semantic search and conversational Q&A over the Bhagavad Gita using **Groq API** (cloud LLM) instead of a local model. The system is split into two independent parts:

- **Frontend:** TanStack Start (React) hosted on Vercel, with multi‑language UI and client‑side persistence (localStorage).  
  *Repository:* `anantha_ui`
- **Backend AI Service:** A lightweight DigitalOcean droplet running ChromaDB (vector search) and a Flask proxy that calls the **Groq API** (free tier).  
  *Repository:* `anantha_backend`

The frontend communicates with its own serverless API routes (Lovable / TanStack Start), which forward requests to the droplet. There is **no user authentication** – the “Enter Library” button is a mock entrance.

## 2. Data Flow (Chat Example)

User types message → Frontend calls `/api/chat` (Lovable API route)  
→ Lovable API route forwards to `http://<droplet-ip>:8000/chat`  
→ Flask server embeds query (sentence‑transformers)  
→ ChromaDB returns top‑k relevant verses  
→ Flask builds prompt and calls **Groq API** (llama‑3.3‑70b‑versatile)  
→ Groq returns answer with citations → Flask returns `{answer, citations}` → Lovable API route → Frontend displays

## 3. Components

### 3.1 Frontend (Lovable / TanStack Start)
- **Location:** Vercel (production), local development in PyCharm.
- **Repository:** `anantha_ui`
- **Key files:**
  - `src/routes/` – pages (landing, app, search, chat, library, wisdom)
  - `src/routes/api/` – serverless proxies (`search.ts`, `chat.ts`, `daily.ts`)
  - `src/lib/api.ts` – frontend client calling `/api/*`
  - `src/lib/i18n.ts` – multi‑language support (6 Indian languages)
- **Persistence:** localStorage for saved verses, journal, streak, language preference.
- **No database, no auth.**

### 3.2 Backend AI Service (DigitalOcean Droplet)
- **IP:** `142.93.7.31` (current)
- **Plan:** 4 GB RAM / 2 vCPUs ($24/month, covered by GitHub Student Pack)
- **Services:**
  - ChromaDB (persistent vector store at `/root/anantha_backend/chroma_db`)
  - Flask server (port 8000) with endpoints:
    - `POST /search` → returns top‑k verses (no LLM)
    - `POST /chat` → retrieves verses, calls **Groq API**, returns answer + citations
    - `GET /daily` → returns random verse + static reflection/practice
- **Code repository:** GitHub `anantha_backend` (cloned on droplet)

### 3.3 Proxy Layer (Lovable API Routes)
- Each route reads `AI_SERVICE_URL` environment variable.
- If the droplet is unreachable, they return mock data (fallback).

## 4. Deployment Diagram
[User Browser]
│
▼
[Vercel – Frontend (anantha_ui)]
│
│ calls /api/*
▼
[Lovable Serverless Functions] (same Vercel project)
│
│ HTTP to droplet:8000
▼
[DigitalOcean Droplet (anantha_backend)]
├─ Flask (port 8000)
├─ ChromaDB
├─ Git repo (cloned)
└─ (No local LLM – uses Groq API)
│
│ HTTPS
▼
[Groq Cloud] – llama-3.3-70b-versatile



## 5. Environment Variables

| Variable | Where | Value |
|----------|-------|-------|
| `AI_SERVICE_URL` | Vercel (frontend) | `http://142.93.7.31:8000` |
| `GROQ_API_KEY` | DigitalOcean droplet (Flask) | Your free Groq API key |
| No other secrets | – | – |

## 6. Security & Constraints

- No authentication – all pages public.
- All API calls are HTTP (no HTTPS on droplet – for MVP only; upgrade later with Let's Encrypt).
- Rate limiting: Groq free tier applies (30 RPM, 14,400 RPD). The Flask service does not add extra limits.
- Data privacy: user queries are sent to Groq (third party). Acceptable for MVP; can be replaced with self‑hosted later.
- User data (saved verses, journal) stays in browser localStorage – no collection by backend.

## 7. Failure Modes & Recovery

| Failure | Recovery |
|---------|----------|
| Droplet unreachable | Lovable API routes return mock data; UI remains functional. |
| Groq API key invalid or rate‑limited | Fallback to static message in Flask; rotate key or implement queue. |
| ChromaDB corrupted | Re‑run `python3 ingest.py` (needs a valid `gita_verses.json`). |
| Out of DigitalOcean credits | Move ChromaDB to a free tier (e.g., Pinecone) or downgrade to 2 GB droplet. |

## 8. Diagram (ASCII)
┌─────────────┐ ┌─────────────────┐ ┌──────────────────────────┐ ┌─────────────┐
│ Browser │────▶│ Vercel (Next) │────▶│ DigitalOcean Droplet │────▶│ Groq API │
│ (TanStack) │ │ /api/* proxies │ │ Flask :8000 │ │ (LLM cloud) │
└─────────────┘ └─────────────────┘ │ │ │ └─────────────┘
│ ├─ ChromaDB │
│ └─ (no local LLM) │
└──────────────────────────┘


## 9. Repositories


## 10. Approval

This document reflects the **final, deployed state** as of May 21, 2026.  
Any changes require written approval and must be reflected in both code repositories.