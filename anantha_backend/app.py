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

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = os.getenv("GROQ_API_URL", f"https://api.groq.ai/v1/models/{GROQ_MODEL}/outputs")
VERSES_PATH = os.getenv("VERSES_PATH")  # optional override

app = Flask(__name__)
CORS(app)

# Try to locate verses JSON from frontend if available
def load_verses():
    # Typical path: repo_root/Anantha_Ui/src/data/verses.json
    candidates = []
    if VERSES_PATH:
        candidates.append(Path(VERSES_PATH))
    repo_root = Path(__file__).resolve().parents[1]
    candidates.append(repo_root / "Anantha_Ui" / "src" / "data" / "verses.json")
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


def search_verses(query: str, k: int = 5):
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

    # Build a simple prompt using the top citations
    prompt = f"User: {query}\n\nCitations:\n"
    for c in citations:
        prompt += f"- {c.get('id')}: {c.get('text')}\n"
    prompt += "\nAnswer:" 

    # If GROQ_API_KEY is provided, attempt to call Groq API
    if GROQ_API_KEY:
        try:
            payload = {
                "input": prompt,
            }
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            # NOTE: response schema may differ — adapt parsing as needed
            answer = body.get("output", body)
            return jsonify({"query": query, "answer": answer, "citations": citations})
        except Exception as e:
            # fallback to mock answer
            print("Groq call failed:", e)

    # Fallback answer: simple merge of citations
    answer_text = "\n".join([c.get("text") for c in citations]) or "No answer available."
    return jsonify({"query": query, "answer": answer_text, "citations": citations})


@app.route("/daily", methods=["GET"]) 
def daily():
    v = random.choice(VERSES)
    return jsonify({"verse": v})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
