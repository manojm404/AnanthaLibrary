"""
Anantha Library Backend - Flask Application

This module serves as the primary API server for the Anantha Library project.
It implements a Retrieval-Augmented Generation (RAG) pipeline by:
1. Receiving user queries.
2. Searching a vector database (ChromaDB) for relevant sacred text passages.
3. Sending the context to an LLM (Groq) to generate a grounded response.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import random
import requests
from pathlib import Path
from collections import deque
from time import time, sleep
from threading import Lock

app = Flask(__name__)
# Enable CORS so the frontend can communicate with this API
CORS(app)

# Explicitly load .env from the backend directory, overriding existing env vars
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
VERSES_PATH = os.getenv("VERSES_PATH")  # optional override
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(Path(__file__).resolve().parent / "chroma_db"))
GROQ_RATE_LIMIT = int(os.getenv("GROQ_RATE_LIMIT", "30"))  # requests per minute (free tier)

# Simple in-memory rate limiting for Groq requests (per-process)
_groq_timestamps = deque()
_groq_lock = Lock()


def _wait_for_groq_slot():
    """Wait until a new Groq request is allowed under local rate limit."""
    window = 60.0
    while True:
        now = time()
        wait_time = 0
        with _groq_lock:
            # prune timestamps older than the sliding window
            while _groq_timestamps and (now - _groq_timestamps[0]) > window:
                _groq_timestamps.popleft()
            
            if len(_groq_timestamps) < GROQ_RATE_LIMIT:
                _groq_timestamps.append(now)
                return
            
            # calculate how long to wait for the oldest entry to expire
            wait_time = window - (now - _groq_timestamps[0])
        
        if wait_time > 0:
            # Sleep briefly and try again
            sleep(wait_time + 0.1)


def _call_groq(prompt: str, system_prompt: str = None, max_retries: int = 3, timeout: int = 30) -> str:
    """
    Calls the Groq API using an OpenAI-compatible payload.
    Includes exponential backoff and retries for network/rate limit issues.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    # Local rate limiting (pre-flight check)
    _wait_for_groq_slot()

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    backoff = 1.0
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.2, # Lower temperature for more grounded/less creative responses
            }
            resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=timeout)
            
            # Handle Groq specific rate limiting (429) or server issues (5xx)
            if resp.status_code == 429:
                sleep(backoff)
                backoff *= 2
                last_err = RuntimeError("Groq 429 Too Many Requests")
                continue
            if resp.status_code >= 500:
                sleep(backoff)
                backoff *= 2
                last_err = RuntimeError(f"Groq server error {resp.status_code}")
                continue
                
            resp.raise_for_status()
            body = resp.json()
            
            # Extract the message content from the OpenAI-compatible response format
            if "choices" in body and len(body["choices"]) > 0:
                return body["choices"][0]["message"]["content"]
            
            return json.dumps(body)
        except Exception as e:
            last_err = e
            sleep(backoff)
            backoff *= 2
            continue
    raise last_err or RuntimeError("Unknown error calling Groq")


def load_verses():
    """
    Attempts to load the sacred text verses from various possible locations.
    This data is used for local search fallbacks and as the source for ingestion.
    """
    candidates = []
    if VERSES_PATH:
        candidates.append(Path(VERSES_PATH))
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / "frontend" / "Anantha_Ui" / "src" / "data" / "verses.json")
    candidates.append(Path(__file__).resolve().parent / "verses.json")

    for p in candidates:
        try:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    # Minimal fallback data
    return [{"id": "fallback-1", "book_id": "gita", "book_title": "Bhagavad Gita", "text": "Wisdom is the bridge to peace."}]


VERSES = load_verses()


def search_verses(query: str, k: int = 5, book_id: str = None):
    """
    Core search logic for the RAG pipeline.
    Prioritizes semantic search via ChromaDB for better relevance.
    """
    if CHROMA_DB_PATH:
        try:
            import chroma_client
            # Semantic search finds verses with similar meaning, filtered by book
            return chroma_client.query(query, k=k, book_id=book_id, db_path=CHROMA_DB_PATH)
        except Exception as e:
            print("Chroma query failed, falling back to local search:", e)

    # Keyword search fallback
    q = (query or "").lower()
    if not q: return []
    scored = []
    for v in VERSES:
        if book_id and v.get("book_id") != book_id: continue
        text = (v.get("text") or "").lower()
        score = 0
        if q in text: score += 100
        score += sum(1 for tok in q.split() if tok and tok in text)
        if score > 0: scored.append((score, v))
    scored.sort(key=lambda x: -x[0])
    return [v for _s, v in scored[:k]]


@app.route("/books", methods=["GET"])
def get_books():
    """Returns a list of available books discovered from local data."""
    try:
        unique_books = {}
        for v in VERSES:
            bid = v.get("book_id")
            btitle = v.get("book_title")
            if bid and bid not in unique_books:
                unique_books[bid] = btitle or bid
        
        if not unique_books:
            return jsonify({"books": [{"id": "gita", "title": "Bhagavad Gita"}]})

        books = [{"id": bid, "title": btitle} for bid, btitle in unique_books.items()]
        return jsonify({"books": books})
    except Exception as e:
        print("Error fetching books:", e)
        return jsonify({"books": [{"id": "gita", "title": "Bhagavad Gita"}]})


@app.route("/search", methods=["POST"]) 
def search():
    """API endpoint for basic verse retrieval."""
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    book_id = data.get("book")
    k = int(data.get("k", 5))
    results = search_verses(query, k, book_id=book_id)
    return jsonify({"query": query, "results": results})


@app.route("/chat", methods=["POST"]) 
def chat():
    """
    Main RAG Chat Endpoint with strict persona enforcement.
    """
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("prompt") or data.get("query")
    book_id = data.get("book")
    k = int(data.get("k", 5))
    
    # Step 1: Retrieve context
    citations = search_verses(query, k, book_id=book_id)

    # Step 2: Build a Strict System-Level Instruction
    active_book = next((v.get("book_title") for v in citations if v.get("book_title")), "the Sacred Texts")
    
    system_instruction = (
        f"You are Anantha, a wise, serene, and compassionate guide for {active_book}. "
        "Your purpose is to provide guidance based STRICTLY on the verses provided in the context below. "
        "\nSTRICT PROTOCOLS:\n"
        "1. ONLY use the provided citations to form your answer.\n"
        "2. If the user's question cannot be answered using the citations, say: 'The verses I have retrieved do not directly address this, but let us consider the broader wisdom of duty and peace.'\n"
        "3. NEVER identify yourself as an AI, large language model, or computer. You are Anantha.\n"
        "4. DO NOT answer questions about math, coding, science, or general news. Gently tell the user your purpose is to discuss spiritual and dharmic paths.\n"
        "5. Use calm, poetic, and respectful language (e.g., 'Dear seeker,' 'Reflect upon this').\n"
        "6. If the user says 'hi' or 'hello', give a warm spiritual greeting and ask how you can help them navigate the current book."
    )

    context_block = "\n".join([f"- [{c.get('id')}]: {c.get('text')}" for c in citations])
    
    user_prompt = (
        f"CONTEXT CITATIONS:\n{context_block}\n\n"
        f"USER QUESTION: {query}"
    )

    # Step 4: Call LLM
    if GROQ_API_KEY:
        try:
            answer = _call_groq(user_prompt, system_prompt=system_instruction)
            # Cleanup prefixes
            clean_answer = answer.strip()
            if clean_answer.lower().startswith("anantha's response:"):
                clean_answer = clean_answer[19:].strip()
            
            return jsonify({"query": query, "content": clean_answer, "citations": citations})
        except Exception as e:
            print("Groq call failed:", e)

    # Fallback if offline
    fallback_responses = [
        "The wisdom of the ages reminds us that peace is found by steadying the mind. Act with devotion, and let stillness be your home.",
        "The self is eternal — untouched by sorrow or time. When you remember this, clarity returns.",
    ]
    
    q_lower = (query or "").strip().lower()
    if q_lower in ["hi", "hello", "namaste", "hey"]:
        answer_text = f"Namaste. I am Anantha, your guide to {active_book}. How can I assist your journey through these verses today?"
        citations = []
    else:
        answer_text = random.choice(fallback_responses) + "\n\n(Note: AI brain is currently in meditation/offline mode.)"

    return jsonify({"query": query, "content": answer_text, "citations": citations})


@app.route("/health", methods=["GET"])  
def health():
    """Check connectivity to dependencies like ChromaDB."""
    ok = {"ok": True}
    try:
        if CHROMA_DB_PATH:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            ok["chroma"] = "ok"
    except Exception:
        ok["chroma"] = "missing"
    return jsonify(ok)


@app.route("/daily", methods=["GET"]) 
def daily():
    """Returns a random verse for the 'Verse of the Day' feature."""
    book_id = request.args.get("book")
    pool = [v for v in VERSES if v.get("book_id") == book_id] if book_id else VERSES
    if not pool: pool = VERSES
    v = random.choice(pool)
    return jsonify({"verse": v})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
