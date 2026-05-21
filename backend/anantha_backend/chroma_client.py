"""ChromaDB client helper (placeholder).
Install chromadb and provide an embeddings function before using.
"""

from typing import Any


def get_chroma_client(db_path: str = "./chroma_db") -> Any:
    try:
        import chromadb
        client = chromadb.PersistentClient(path=db_path)
        return client
    except Exception:
        raise RuntimeError("ChromaDB client unavailable or not configured. Install chromadb and set CHROMA_DB_PATH.")
