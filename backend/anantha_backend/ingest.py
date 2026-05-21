"""Placeholder ingest script to create a ChromaDB collection from verses JSON.
Replace vectorizer/embedder with your chosen embeddings (sentence-transformers or remote API).
"""
from pathlib import Path
import json

VERSES_FILE = Path(__file__).resolve().parents[1] / "frontend" / "Anantha_Ui" / "src" / "data" / "verses.json"


def load_verses(path: Path = VERSES_FILE):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    raise FileNotFoundError(f"Verses file not found: {path}")


if __name__ == "__main__":
    verses = load_verses()
    print(f"Loaded {len(verses)} verses (preview):")
    for v in verses[:3]:
        print(v)
    print("Implement ChromaDB ingestion here.")
