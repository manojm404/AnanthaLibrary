# Anantha Library – Technical Stack

**Version:** 2.0  
**Last updated:** May 21, 2026

## 1. Frontend (Lovable / TanStack Start)

| Category | Technology | Version / Notes |
|----------|------------|------------------|
| Framework | TanStack Start | React, file‑based routing |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS + shadcn/ui | Glassmorphism, dark mode |
| State Management | Zustand + React Query | For server state (optional) |
| i18n | react-i18next | 6 languages (en, hi, ta, te, kn, ml) |
| Persistence | localStorage | Saved verses, journal, streak, language |
| Build Tool | Vite (via TanStack) | – |
| Hosting | Vercel | Free tier |

## 2. Backend AI Service (DigitalOcean)

| Category | Technology | Version / Notes |
|----------|------------|------------------|
| OS | Ubuntu | 24.04 LTS |
| LLM | Ollama + llama3.2:3b | 3B parameters, CPU‑only |
| Vector DB | ChromaDB | Persistent client, cosine similarity |
| Embeddings | sentence‑transformers | `all-MiniLM-L6-v2` (384 dim) |
| API Server | Flask | Python, single‑threaded |
| Process Manager | nohup (manual) | For MVP; later use systemd |
| Firewall | ufw | Port 8000 open |
| Version Control | Git | GitHub repository |

## 3. Data Sources

| Source | Format | Verses |
|--------|--------|--------|
| Bhagavad Gita | JSON | 700 verses (Sanskrit + English translation) |

The JSON file is stored in the backend repository (`gita_verses.json`). For MVP, a minimal 2‑verse version is acceptable; production should use full 700 verses.

## 4. API Communication

| Direction | Protocol | Data Format |
|-----------|----------|-------------|
| Frontend ↔ Lovable API routes | HTTP (same origin) | JSON |
| Lovable API routes ↔ Droplet | HTTP | JSON |

All endpoints use `POST` for search/chat, `GET` for daily.

## 5. Development Tools

| Tool | Purpose |
|------|---------|
| PyCharm | Frontend (Lovable project) |
| Terminal / SSH | Droplet management |
| GitHub | Backend repo |
| Vercel CLI | Frontend deployment |
| curl / Postman | API testing |

## 6. Cost (Zero Budget using GitHub Student Pack)

| Service | Monthly Cost | Covered By |
|---------|--------------|-------------|
| DigitalOcean droplet (8GB/4vCPU) | $48 | Student Pack ($200 credit) – ~4 months |
| Vercel (frontend) | $0 | Free tier |
| Ollama / Chroma | $0 | – |
| Domain (optional) | $0 | Namecheap via Student Pack (1 year) |

After credits expire, options:
- Reduce droplet to 4GB/2vCPU ($24/month)
- Add donations / premium features
- Migrate to free LLM API (Groq)