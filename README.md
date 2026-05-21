# AnanthaLibrary (Monorepo)

This repository contains both frontend and backend for Anantha Library.

Layout:
- frontend/Anantha_Ui — TanStack Start frontend (do not modify files inside this folder unless necessary)
- backend/anantha_backend — Flask backend service (search, chat, daily)

Quickstart

Frontend (local dev):

  cd frontend/Anantha_Ui
  npm install
  npm run dev

Backend (local dev):

  cd backend/anantha_backend
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env
  # set GROQ_API_KEY in .env if using Groq
  FLASK_APP=app.py flask run --host=0.0.0.0 --port=8000

Docker (backend):

  docker-compose up --build

Notes
- Frontend is deployed to Vercel in production; backend runs on a droplet and proxies to Groq API.
- See backend/anantha_backend/README.md for more backend details.
