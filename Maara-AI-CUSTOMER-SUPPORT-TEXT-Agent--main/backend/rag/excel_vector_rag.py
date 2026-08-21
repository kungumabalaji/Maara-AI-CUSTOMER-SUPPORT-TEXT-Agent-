import json

import faiss
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CSV_FILE_PATH = "etech_chatbot_dataset.csv"

FAISS_INDEX_PATH = "etech_faiss.index"

METADATA_PATH = "etech_metadata.json"

CHUNK_SIZE = 800

CHUNK_OVERLAP = 100


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

print("Embedding model loaded.")


# ============================================================
# 1. LOAD CSV
# ============================================================

def load_csv(file_path: str) -> pd.DataFrame:

    print(f"[1/5] Reading CSV file: {file_path}")
    df = pd.read_csv(file_path)

    # Replace missing values with empty strings
    df = df.fillna("")

    print(f"[1/5] Loaded {len(df)} rows from {file_path}")

    print("CSV columns:")
    print(df.columns.tolist())

    return df


# ============================================================
# 2. CONVERT CSV ROWS INTO CHUNKS
# ============================================================

def dataframe_to_documents(df: pd.DataFrame):

    print(
        f"[2/5] Converting CSV rows into {CHUNK_SIZE}-character chunks "
        f"with {CHUNK_OVERLAP}-character overlap..."
    )
    documents = []
    metadata = []

    for row_index, row in df.iterrows():

        text_parts = []

        for column in df.columns:

            value = str(row[column]).strip()

            if value:

                text_parts.append(
                    f"{column}: {value}"
                )

        document_text = "\n".join(text_parts)

        if not document_text:
            continue

        step = CHUNK_SIZE - CHUNK_OVERLAP

        for chunk_number, start_index in enumerate(
            range(0, len(document_text), step),
            start=1
        ):
            chunk_text = document_text[
                start_index:start_index + CHUNK_SIZE
            ]

            if not chunk_text.strip():
                continue

            documents.append(chunk_text)

            metadata.append({
                "row_id": int(row_index),
                "chunk_id": chunk_number,
                "start_index": start_index,
                "content": chunk_text
            })

    print(f"[2/5] Created {len(documents)} chunks from CSV.")

    return documents, metadata


# ============================================================
# 3. CREATE EMBEDDINGS
# ============================================================

def create_embeddings(documents):

    print(f"[3/5] Generating embeddings for {len(documents)} documents...")

    embeddings = embedding_model.encode(
        documents,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(f"[3/5] Embedding shape: {embeddings.shape}")
    print(f"[3/5] Embedding dimension: {embeddings.shape[1]}")

    return embeddings


# ============================================================
# 4. CREATE FAISS VECTOR INDEX
# ============================================================

def create_faiss_index(embeddings):

    print("[4/5] Creating FAISS vector index...")
    dimension = embeddings.shape[1]

    print(f"[4/5] Using embedding dimension: {dimension}")

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    print(f"[4/5] Vectors stored in FAISS: {index.ntotal}")

    return index


# ============================================================
# 5. SAVE FAISS + METADATA
# ============================================================

def save_vector_database(
    index,
    metadata
):

    print("[5/5] Saving FAISS index and metadata...")
    # Save FAISS index
    faiss.write_index(
        index,
        FAISS_INDEX_PATH
    )

    # Save actual CSV text
    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"[5/5] Saved FAISS index: {FAISS_INDEX_PATH}")
    print(f"[5/5] Saved metadata: {METADATA_PATH}")


def csv_to_vector_rag(file_path: str):
    print("Starting CSV-to-vector ingestion...")

    df = load_csv(file_path)
    documents, metadata = dataframe_to_documents(df)

    if not documents:
        raise ValueError("CSV contains no usable data.")

    embeddings = create_embeddings(documents)
    index = create_faiss_index(embeddings)
    save_vector_database(index, metadata)

    print("RAG ingestion completed successfully.")
    return index, metadata


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("Starting vector database creation...")
    csv_to_vector_rag(
        CSV_FILE_PATH
    )
    print("Vector database creation finished.")
