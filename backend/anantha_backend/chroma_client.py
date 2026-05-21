"""ChromaDB client and ingestion helpers.

Uses sentence-transformers for embeddings (all-MiniLM-L6-v2) and ChromaDB persistent client.
"""
from typing import Any, List, Dict
from pathlib import Path
import os


def _load_model():
    # Lazy import to avoid heavy dependency at module import time when not used
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError("sentence-transformers not installed. Please pip install -r requirements.txt") from e
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_chroma_client(db_path: str = "./chroma_db") -> Any:
    try:
        import chromadb
        client = chromadb.PersistentClient(path=db_path)
        return client
    except Exception as e:
        raise RuntimeError("ChromaDB client unavailable or not configured. Install chromadb and set CHROMA_DB_PATH.") from e


def ingest_verses(verses: List[Dict], collection_name: str = "gita_verses", db_path: str = "./chroma_db") -> int:
    """Ingest verses into ChromaDB. Returns number of ingested items."""
    if not verses:
        return 0
    client = get_chroma_client(db_path)
    collection = None
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        collection = client.create_collection(name=collection_name)

    texts = [v.get("text", "") for v in verses]
    ids = [str(v.get("id") or i) for i, v in enumerate(verses)]
    metadatas = [{k: v.get(k) for k in v if k != "text"} for v in verses]

    model = _load_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    # Add to collection (will error on duplicates depending on Chroma version)
    try:
        collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    except Exception:
        # Try upsert variant if supported
        try:
            collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        except Exception as e:
            raise

    # Persist if client supports it
    try:
        client.persist()
    except Exception:
        pass

    return len(ids)


def query(query_text: str, k: int = 5, collection_name: str = "gita_verses", db_path: str = "./chroma_db") -> List[Dict]:
    """Query ChromaDB using semantic embedding of query_text."""
    client = get_chroma_client(db_path)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        raise RuntimeError("ChromaDB collection not found. Run ingest_verses first.")

    model = _load_model()
    q_emb = model.encode([query_text], convert_to_numpy=True).tolist()[0]

    results = collection.query(query_embeddings=[q_emb], n_results=k, include=["metadatas", "documents", "ids"])  # type: ignore
    docs = []
    ids = results.get("ids", [[]])[0]
    docs_list = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    for i in range(len(ids)):
        docs.append({"id": ids[i], "text": docs_list[i], "metadata": metas[i] if i < len(metas) else {}})
    return docs
