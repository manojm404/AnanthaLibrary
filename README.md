# 🕉️ Anantha Library

Anantha Library is a modern, AI-powered spiritual companion for exploring the **Bhagavad Gita**. Using **Retrieval-Augmented Generation (RAG)**, Anantha provides semantic search and a conversational interface, allowing users to ask life questions and receive guidance grounded in the eternal wisdom of the Gita.

---

## ✨ Key Features

- **🧠 Conversational AI:** Chat with "Anantha," an AI guide that retrieves relevant verses from the Bhagavad Gita to answer your personal questions.
- **🔍 Semantic Search:** Find verses by meaning and emotion (e.g., searching for "anxiety" or "purpose") rather than just keywords.
- **🔊 Sanskrit Audio Integration:** Listen to the eternal vibrations of Sanskrit chanting directly within the verse cards.
- **📅 Daily Wisdom:** A dedicated page for a "Verse of the Day" with reflection and practice prompts.
- **📚 Personal Library:** Save your favorite verses to a local library for offline study.
- **🌐 Multi-Language Support:** Full support for Sanskrit, English, and Hindi translations.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** TanStack Start (React + TypeScript)
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** TanStack Query + React Hooks
- **Persistence:** LocalStorage for user preferences and saved verses.

### Backend (The AI Engine)
- **API Server:** Flask (Python)
- **Vector Database:** ChromaDB (for semantic similarity searching)
- **Embeddings:** `sentence-transformers` (all-MiniLM-L6-v2)
- **LLM Engine:** Groq API (running Llama-3.3-70b-versatile)
- **Dataset:** `JDhruv14/Bhagavad-Gita_Dataset` (HuggingFace)

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
4. Ingest the data: 
   ```bash
   python backend/anantha_backend/ingest.py --fetch --ingest
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
