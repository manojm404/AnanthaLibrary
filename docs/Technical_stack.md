# Anantha Library – Technical Stack

**Version:** 3.0 (Multi-Text Edition)  
**Last updated:** May 21, 2026

## 1. Frontend (TanStack Start)

| Category | Technology | Purpose |
|----------|------------|---------|
| Framework | TanStack Start | Hybrid SSR/SPA with type-safe routing |
| Language | TypeScript 5.x | Core application logic |
| UI Components | shadcn/ui + Lucide | Reusable, accessible UI elements |
| Styling | Tailwind CSS | Glassmorphism and responsive layout |
| State Management | React Context (LibraryProvider) | Active book synchronization |
| Audio | HTML5 Audio API | Integrated Sanskrit recitation player |
| Hosting | Vercel | Production deployment |

## 2. Backend (AI Service)

| Category | Technology | Purpose |
|----------|------------|---------|
| Runtime | Python 3.9+ | Main service execution |
| API Framework | Flask | RESTful endpoint management |
| Vector DB | ChromaDB | Semantic vector storage and filtering |
| Embeddings | sentence-transformers | `all-MiniLM-L6-v2` (384 dimensions) |
| LLM API | Groq (Llama-3) | High-speed contextual reasoning |
| Rate Limiter | Sliding-Window (In-Memory) | API stability management |
| Data Processing | `datasets` (HuggingFace) | Dynamic ingestion pipeline |

## 3. Data Sources

| Book | ID | Source |
|------|----|--------|
| Bhagavad Gita | `gita` | `JDhruv14/Bhagavad-Gita_Dataset` |
| Ramayana | `ramayana` | `SatyaSanatan/...` (and similar HF datasets) |
| *Scalable* | *Any* | Any standardized HuggingFace CSV/JSON |

## 4. API Communication

- **Frontend → Proxy:** `/api/chat`, `/api/search`, `/api/books`, `/api/daily` (Standard TanStack Server Handlers).
- **Proxy → Backend:** Direct HTTP communication to DigitalOcean Droplet (Hidden from client).
- **Backend → AI:** Secure authenticated requests to Groq Cloud.

## 5. Development Infrastructure

- **Version Control:** Git (managed on GitHub).
- **Package Managers:** `npm` (Frontend), `pip` (Backend).
- **Environments:** `.env` files for secure credential isolation.
- **CI/CD:** GitHub Actions for automated testing.

## 6. Project Roadmap

- [x] **Phase 1:** Core Gita MVP.
- [x] **Phase 2:** RAG Integration & Groq support.
- [x] **Phase 3:** Multi-book dynamic architecture & Audio.
- [ ] **Phase 4:** User Authentication & Cloud Sync.
- [ ] **Phase 5:** Mobile App (React Native).
