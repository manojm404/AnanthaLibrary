# Anantha Backend (anantha_backend)

Minimal Flask backend for Anantha Library. Provides three HTTP endpoints used by the frontend:

- POST /search  — returns top-k verses for a query
- POST /chat    — returns an answer + citations (calls Groq API when GROQ_API_KEY present)
- GET  /daily   — returns a random verse

Quickstart (local):

1. python3 -m venv .venv
2. . .venv/bin/activate
3. pip install -r requirements.txt
4. copy `.env.example` to `.env` and set GROQ_API_KEY (optional)
5. FLASK_APP=app.py flask run --host=0.0.0.0 --port=8000

Notes:
- ChromaDB integration and ingest scripts are placeholders; implement ingestion when ready.
- This service expects the frontend to set `AI_SERVICE_URL` to this droplet's address.
