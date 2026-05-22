"""
Anantha Library - Ingestion Pipeline

This script handles the acquisition and preparation of sacred text data.
It supports:
1. Fetching from bhagavadgita.io API (requires API key).
2. Fetching from HuggingFace Datasets (dynamic registry).
3. Local JSON loading and ingestion into ChromaDB.
"""
import json
from pathlib import Path
import os
import requests
import time
import argparse

# Path resolution for locating local data files
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
    Orchestrates the full API fetch process for Bhagavad Gita.
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
            text = v.get("text") or v.get("translation")
            if not text and "translations" in v and isinstance(v["translations"], list):
                eng = next((t for t in v["translations"] if t.get("language", "").lower() == "english"), None)
                if eng:
                    text = eng.get("description") or eng.get("translated")
                elif len(v["translations"]) > 0:
                    text = v["translations"][0].get("description") or v["translations"][0].get("translated")
            
            processed = {
                "id": f"gita-{vid}",
                "book_id": "gita",
                "book_title": "Bhagavad Gita",
                "text": text or json.dumps(v),
                "translation": text,
                **{k: v.get(k) for k in v if k not in ("id","text")}
            }
            all_verses.append(processed)
            
        time.sleep(0.5)
        
    return _merge_and_save(all_verses, save_path)


def load_local_verses(path: Path = FRONTEND_VERSES):
    """Loads verses from a local JSON file."""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _merge_and_save(new_verses: list, save_path: Path):
    """Merges new verses with existing local JSON to avoid overwriting other books."""
    existing = load_local_verses(save_path)
    verse_map = {v['id']: v for v in existing}
    for v in new_verses:
        verse_map[v['id']] = v
    
    final_list = list(verse_map.values())
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(final_list)} total entries to {save_path}")
    return final_list


# Registry of known datasets and their mapping configurations
DATASET_REGISTRY = {
    "gita": {
        "dataset_name": "JDhruv14/Bhagavad-Gita_Dataset",
        "book_id": "gita",
        "book_title": "Bhagavad Gita",
        "id_parts": ["chapter", "verse"],
        "mapping": {
            "chapter": "chapter",
            "verse": "verse",
            "sanskrit": "sanskrit",
            "english": "english",
            "hindi": "hindi",
            "transliteration": "transliteration"
        }
    },
    "ramayana": {
        "dataset_name": "JDhruv14/Ramayana",
        "book_id": "ramayana",
        "book_title": "Ramayana",
        "id_parts": ["kanda", "sarga", "shloka_no"],
        "mapping": {
            "chapter": "kanda",
            "section": "sarga",
            "verse": "shloka_no",
            "sanskrit": "shloka",
            "english": "translation",
            "transliteration": "transliteration"
        }
    },
    "mahabharata": {
        "dataset_name": "JDhruv14/Mahabharata",
        "book_id": "mahabharata",
        "book_title": "Mahabharata",
        "id_parts": ["book_name", "chapter_no", "verse_no"],
        "mapping": {
            "chapter": "book_name",
            "section": "chapter_no",
            "verse": "verse_no",
            "sanskrit": "sanskrit_text",
            "english": "translation",
            "transliteration": "transliteration"
        }
    },
    "manu_smriti": {
        "dataset_name": "JDhruv14/Manu_Smriti",
        "book_id": "manu_smriti",
        "book_title": "Manu Smriti",
        "id_parts": ["chapter_no", "verse_no"],
        "mapping": {
            "chapter": "chapter_no",
            "verse": "verse_no",
            "sanskrit": "sanskrit",
            "english": "translation",
            "transliteration": "transliteration"
        }
    },
    "markandeya_purana": {
        "dataset_name": "JDhruv14/Markandeya_Purana",
        "book_id": "markandeya_purana",
        "book_title": "Markandeya Purana",
        "id_parts": ["book_name", "chapter_no", "verse_no"],
        "mapping": {
            "chapter": "book_name",
            "section": "chapter_no",
            "verse": "verse_no",
            "sanskrit": "sanskrit",
            "english": "translation",
            "transliteration": "transliteration"
        }
    },
    "srimad_bhagavatam": {
        "dataset_name": "JDhruv14/Srimad_Bhagavatam",
        "book_id": "srimad_bhagavatam",
        "book_title": "Srimad Bhagavatam",
        "id_parts": ["book", "canto_no", "chapter_no", "verse_no"],
        "mapping": {
            "chapter": "chapter_no",
            "section": "canto_no",
            "verse": "verse_no",
            "book": "book",
            "sanskrit": "sanskrit",
            "english": "translation",
            "transliteration": "transliteration"
        }
    }
}


def fetch_huggingface_dataset(book_id: str, save_path: Path = FRONTEND_VERSES):
    """Downloads and standardizes a dataset from HuggingFace."""
    config = DATASET_REGISTRY.get(book_id)
    if not config:
        raise ValueError(f"Book ID '{book_id}' not found in registry.")

    try:
        from datasets import load_dataset
    except ImportError:
        raise RuntimeError("Please install the datasets library: pip install datasets")

    print(f"Downloading HuggingFace dataset '{config['dataset_name']}' for {config['book_title']}...")
    ds = load_dataset(config['dataset_name'])
    
    all_verses = []
    mapping = config['mapping']
    id_parts = config.get('id_parts', [])
    
    split = list(ds.keys())[0]
    print(f"Loaded {len(ds[split])} rows from dataset. Converting...")
    
    for i, row in enumerate(ds[split]):
        id_slug = "-".join([str(row.get(p, '0')) for p in id_parts])
        if not id_slug or "None" in id_slug:
            id_slug = str(i)
            
        processed = {
            "id": f"{book_id}-{id_slug}",
            "book_id": book_id,
            "book_title": config['book_title']
        }
        
        for internal_key, dataset_key in mapping.items():
            processed[internal_key] = row.get(dataset_key, '')
            
        text_parts = []
        if processed.get("sanskrit"): text_parts.append(f"Sanskrit: {processed['sanskrit']}")
        if processed.get("english"): text_parts.append(f"Translation: {processed['english']}")
        if processed.get("hindi"): text_parts.append(f"Hindi: {processed['hindi']}")
        
        processed["text"] = "\n\n".join(text_parts)
        processed["translation"] = processed.get("english")
        
        all_verses.append(processed)
        
    return _merge_and_save(all_verses, save_path)


def main():
    """CLI entry point with dynamic arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=str, default="gita", help="Book ID to fetch")
    parser.add_argument("--fetch", action="store_true", help="Fetch from HuggingFace dataset")
    parser.add_argument("--fetch-api", action="store_true", help="Fetch Gita from bhagavadgita.io")
    parser.add_argument("--ingest", action="store_true", help="Ingest local JSON into ChromaDB")
    parser.add_argument("--list", action="store_true", help="List supported books")
    args = parser.parse_args()

    if args.list:
        print("Supported Books:")
        for bid, cfg in DATASET_REGISTRY.items():
            print(f" - {bid}: {cfg['book_title']} ({cfg['dataset_name']})")
        return

    if args.fetch_api:
        verses = fetch_all_verses()
    elif args.fetch:
        verses = fetch_huggingface_dataset(args.book)
    else:
        verses = load_local_verses()
        print(f"Loaded {len(verses)} local verses")
    
    if args.ingest:
        try:
            import chroma_client
            db_path = os.getenv("CHROMA_DB_PATH", str(Path(__file__).resolve().parent / "chroma_db"))
            count = chroma_client.ingest_verses(verses, db_path=db_path)
            print(f"Ingested {count} verses into ChromaDB at {db_path}")
        except Exception as e:
            print("ChromaDB ingestion failed:", e)


if __name__ == "__main__":
    main()
