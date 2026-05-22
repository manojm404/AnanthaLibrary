# System Architecture – Anantha Library

Anantha Library follows a decoupled, dynamic architecture designed to scale across an unlimited number of sacred texts while maintaining a sleek, privacy-focused user experience.

---

## 🏗️ 1. High-Level Overview

The system uses a **Client-Server-AI** pattern. The frontend remains agnostic of the specific books available, dynamically synchronizing its state with the backend's vector database.

```mermaid
graph TD
    Browser[User Browser] -->|HTTPS| Frontend[Vercel: TanStack Start UI]
    Frontend -->|Dynamic Book Discovery| API_Books[/api/books]
    Frontend -->|Context-Filtered Query| API_Search[/api/search]
    API_Search -->|Metadata Filter| ChromaDB[(ChromaDB: Vector DB)]
    API_Search -->|Contextual Prompt| Groq[Groq API: Llama-3]
    Groq -->|Dynamic Answer| API_Search
    API_Search -->|Answer + Audio + Citations| Frontend
```

---

## 🧠 2. The Dynamic RAG Pipeline

The "brain" of the system is a context-aware **Retrieval-Augmented Generation** pipeline that supports multiple datasets simultaneously.

1.  **Selection:** The user selects a book (e.g., *Bhagavad Gita* or *Ramayana*) via the UI.
2.  **Input:** User asks a question: *"What is the path to peace?"*
3.  **Embedding & Filtering:** The backend converts the query into a vector and queries ChromaDB with a `where={"book_id": "active_book"}` metadata filter.
4.  **Retrieval:** ChromaDB returns the top 5 most relevant passages strictly from the selected book.
5.  **Augmentation:** The system builds a strict instruction prompt:
    > "You are Anantha, a guide for [Book Title]. Use ONLY the following citations to answer: [Citations]. User: [Question]"
6.  **Generation:** Groq generates a conversational response grounded in the retrieved text.
7.  **Response:** The answer is delivered with original Sanskrit, translations, and **Audio URLs** if available.

---

## 🗄️ 3. Data Architecture

-   **Vector Database (ChromaDB):** Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings. Data is stored persistently with metadata keys: `book_id`, `book_title`, `chapter`, `verse`, and `audio_url`.
-   **Dynamic Ingestion:** A Registry-based Python script (`ingest.py`) allows developers to map any HuggingFace dataset columns into the unified Anantha schema.
-   **Client Storage:** `localStorage` is used for bookmarks, journal entries, and the "last active book" setting.

---

## 🛡️ 4. Resilience & Security

-   **Server-Side Proxying:** All AI and database calls are proxied through TanStack Start's server handlers (`ai-proxy.server.ts`). This prevents the leakage of the DigitalOcean IP address and the Groq API key to the client.
-   **Sliding-Window Rate Limiting:** A thread-safe Python implementation ensures the backend never crashes due to Groq's 30 RPM limit. It pauses requests and executes them as slots become available.
-   **Graceful Degradation:** If the backend droplet is down, the frontend switches to **Offline Mode**, utilizing a local `verses.json` cache and keyword search to maintain a functional experience.

---

## ⚙️ 5. Deployment Workflow

-   **Frontend:** Auto-deployed via **Vercel** on every push to `main`.
-   **Backend:** Python 3.x environment running on a **DigitalOcean Droplet**, managed via a Systemd service (recommended for production).
-   **AI Inference:** **Groq Cloud** for sub-second Llama-3 responses.
