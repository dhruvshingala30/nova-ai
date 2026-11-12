"""
app/tools/knowledge_base_search.py - Hybrid Retrieval Engine (Dense + BM25 + RRF + Reranker).
Combines ChromaDB vector similarity with BM25 keyword matching for optimal recall,
then applies a Cross-Encoder reranker for precision.
"""

import os
import re
import sys
from collections import (
    defaultdict,  # Automatically initializes missing keys with default values
)
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import (
    BM25Okapi,  # Gold Standard algorithm used by modern search engines for keywords matching(sparse retrival)
)
from sentence_transformers import (
    CrossEncoder,  # Cross-Encoder reranker for precise query-document relevance scoring
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.hyde import hyde_generator

VECTOR_DB_DIR = str((PROJECT_ROOT / "data" / "vector_db").resolve())
COLLECTION_NAME = "nova_workspace_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# -------------------------------------------------------------
# Module-level Singleton Cache to avoid re-instantiation overhead
# -------------------------------------------------------------
_CHROMA_CLIENT = None
_EMBEDDING_FN = None
_COLLECTION = None
_RERANKER = None


def _get_collection():
    """
    Initializes and caches the persistent ChromaDB client, SentenceTransformer
    embedding function, and collection once in memory.
    """
    global _CHROMA_CLIENT, _EMBEDDING_FN, _COLLECTION
    if _COLLECTION is None:
        if not os.path.exists(VECTOR_DB_DIR):
            return None
        _CHROMA_CLIENT = chromadb.PersistentClient(VECTOR_DB_DIR)
        _EMBEDDING_FN = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        _COLLECTION = _CHROMA_CLIENT.get_collection(
            name=COLLECTION_NAME,
            embedding_function=_EMBEDDING_FN,  # type: ignore
        )
    return _COLLECTION


def tokenize(text: str) -> list[str]:
    """
    Simple lowercase regex word tokenizer for BM25.
    """
    # To match all alphanumeric words, automatically stripping out punctuations, commas, brackets and extra spaces
    return re.findall(r"\w+", text.lower()) # Because BM25 requires list of tokens as input(e.g., 'Risk in Trading!' -> ['risk', 'in', 'trading'])


def rrf_score(
    dense_ranks: list[dict], bm25_ranks: list[dict], k: int = 60
) -> list[dict]:    # k is a smoothing constant. Standardized in information retrival research as k = 60
    """
    Fuses dense and sparse rankings using Reciprocal Rank Fusion (RRF).
    Formula: RRF(d) = sum(1 / (k + rank))
    """
    scores = defaultdict(float)
    doc_map = {}

    # 1. Score Dense Results
    for rank, item in enumerate(dense_ranks, start=1):
        doc_id = item["id"]
        scores[doc_id] += 1.0 / (k + rank)
        doc_map[doc_id] = item

    # 2. Score BM25 Results
    for rank, item in enumerate(bm25_ranks, start=1):
        doc_id = item["id"]
        scores[doc_id] += 1.0 / (k + rank)
        # if BM25 found a document which vector search missed completely
        if doc_id not in doc_map:
            doc_map[doc_id] = item

    # 3. Sort by combined RRF score descending
    fused_results = []
    for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        entry = dict(doc_map[doc_id])
        entry["rrf_score"] = round(score, 5)
        fused_results.append(entry)

    return fused_results


def _get_reranker() -> CrossEncoder:
    """
    Initializes and caches the Cross-Encoder reranker model once in memory.
    Uses ms-marco-MiniLM-L-6-v2 (22M params) — optimized for passage relevance scoring.
    """
    global _RERANKER
    if _RERANKER is None:
        _RERANKER = CrossEncoder(RERANKER_MODEL)
    return _RERANKER


def rerank(query: str, candidates: list[dict], top_n: int) -> list[dict]:
    """
    Reranks RRF-fused candidates using a Cross-Encoder for precise semantic relevance.
    Scores each (query, document_text) pair independently and sorts by relevance.

    Args:
        query: The original user query (NOT the HyDE passage).
        candidates: RRF-fused result dicts, each containing a 'text' field.
        top_n: Number of top results to return after reranking.

    Returns:
        Top-n candidates sorted by cross-encoder relevance score (descending).
    """
    if not candidates:
        return candidates

    cross_encoder = _get_reranker()

    # Build (query, document) pairs for cross-encoder scoring
    pairs = [(query, item["text"]) for item in candidates]
    ce_scores = cross_encoder.predict(pairs)

    # Attach cross-encoder scores and sort descending
    for item, score in zip(candidates, ce_scores):
        item["rerank_score"] = round(float(score), 4)

    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_n]


def get_indexed_documents() -> list[str]:
    """
    Dynamically fetches all unique document sources currently indexed in ChromaDB.
    Runs in zero-shot fashion without hardcoding.
    """
    if not os.path.exists(VECTOR_DB_DIR):
        return []

    try:
        collection = _get_collection()
        if collection is None:
            return []
        
        data = collection.get(include=["metadatas"])
        if not data or not data.get("metadatas"):
            return []

        # Extracting unique source names by set comprehension
        sources = {
            m.get("source") 
            for m in data["metadatas"] if m and "source" in m # type: ignore
        }
        return sorted(list(sources)) # type: ignore  # noqa: C414

    except Exception:  # noqa: BLE001
        return []
    

def search_knowledge_base(query: str, n_results: int = 10) -> dict:
    """
    Hybrid semantic search combining Dense Embeddings (ChromaDB) and Sparse Keywords (BM25).
    """
    if not os.path.exists(VECTOR_DB_DIR):
        return {
            "success": False,
            "message": f"Vector database directory not found at '{VECTOR_DB_DIR}'. Please ensure documents are indexed.",
        }

    try:
        collection = _get_collection()
        if collection is None:
            return {
                "success": False,
                "message": f"Collection '{COLLECTION_NAME}' could not be loaded from '{VECTOR_DB_DIR}'.",
            }

        # Generate hypothetical passage for dense ChromaDB matching
        dense_search_text = hyde_generator.generate(query=query)

        # ---------------------------------------------------------
        # 1. DENSE RETRIEVAL (ChromaDB Vector Search with HyDE document)
        # ---------------------------------------------------------
        dense_response = collection.query(
            query_texts=[dense_search_text],
            n_results=n_results * 2,  # Fetch top 2x candidates for rank fusion
            include=["documents", "metadatas", "distances"],
        )

        dense_candidates = []
        if dense_response.get("documents") and dense_response["documents"][0]: # type: ignore
            docs = dense_response["documents"][0] # type: ignore
            metas = dense_response["metadatas"][0] # type: ignore
            ids = dense_response["ids"][0]
            dists = dense_response["distances"][0] # type: ignore

            for doc_id, doc, meta, dist in zip(ids, docs, metas, dists):
                dense_candidates.append(
                    {
                        "id": doc_id,
                        "source": meta.get("source", "Unknown"),
                        "page": meta.get("page", "N/A"),
                        "text": doc,
                        "dense_distance": round(dist, 4) if dist is not None else None,
                    }
                )

        # ---------------------------------------------------------
        # 2. SPARSE RETRIEVAL (BM25 over indexed corpus)
        # ---------------------------------------------------------
        all_docs_data = collection.get(include=["documents", "metadatas"])
        bm25_candidates = []

        if all_docs_data.get("documents"):
            corpus_texts = all_docs_data["documents"]
            corpus_metas = all_docs_data["metadatas"]
            corpus_ids = all_docs_data["ids"]

            tokenized_corpus = [tokenize(doc) for doc in corpus_texts] # type: ignore
            bm25 = BM25Okapi(tokenized_corpus)

            tokenized_query = tokenize(query)
            bm25_scores = bm25.get_scores(tokenized_query)

            # Get top BM25 results
            top_bm25_indices = sorted(
                range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
            )[: n_results * 2]

            for idx in top_bm25_indices:
                if bm25_scores[idx] > 0:  # Only include keyword matches
                    bm25_candidates.append(
                        {
                            "id": corpus_ids[idx],
                            "source": corpus_metas[idx].get("source", "Unknown"), # type: ignore
                            "page": corpus_metas[idx].get("page", "N/A"), # type: ignore
                            "text": corpus_texts[idx], # type: ignore
                            "bm25_score": round(float(bm25_scores[idx]), 4),
                        }
                    )

        # ---------------------------------------------------------
        # 3. RECIPROCAL RANK FUSION (RRF)
        # ---------------------------------------------------------
        fused = rrf_score(dense_candidates, bm25_candidates, k=60)

        # ---------------------------------------------------------
        # 4. CROSS-ENCODER RERANKING (Precision pass)
        # ---------------------------------------------------------
        # Rerank the full fused candidate pool using the original query
        # (not the HyDE passage) for true semantic relevance scoring
        final_results = rerank(query, fused, top_n=n_results)

        if not final_results:
            return {
                "success": True,
                "query": query,
                "message": "No relevant documents found in knowledge base.",
                "results": [],
            }

        return {
            "success": True,
            "query": query,
            "results_count": len(final_results),
            "results": final_results,
        }

    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "message": f"Failed to query knowledge base: {str(e)}",  # noqa: RUF010
        }
