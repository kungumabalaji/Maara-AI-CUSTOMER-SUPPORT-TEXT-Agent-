import json
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

RAG_DIR = Path(__file__).resolve().parent.parent / "rag"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = RAG_DIR / "etech_faiss.index"
METADATA_PATH = RAG_DIR / "etech_metadata.json"


@lru_cache(maxsize=1)
def _embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@lru_cache(maxsize=1)
def _vector_database():
    if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Vector index not found. Run backend/rag/rag.py first to build "
            f"{FAISS_INDEX_PATH.name} and {METADATA_PATH.name}."
        )
    index = faiss.read_index(str(FAISS_INDEX_PATH))
    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    return index, metadata


def search(query: str, top_k: int = 5) -> list[dict]:
    index, metadata = _vector_database()
    model = _embedding_model()

    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.asarray(query_embedding, dtype="float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, vector_id in zip(scores[0], indices[0]):
        if vector_id == -1:
            continue
        results.append(
            {
                "score": float(score),
                "row_id": metadata[vector_id]["row_id"],
                "content": metadata[vector_id]["content"],
            }
        )
    return results
