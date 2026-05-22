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


def ingest_verses(verses: List[Dict], collection_name: str = "anantha_collection", db_path: str = "./chroma_db") -> int:
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
    # Store all other fields as metadata for retrieval and filtering
    metadatas = [{k: v.get(k) for k in v if k != "text"} for v in verses]

    model = _load_model()
    # model.encode converts the text into a list of floats (the vector)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    # Add data to the collection in batches to avoid max batch size errors
    batch_size = 5000
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_texts = texts[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        batch_embs = embeddings[i:i + batch_size]
        
        try:
            collection.add(ids=batch_ids, documents=batch_texts, metadatas=batch_metas, embeddings=batch_embs)
        except Exception:
            # Fallback to upsert (update if exists, else insert) to prevent duplicate errors
            try:
                collection.upsert(ids=batch_ids, documents=batch_texts, metadatas=batch_metas, embeddings=batch_embs)
            except Exception:
                raise

    return len(ids)


def query(query_text: str, k: int = 5, book_id: str = None, collection_name: str = "anantha_collection", db_path: str = "./chroma_db") -> List[Dict]:
    """
    Performs a semantic search for a user's query, optionally filtered by book_id.
    
    Process:
    1. Convert the user's search string into a vector.
    2. Use ChromaDB to find the top K vectors, optionally filtered by metadata.
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

    # Build filter if book_id is provided
    where_filter = {"book_id": book_id} if book_id else None

    # Query the collection for the K nearest neighbors
    results = collection.query(
        query_embeddings=[q_emb], 
        n_results=k, 
        where=where_filter,
        include=["metadatas", "documents"]
    )  # type: ignore
    
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


def get_available_books(collection_name: str = "anantha_collection", db_path: str = "./chroma_db") -> List[Dict[str, str]]:
    """
    Returns a unique list of books (book_id and book_title) currently in the database.
    Optimized to handle larger collections.
    """
    client = get_chroma_client(db_path)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        return []

    # In a real-world scenario with millions of rows, we'd use a separate lookup table.
    # For Anantha Library's scale, we fetch a large sample to identify unique books.
    # Since books are added in blocks, unique ones appear across the range.
    unique_books = {}
    
    # We peek at the collection in chunks to find unique book IDs
    total_count = collection.count()
    limit = min(total_count, 100000) # Fetch up to 100k metadata rows
    
    # Note: Fetching only metadatas is relatively cheap in Chroma
    results = collection.get(limit=limit, include=["metadatas"])
    metas = results.get("metadatas", [])
    
    for m in metas:
        bid = m.get("book_id")
        btitle = m.get("book_title")
        if bid and bid not in unique_books:
            unique_books[bid] = btitle or bid
            
    return [{"id": bid, "title": btitle} for bid, btitle in unique_books.items()]
