"""
ChromaDB Client & Semantic Search Engine

This module handles the 'Vector DB' part of the RAG pipeline.
It uses 'sentence-transformers' to convert text into numerical vectors (embeddings)
and ChromaDB to store and perform similarity searches on these vectors.
"""
from typing import Any, List, Dict
from pathlib import Path
import os


def _load_model():
    """
    Loads the SentenceTransformer model.
    'all-MiniLM-L6-v2' is a lightweight, efficient model that converts
    sentences into 384-dimensional vectors while preserving semantic meaning.
    """
    # Lazy import to avoid heavy dependency at module import time when not used
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError("sentence-transformers not installed. Please pip install -r requirements.txt") from e
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_chroma_client(db_path: str = "./chroma_db") -> Any:
    """
    Initializes a persistent ChromaDB client.
    Data is stored on disk at the specified db_path.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=db_path)
        return client
    except Exception as e:
        raise RuntimeError("ChromaDB client unavailable or not configured. Install chromadb and set CHROMA_DB_PATH.") from e


def ingest_verses(verses: List[Dict], collection_name: str = "gita_verses", db_path: str = "./chroma_db") -> int:
    """
    Converts verses into embeddings and stores them in ChromaDB.
    
    Process:
    1. Extract text and metadata from the verse list.
    2. Use the transformer model to generate numerical vectors (embeddings) for each verse.
    3. Add or update these vectors and metadata in the ChromaDB collection.
    """
    if not verses:
        return 0
    client = get_chroma_client(db_path)
    collection = None
    try:
        # Try to get existing collection or create a new one
        collection = client.get_collection(name=collection_name)
    except Exception:
        collection = client.create_collection(name=collection_name)

    texts = [v.get("text", "") for v in verses]
    ids = [str(v.get("id") or i) for i, v in enumerate(verses)]
    # Store other verse fields (chapter, verse number, etc.) as metadata for retrieval
    metadatas = [{k: v.get(k) for k in v if k != "text"} for v in verses]

    model = _load_model()
    # model.encode converts the text into a list of floats (the vector)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    # Add data to the collection. Chroma uses HNSW (Hierarchical Navigable Small World) 
    # indexing internally for fast nearest-neighbor search.
    try:
        collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    except Exception:
        # Fallback to upsert (update if exists, else insert) to prevent duplicate errors
        try:
            collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        except Exception as e:
            raise

    # Persist the changes to the disk
    try:
        client.persist()
    except Exception:
        pass

    return len(ids)


def query(query_text: str, k: int = 5, collection_name: str = "gita_verses", db_path: str = "./chroma_db") -> List[Dict]:
    """
    Performs a semantic search for a user's query.
    
    Process:
    1. Convert the user's search string into a vector using the same model.
    2. Use ChromaDB to find the top K vectors in the database that are 'closest' 
       to the query vector (typically using cosine similarity).
    3. Return the original text and metadata for the closest matches.
    """
    client = get_chroma_client(db_path)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        raise RuntimeError("ChromaDB collection not found. Run ingest_verses first.")

    model = _load_model()
    # Encode the user query into the vector space
    q_emb = model.encode([query_text], convert_to_numpy=True).tolist()[0]

    # Query the collection for the K nearest neighbors
    results = collection.query(query_embeddings=[q_emb], n_results=k, include=["metadatas", "documents", "ids"])  # type: ignore
    
    # Format the results into a developer-friendly list of dictionaries
    docs = []
    ids = results.get("ids", [[]])[0]
    docs_list = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    for i in range(len(ids)):
        docs.append({
            "id": ids[i], 
            "text": docs_list[i], 
            "metadata": metas[i] if i < len(metas) else {}
        })
    return docs
