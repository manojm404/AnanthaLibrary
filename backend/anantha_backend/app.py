"""Simple Flask backend scaffold for Anantha Library.
Endpoints:
- POST /search  { query: string, k?: number }
- POST /chat    { query: string, k?: number }
- GET  /daily

This is a starting point. Replace the placeholder Groq call with production-ready request formatting
and wire up ChromaDB for real vector search.
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

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = os.getenv("GROQ_API_URL", f"https://api.groq.ai/v1/models/{GROQ_MODEL}/outputs")
VERSES_PATH = os.getenv("VERSES_PATH")  # optional override
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
GROQ_RATE_LIMIT = int(os.getenv("GROQ_RATE_LIMIT", "30"))  # requests per minute (free tier)

# Simple in-memory rate limiting for Groq requests (per-process)
_groq_timestamps = deque()
_groq_lock = Lock()

app = Flask(__name__)
CORS(app)


def _allow_groq_request() -> bool:
    """Return True if a new Groq request is allowed under rate limit."""
    now = time()
    window = 60.0
    with _groq_lock:
        # prune old
        while _groq_timestamps and (now - _groq_timestamps[0]) > window:
            _groq_timestamps.popleft()
        if len(_groq_timestamps) < GROQ_RATE_LIMIT:
            _groq_timestamps.append(now)
            return True
        return False


def _call_groq(prompt: str, max_retries: int = 3, timeout: int = 30) -> str:
    """Call Groq API with exponential backoff. Returns string answer or raises Exception."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    if not _allow_groq_request():
        raise RuntimeError("Groq rate limit exceeded (local quota)")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    backoff = 1.0
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            payload = {"input": prompt}
            resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                # rate limited by Groq — backoff and retry
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
            # Try common keys
            if isinstance(body, dict):
                if "output" in body:
                    return body["output"] if isinstance(body["output"], str) else json.dumps(body["output"])
                if "outputs" in body and isinstance(body["outputs"], list) and body["outputs"]:
                    out = body["outputs"][0]
                    if isinstance(out, dict) and "content" in out:
                        return out["content"]
                    return json.dumps(out)
                if "result" in body:
                    return body["result"] if isinstance(body["result"], str) else json.dumps(body["result"])
                if "choices" in body and isinstance(body["choices"], list) and body["choices"]:
                    c = body["choices"][0]
                    if isinstance(c, dict) and "text" in c:
                        return c["text"]
                    return json.dumps(c)
            # Fallback: stringified body
            return json.dumps(body)
        except Exception as e:
            last_err = e
            sleep(backoff)
            backoff *= 2
            continue
    raise last_err or RuntimeError("Unknown error calling Groq")

# Try to locate verses JSON from frontend if available
def load_verses():
    # Typical path: repo_root/Anantha_Ui/src/data/verses.json
    candidates = []
    if VERSES_PATH:
        candidates.append(Path(VERSES_PATH))
    repo_root = Path(__file__).resolve().parents[1]
    candidates.append(repo_root / "frontend" / "Anantha_Ui" / "src" / "data" / "verses.json")
    candidates.append(Path(__file__).resolve().parent / "verses.json")

    for p in candidates:
        try:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    # Fallback: minimal mock verses
    return [
        {"id": "gita:1:1", "text": "Dhritarashtra said: O Sanjaya, what did my sons and the Pandavas do?"},
        {"id": "gita:1:2", "text": "Sanjaya said: On the field of Kurukshetra, great battle took place..."},
    ]

VERSES = load_verses()


# Prefer semantic search via ChromaDB when available
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", None)


def search_verses(query: str, k: int = 5):
    # If ChromaDB is configured, use semantic search
    if CHROMA_DB_PATH:
        try:
            from . import chroma_client
        except Exception:
            # chroma_client import failed; fall back to local search
            pass
        else:
            try:
                return chroma_client.query(query, k=k, db_path=CHROMA_DB_PATH)
            except Exception as e:
                print("Chroma query failed, falling back to local search:", e)

    # Fallback naive text search
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
        # small boost for word overlap
        score += sum(1 for tok in q.split() if tok and tok in text)
        if score > 0:
            scored.append((score, v))
    scored.sort(key=lambda x: -x[0])
    return [v for _s, v in scored[:k]]


@app.route("/search", methods=["POST"]) 
def search():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    k = int(data.get("k", 5))
    results = search_verses(query, k)
    return jsonify({"query": query, "results": results})


@app.route("/chat", methods=["POST"]) 
def chat():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    k = int(data.get("k", 5))
    citations = search_verses(query, k)

    # Build a prompt using the top citations
    prompt_lines = [f"User: {query}", "", "Citations:"]
    for c in citations:
        # citations may be dicts from chroma_client.query
        cid = c.get("id") if isinstance(c, dict) else c.get("id")
        text = c.get("text") if isinstance(c, dict) else c.get("text")
        prompt_lines.append(f"- {cid}: {text}")
    prompt_lines.append("")
    prompt_lines.append("Answer:")
    prompt = "\n".join(prompt_lines)

    # If GROQ_API_KEY is provided, attempt to call Groq API with retries/backoff
    if GROQ_API_KEY:
        try:
            answer = _call_groq(prompt)
            return jsonify({"query": query, "answer": answer, "citations": citations})
        except Exception as e:
            print("Groq call failed:", e)

    # Fallback answer: simple merge of citations
    answer_text = "\n".join([c.get("text") for c in citations]) or "No answer available."
    return jsonify({"query": query, "answer": answer_text, "citations": citations})


@app.route("/health", methods=["GET"])  
def health():
    # Simple healthcheck: app up, optional Chroma presence
    ok = {"ok": True}
    try:
        if CHROMA_DB_PATH:
            import chromadb
            # attempt to connect
            client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            ok["chroma"] = "ok"
    except Exception:
        ok["chroma"] = "missing"
    return jsonify(ok)


@app.route("/daily", methods=["GET"]) 
def daily():
    v = random.choice(VERSES)
    return jsonify({"verse": v})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
