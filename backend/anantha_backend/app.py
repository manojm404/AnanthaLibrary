"""
Anantha Library Backend - Flask Application

This module serves as the primary API server for the Anantha Library project.
It implements a Retrieval-Augmented Generation (RAG) pipeline by:
1. Receiving user queries.
2. Searching for relevant Bhagavad Gita verses (using semantic search via ChromaDB or local fallback).
3. Constructing a context-rich prompt for the Groq LLM.
4. Returning the LLM's response along with citations.
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

# Load environment variables from .env file for configuration
# This includes API keys, model names, and database paths.
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Configuration for Groq API and ChromaDB
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
VERSES_PATH = os.getenv("VERSES_PATH")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
GROQ_RATE_LIMIT = int(os.getenv("GROQ_RATE_LIMIT", "30"))  # Default to 30 requests per minute

# Thread-safe rate limiting for Groq API calls to avoid 429 errors on free tiers
_groq_timestamps = deque()
_groq_lock = Lock()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend communication


def _wait_for_groq_slot():
    """
    Implements a sliding window rate limiter.
    Ensures that we don't exceed the configured requests per minute (GROQ_RATE_LIMIT).
    If the limit is reached, it blocks the thread until a slot becomes available.
    """
    window = 60.0
    while True:
        now = time()
        wait_time = 0
        with _groq_lock:
            # Remove timestamps older than the 60-second window
            while _groq_timestamps and (now - _groq_timestamps[0]) > window:
                _groq_timestamps.popleft()
            
            # If under the limit, record the new request and proceed
            if len(_groq_timestamps) < GROQ_RATE_LIMIT:
                _groq_timestamps.append(now)
                return
            
            # Calculate wait time based on the oldest request in the window
            wait_time = window - (now - _groq_timestamps[0])
        
        if wait_time > 0:
            sleep(wait_time + 0.1)


def _call_groq(prompt: str, max_retries: int = 3, timeout: int = 30) -> str:
    """
    Wrapper for calling the Groq API with error handling and exponential backoff.
    This function manages the communication with the Large Language Model.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    _wait_for_groq_slot()

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    backoff = 1.0
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=timeout)
            
            # Handle rate limiting from the API side
            if resp.status_code == 429:
                sleep(backoff)
                backoff *= 2
                last_err = RuntimeError("Groq 429 Too Many Requests")
                continue
            
            # Handle temporary server errors
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
    Attempts to load the Bhagavad Gita verses from various possible locations.
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
    # Minimal fallback data if no file is found
    return [
        {"id": "gita:1:1", "text": "Dhritarashtra said: O Sanjaya, what did my sons and the Pandavas do?"},
        {"id": "gita:1:2", "text": "Sanjaya said: On the field of Kurukshetra, great battle took place..."},
    ]

VERSES = load_verses()

# Semantic search path configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", None)


def search_verses(query: str, k: int = 5):
    """
    Core search logic for the RAG pipeline.
    Prioritizes semantic search via ChromaDB for better relevance.
    Falls back to simple keyword-based search if ChromaDB is unavailable.
    """
    if CHROMA_DB_PATH:
        try:
            import chroma_client
            # Semantic search finds verses with similar meaning, even if words don't match exactly
            return chroma_client.query(query, k=k, db_path=CHROMA_DB_PATH)
        except Exception as e:
            print("Chroma query failed, falling back to local search:", e)

    # Naive keyword search: calculates a basic score based on term frequency and word overlap
    q = (query or "").lower()
    if not q:
        return []
    scored = []
    for v in VERSES:
        text = (v.get("text") or "").lower()
        score = 0
        if q in text:
            score += 100
            score += text.count(q)
        score += sum(1 for tok in q.split() if tok and tok in text)
        if score > 0:
            scored.append((score, v))
    scored.sort(key=lambda x: -x[0])
    return [v for _s, v in scored[:k]]


@app.route("/search", methods=["POST"]) 
def search():
    """API endpoint for basic verse retrieval based on a query."""
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    k = int(data.get("k", 5))
    results = search_verses(query, k)
    return jsonify({"query": query, "results": results})


@app.route("/chat", methods=["POST"]) 
def chat():
    """
    Main RAG Chat Endpoint.
    1. Retrieves top K relevant verses (the 'Retrieval' in RAG).
    2. Packages these verses as 'Citations' for the LLM prompt.
    3. Requests an answer from Groq based on the context (the 'Augmented Generation').
    """
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("prompt") or data.get("query")
    k = int(data.get("k", 5))
    
    # Step 1: Retrieve context (verses)
    citations = search_verses(query, k)

    # Step 2: Build Augmented Prompt
    # We provide the verses as grounded facts to the LLM to minimize hallucinations.
    prompt_lines = [f"User: {query}", "", "Citations:"]
    for c in citations:
        cid = c.get("id") if isinstance(c, dict) else c.get("id")
        text = c.get("text") if isinstance(c, dict) else c.get("text")
        prompt_lines.append(f"- {cid}: {text}")
    prompt_lines.append("")
    prompt_lines.append("Answer:")
    prompt = "\n".join(prompt_lines)

    # Step 3: Call LLM
    if GROQ_API_KEY:
        try:
            answer = _call_groq(prompt)
            return jsonify({"query": query, "content": answer, "citations": citations})
        except Exception as e:
            print("Groq call failed:", e)

    # Fallback to predefined responses if the LLM is unavailable or unconfigured
    fallback_responses = [
        "The Gita reminds us that peace is found not in changing the world, but in steadying the mind. Act with devotion, release the fruits, and let stillness become your foundation.",
        "Krishna teaches Arjuna that the self is eternal — untouched by sorrow, fire, or time. When you remember this, fear softens and clarity returns.",
        "Equanimity in success and failure is the heart of yoga. Begin small: notice when you grasp at outcomes, and gently return to the present action."
    ]
    
    q_lower = (query or "").strip().lower()
    if q_lower in ["hi", "hello", "namaste", "hey", "greetings"]:
        answer_text = "Namaste. I am Anantha — your companion to the Bhagavad Gita. Ask me about a verse, a feeling you're working through, or a question life has placed before you."
        citations = []
    else:
        answer_text = random.choice(fallback_responses) + "\n\n(Note: I am currently running in offline mode. For dynamic answers, please configure the GROQ_API_KEY in the backend.)"

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
    v = random.choice(VERSES)
    return jsonify({"verse": v})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
