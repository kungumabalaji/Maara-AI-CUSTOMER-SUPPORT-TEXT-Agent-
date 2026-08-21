import json

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "etech_faiss.index"
METADATA_PATH = "etech_metadata.json"


print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Embedding model loaded.")


def load_vector_database():
    print("Loading FAISS index and metadata...")
    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    print(f"Loaded {index.ntotal} vectors and {len(metadata)} metadata records.")
    return index, metadata


def search_rag(query: str, top_k: int = 5):
    print(f"[1/3] Customer question: {query}")
    index, metadata = load_vector_database()

    print("[2/3] Creating embedding for the customer question...")
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )
    query_embedding = np.asarray(query_embedding, dtype="float32")
    print(f"[2/3] Question embedding shape: {query_embedding.shape}")

    print(f"[3/3] Searching FAISS for the top {top_k} results...")
    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, vector_id in zip(scores[0], indices[0]):
        if vector_id == -1:
            continue

        results.append({
            "score": float(score),
            "vector_id": int(vector_id),
            "row_id": metadata[vector_id]["row_id"],
            "content": metadata[vector_id]["content"]
        })

    print(f"[3/3] Retrieved {len(results)} matching results.")
    return results


if __name__ == "__main__":
    query = input("Type your customer question: ").strip()

    if not query:
        raise ValueError("Please type a customer question.")

    results = search_rag(query, top_k=3)

    print("\nCustomer question:")
    print(query)
    print("\nRetrieved results:")

    for number, result in enumerate(results, start=1):
        print("\n-----------------------")
        print(f"Result {number}")
        print("Similarity score:", result["score"])
        print(result["content"])
