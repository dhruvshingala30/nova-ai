import os
from pathlib import Path
from typing import Any

import chromadb
import pdfplumber
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

path = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = str(path / "data/vector_db")

COLLECTION_NAME = "nova_workspace_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def extract_pdf_pages(file_path: str):
    """
    Extracts text page-by-page from a PDF file using pdfplumber.
    Returns a list of dicts containing text, page number, and source filename.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: '{file_path}'.")
    
    filename = os.path.basename(file_path)
    pages_data = []

    with pdfplumber.open(file_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text and text.strip():
                pages_data.append(
                    {
                        "text": text.strip(),
                        "page_number": idx + 1,
                        "source": filename
                    }
                )
    print(f"✅ Extracted {len(pages_data)} pages from {filename}.")
    return pages_data


def chunk_documents(pages_data: list[dict[str, Any]], chunk_size: int = 800, chunk_overlap: int = 150):
    """
    Splits extracted page texts into smaller overlapping chunks while retaining page metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    chunk_counter = 0

    for item in pages_data:
        chunks = text_splitter.split_text(item["text"])

        for chunk_idx, chunk_text in enumerate(chunks):
            chunk_counter += 1
            all_chunks.append(
                {
                    "id": f"{item['source']}_p{item['page_number']}_c{chunk_idx}",
                    "text": chunk_text,
                    "metadata": {
                        "source": item["source"],
                        "page": item["page_number"],
                        "chunk": chunk_idx
                    }
                }
            )

    print(f"✂️ Created {len(all_chunks)} total chunks from {len(pages_data)} pages.")
    return all_chunks


def ingest_to_chromadb(chunks: list[dict[str, Any]], db_path: str = VECTOR_DB_DIR):
    """
    Embeds chunks using sentence-transformers and persists them to ChromaDB at ./data/vector_db.
    """
    print(f"💾 Connecting to ChromaDB at '{db_path}'...")
    chroma_client = chromadb.PersistentClient(db_path)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn # type: ignore
    )

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadata = [c["metadata"] for c in chunks]

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadata[i:i + batch_size]
        )

    total_count = collection.count()
    print(
        f"🎉 Ingestion Complete! Collection '{COLLECTION_NAME}' now contains {total_count} embedded chunks."
    )
    return total_count


if __name__ == "__main__":
    # Test Ingestion Path (e.g., ./nova_workspace/Trading_in_the_Zone.pdf)
    path = Path(__file__).resolve().parent.parent
    target_pdf = str(path / "nova_workspace/Trading in the zone by Mark Douglas.pdf")

    if os.path.exists(target_pdf):
        pages = extract_pdf_pages(target_pdf)
        chunks = chunk_documents(pages) # type: ignore
        ingest_to_chromadb(chunks)
    else:
        print(
            f"⚠️ Test file '{target_pdf}' not found. Place a PDF in ./nova_workspace to run ingestion."
        )