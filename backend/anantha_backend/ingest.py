"""Ingest script for Anantha Library.

- If BHAGAVADGITA_API_KEY is set in the environment, fetch verses from
  https://bhagavadgita.io API and write them to frontend/Anantha_Ui/src/data/verses.json.
- Otherwise, read existing verses.json and (placeholder) prepare for ChromaDB ingestion.

Usage:
  export BHAGAVADGITA_API_KEY=your_key
  python ingest.py --fetch

After fetching, run ingest.py --ingest to implement ChromaDB ingestion (placeholder).
"""
from pathlib import Path
import json
import os
import requests
import time
import argparse

FRONTEND_VERSES = Path(__file__).resolve().parents[1] / "frontend" / "Anantha_Ui" / "src" / "data" / "verses.json"
LOCAL_VERSES = Path(__file__).resolve().parent / "verses.json"
API_BASE = "https://bhagavadgita.io/api/v1"
API_KEY = os.getenv("BHAGAVADGITA_API_KEY")


def fetch_chapters():
    url = f"{API_BASE}/chapters"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_verses_for_chapter(chapter_id):
    # Try a couple of plausible endpoints
    headers = {"Authorization": f"Bearer {API_KEY}"}
    candidates = [
        f"{API_BASE}/chapters/{chapter_id}/verses",
        f"{API_BASE}/chapters/{chapter_id}/verses?translation=english",
    ]
    for url in candidates:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            continue
    # If none worked, return empty
    return []


def fetch_all_verses(save_path: Path = FRONTEND_VERSES):
    if not API_KEY:
        raise RuntimeError("BHAGAVADGITA_API_KEY not set in environment")
    chapters = fetch_chapters()
    all_verses = []
    print(f"Found {len(chapters)} chapters; fetching verses (may take a while)...")
    for ch in chapters:
        # try to extract id or number
        chapter_id = ch.get("id") or ch.get("chapter_number") or ch.get("chapter")
        if chapter_id is None:
            continue
        verses = fetch_verses_for_chapter(chapter_id)
        # Expect verses as a list of objects — normalize
        for v in verses:
            # Minimal normalization: ensure id and text
            vid = v.get("id") or f"chapter-{chapter_id}-{v.get('verse_number', '?')}"
            text = v.get("text") or v.get("translation") or v.get("verse") or json.dumps(v)
            all_verses.append({"id": str(vid), "text": text, **{k: v.get(k) for k in v if k not in ("id","text")}})
        time.sleep(0.05)  # polite pacing
    # Ensure directory exists
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_verses)} verses to {save_path}")
    return all_verses


def load_local_verses(path: Path = FRONTEND_VERSES):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    if LOCAL_VERSES.exists():
        return json.loads(LOCAL_VERSES.read_text(encoding='utf-8'))
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Fetch verses from bhagavadgita.io and save to frontend data path")
    parser.add_argument("--ingest", action="store_true", help="(Placeholder) Ingest into ChromaDB")
    args = parser.parse_args()

    if args.fetch:
        verses = fetch_all_verses()
        print("Fetch complete.")
        return

    verses = load_local_verses()
    print(f"Loaded {len(verses)} local verses")
    if args.ingest:
        try:
            from . import chroma_client
            db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            count = chroma_client.ingest_verses(verses, db_path=db_path)
            print(f"Ingested {count} verses into ChromaDB at {db_path}")
        except Exception as e:
            print("ChromaDB ingestion failed:", e)
            print("Ensure chromadb and sentence-transformers are installed and CHROMA_DB_PATH is writable.")


if __name__ == "__main__":
    main()
