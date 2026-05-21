"""
Anantha Library - Ingestion Pipeline

This script handles the acquisition and preparation of Bhagavad Gita data.
It supports:
1. Fetching from bhagavadgita.io API (requires API key).
2. Fetching from HuggingFace Datasets (using JDhruv14/Bhagavad-Gita_Dataset).
3. Local ingestion of JSON data into ChromaDB.
"""
from pathlib import Path
import json
import os
import requests
import time
import argparse

# Paths for saving the processed verses
FRONTEND_VERSES = Path(__file__).resolve().parents[2] / "frontend" / "Anantha_Ui" / "src" / "data" / "verses.json"
LOCAL_VERSES = Path(__file__).resolve().parent / "verses.json"
API_BASE = "https://bhagavadgita.io/api/v1"
API_KEY = os.getenv("BHAGAVADGITA_API_KEY")


def fetch_chapters():
    """Fetches the list of chapters from the Bhagavad Gita API."""
    url = f"{API_BASE}/chapters"
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("chapters", data) if isinstance(data, dict) else data


def fetch_verses_for_chapter(chapter_id):
    """Fetches all verses for a specific chapter from the Bhagavad Gita API."""
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    candidates = [
        f"{API_BASE}/verses/{chapter_id}?language=english",
        f"{API_BASE}/verses/{chapter_id}",
        f"{API_BASE}/chapters/{chapter_id}/verses"
    ]
    for url in candidates:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("verses", data) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Warning: Failed fetching from {url} - {e}")
            continue
    print(f"Warning: Could not fetch verses for chapter {chapter_id}")
    return []


def fetch_all_verses(save_path: Path = FRONTEND_VERSES):
    """
    Orchestrates the full API fetch process.
    Iterates through all 18 chapters and saves the consolidated verses to a JSON file.
    """
    if not API_KEY:
        raise RuntimeError("BHAGAVADGITA_API_KEY not set in environment.")
    
    print("Fetching chapters...")
    chapters = fetch_chapters()
    if not chapters:
        chapters = [{"chapter_number": i} for i in range(1, 19)]
        
    all_verses = []
    print(f"Found {len(chapters)} chapters; fetching verses...")
    for ch in chapters:
        chapter_id = ch.get("id") or ch.get("chapter_number") or ch.get("chapter")
        if chapter_id is None:
            continue
            
        print(f"Fetching Chapter {chapter_id}...")
        verses = fetch_verses_for_chapter(chapter_id)
        
        for v in verses:
            vid = v.get("id") or f"chapter-{chapter_id}-{v.get('verse_number', '?')}"
            
            # Normalize the verse text/translation from various possible API response formats
            text = v.get("text") or v.get("translation")
            if not text and "translations" in v and isinstance(v["translations"], list):
                eng = next((t for t in v["translations"] if t.get("language", "").lower() == "english"), None)
                if eng:
                    text = eng.get("description") or eng.get("translated")
                elif len(v["translations"]) > 0:
                    text = v["translations"][0].get("description") or v["translations"][0].get("translated")
                    
            if not text:
                text = json.dumps(v)
                
            all_verses.append({
                "id": str(vid), 
                "text": text, 
                **{k: v.get(k) for k in v if k not in ("id","text")}
            })
            
        time.sleep(0.5)  # Pacing to respect API rate limits
        
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_verses)} verses to {save_path}")
    return all_verses


def load_local_verses(path: Path = FRONTEND_VERSES):
    """Loads verses from a local JSON file."""
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    if LOCAL_VERSES.exists():
        return json.loads(LOCAL_VERSES.read_text(encoding='utf-8'))
    return []


def fetch_huggingface_dataset(save_path: Path = FRONTEND_VERSES):
    """
    Alternative data source: HuggingFace.
    Useful for local development without an external API key.
    Processes the dataset into the internal project format.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise RuntimeError("Please install the datasets library: pip install datasets")

    print("Downloading HuggingFace dataset 'JDhruv14/Bhagavad-Gita_Dataset'...")
    ds = load_dataset('JDhruv14/Bhagavad-Gita_Dataset')
    
    all_verses = []
    print(f"Loaded {len(ds['train'])} rows from dataset. Converting...")
    
    for i, row in enumerate(ds['train']):
        chapter = row.get('chapter', 0)
        verse = row.get('verse', 0)
        sanskrit = row.get('sanskrit', '')
        english = row.get('english', '')
        hindi = row.get('hindi', '')
        translit = row.get('transliteration', '')
        
        # Combine different language versions into a single 'text' block for vector search context
        combined_text = f"Sanskrit: {sanskrit}\n\nTranslation: {english}\n\nHindi: {hindi}"
        
        all_verses.append({
            "id": f"gita-{chapter}-{verse}",
            "text": combined_text,
            "chapter": chapter,
            "verse": verse,
            "sanskrit": sanskrit,
            "translation": english,
            "hindi": hindi,
            "transliteration": translit
        })
        
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_verses)} verses to {save_path}")
    return all_verses


def main():
    """CLI entry point for managing data ingestion."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Fetch verses from bhagavadgita.io API")
    parser.add_argument("--fetch-hf", action="store_true", help="Fetch from HuggingFace dataset")
    parser.add_argument("--ingest", action="store_true", help="Ingest local JSON into ChromaDB")
    args = parser.parse_args()

    if args.fetch:
        verses = fetch_all_verses()
        return
        
    if args.fetch_hf:
        verses = fetch_huggingface_dataset()
        return

    verses = load_local_verses()
    print(f"Loaded {len(verses)} local verses")
    
    # Final step of ingestion: Vectorizing and storing in ChromaDB
    if args.ingest:
        try:
            import chroma_client
            db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            count = chroma_client.ingest_verses(verses, db_path=db_path)
            print(f"Ingested {count} verses into ChromaDB at {db_path}")
        except Exception as e:
            print("ChromaDB ingestion failed:", e)


if __name__ == "__main__":
    main()
