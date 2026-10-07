"""rag/ingest_pdf.py - Resilient In-Memory PDF Ingestion and Vector Embedding Pipeline."""

import io
from pathlib import Path
from typing import Any

import chromadb
import pdfplumber
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

path = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = str(path / "data/vector_db")

COLLECTION_NAME = "nova_workspace_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def extract_pdf_pages_from_bytes(
    file_bytes: bytes, filename: str
) -> list[dict[str, Any]]:
    """
    Extracts text page-by-page from an in-memory PDF stream.
    Uses pdfplumber first; falls back to pypdf if pdfplumber encounters a 'No /Root object' syntax error.
    """
    pages_data: list[dict[str, Any]] = []

    # 1. Primary Attempt: pdfplumber
    try:
        stream = io.BytesIO(file_bytes)
        with pdfplumber.open(stream) as pdf:
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages_data.append(
                        {
                            "text": text.strip(),
                            "page_number": idx + 1,
                            "source": filename,
                        }
                    )
    except Exception as plumber_err:  # noqa: BLE001
        print(
            f"⚠️ [RAG] pdfplumber parser warning on '{filename}': {plumber_err}. Retrying with pypdf..."
        )

    # 2. Resilient Fallback: pypdf (handles missing /Root objects and lenient trailers)
    if not pages_data:
        try:
            reader = PdfReader(io.BytesIO(file_bytes), strict=False)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages_data.append(
                        {
                            "text": text.strip(),
                            "page_number": idx + 1,
                            "source": filename,
                        }
                    )
        except Exception as pypdf_err:  # noqa: BLE001
            print(f"❌ [RAG] pypdf parser also failed on '{filename}': {pypdf_err}")

    if not pages_data:
        print(
            f"⚠️ [RAG] No readable text found in '{filename}' (it may be a scanned or image-only PDF)."
        )
        return []

    print(f"✅ Extracted {len(pages_data)} pages from '{filename}'.")
    return pages_data


def chunk_documents(
    pages_data: list[dict[str, Any]], chunk_size: int = 800, chunk_overlap: int = 150
):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    all_chunks = []
    for item in pages_data:
        chunks = text_splitter.split_text(item["text"])
        for chunk_idx, chunk_text in enumerate(chunks):
            all_chunks.append(
                {
                    "id": f"{item['source']}_p{item['page_number']}_c{chunk_idx}",
                    "text": chunk_text,
                    "metadata": {
                        "source": item["source"],
                        "page": item["page_number"],
                        "chunk": chunk_idx,
                    },
                }
            )
    return all_chunks


def ingest_to_chromadb(
    chunks: list[dict[str, Any]], db_path: str = VECTOR_DB_DIR
) -> int:
    if not chunks:
        return 0

    chroma_client = chromadb.PersistentClient(db_path)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,  # type: ignore
    )

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    total_count = collection.count()
    print(f"🎉 Ingestion Complete! Collection now contains {total_count} chunks.")
    return total_count
