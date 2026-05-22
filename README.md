# 🕉️ Anantha Library

Anantha Library is a highly scalable, AI-powered spiritual companion for exploring the vast wisdom of Sanatana Dharma. Initially built for the **Bhagavad Gita**, it has evolved into a multi-text platform using **Retrieval-Augmented Generation (RAG)** to provide semantic search, conversational guidance, and audio recitations for various sacred texts including the Ramayana, Mahabharata, and Puranas.

---

## ✨ Key Features

- **🧠 Multi-Text AI Chat:** Converse with "Anantha," an AI guide that dynamically adapts its wisdom based on the book you select (Gita, Ramayana, etc.).
- **📖 Dynamic Book Selector:** A unified UI that automatically detects and lists all ingested sacred texts from the backend.
- **🔍 Context-Aware Semantic Search:** Find verses and passages by meaning, feeling, or reference, isolated specifically to your chosen book.
- **🔊 Sanskrit Audio Integration:** Listen to the eternal vibrations of Sanskrit chanting directly within the verse cards.
- **📅 Personalized Daily Wisdom:** Receive a "Verse of the Day" filtered by your active book to ground your daily practice.
- **📚 Local Library & Journaling:** Save favorites and record your reflections privately in your browser.

---

## 🛠️ Tech Stack

### Frontend (The Interface)
- **Framework:** TanStack Start (React + TypeScript)
- **Styling:** Tailwind CSS + shadcn/ui (Glassmorphism design)
- **State Management:** React Context (LibraryProvider) for dynamic book synchronization.
- **Persistence:** LocalStorage for privacy-first user data.

### Backend (The AI Engine)
- **API Server:** Flask (Python)
- **Vector Database:** ChromaDB (Multi-collection ready with metadata filtering)
- **Embeddings:** `sentence-transformers` (all-MiniLM-L6-v2)
- **LLM Engine:** Groq API (Blazing-fast Llama-3 inference)
- **Data Ingestion:** Dynamic Python pipeline supporting any HuggingFace dataset.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/manojm404/AnanthaLibrary.git
cd AnanthaLibrary
```

### 2. Backend Setup
1. Create a virtual environment: `python3 -m venv .venv_backend && source .venv_backend/bin/activate`
2. Install deps: `pip install -r backend/anantha_backend/requirements.txt`
3. Add your Groq API key in `backend/anantha_backend/.env`:
   ```text
   GROQ_API_KEY=your_gsk_key_here
   ```
4. **Dynamic Ingestion:**
   ```bash
   # Ingest the Gita
   python backend/anantha_backend/ingest.py --book gita --fetch --ingest
   
   # Ingest the Ramayana (Example)
   python backend/anantha_backend/ingest.py --book ramayana --fetch --ingest
   ```
5. Start the server: `FLASK_APP=backend/anantha_backend/app.py flask run --port=8000`

### 3. Frontend Setup
1. `cd frontend/Anantha_Ui`
2. `npm install`
3. `echo "VITE_AI_SERVICE_URL=http://127.0.0.1:8000" > .env`
4. `npm run dev`

---

## 📖 Detailed Documentation
- [System Architecture](./docs/Architecture.md)
- [How We Built It (Cheat Sheet)](./docs/how_we_did.md)
- [Technical Stack](./docs/Technical_stack.md)
