import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VECTOR_DB_DIR = str(PROJECT_ROOT / "data/vector_db")
COLLECTION_NAME = "nova_workspace_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def search_knowledge_base(query: str, n_results: int = 3):
    """
    Semantically searches NovaAI's vector knowledge base (ChromaDB) for relevant document chunks.

    Args:
        query (str): The natural language search query.
        n_results (int): Number of relevant document chunks to retrieve (default: 3).

    Returns:
        dict: A dictionary containing query status, retrieved chunks with text, page numbers, and sources.
    """
    # 1. Defensive Check: Ensure Vector DB exists on disk
    if not os.path.exists(VECTOR_DB_DIR):
        return {
            "status": "error",
            "message": f"vector database directory not found at '{VECTOR_DB_DIR}'. Please run ingest_pdf.py first."
        }

    try:
        # 2. Connect to local ChromaDB instance
        client = chromadb.PersistentClient(VECTOR_DB_DIR)

        # 3. Instantiate the SentenceTransformer embedding model
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        # 4. Access the existing collection
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn # type: ignore
        )

        # 5. Perform similarity query
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        # 6. Extract raw nested lists from query response
        retrieved_chunks = []

        # ChromaDB returns nested lists for batch queries: results["documents"][0]
        documents = results.get("documents", [[]])[0] # type: ignore
        metadatas = results.get("metadatas", [[]])[0] # type: ignore
        distances = results.get("distances", [[]])[0] # type: ignore

        # 7. Zip and iterate through the matching records
        for doc, meta, dist in zip(documents, metadatas, distances):
            retrieved_chunks.append(
                {
                    "source": meta.get("source", "Unknown"),
                    "page": meta.get("page", "N/A"),
                    "similarity_score": round(1.0 - dist, 4) if dist is not None else "N/A",
                    "text": doc
                }
            )

        # 8. Check if any results were returned
        if not retrieved_chunks:
            return {
                "success": True,
                "query": query,
                "message": "No relavant document found",
                "results": []
            }

        # 9. Return successful results payload
        return {
            "success": True,
            "query": query,
            "results_count": len(retrieved_chunks),
            "results": retrieved_chunks
        }

    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "message": f"Failed to query knowledge base: {str(e)}"  # noqa: RUF010
        }

if __name__ == "__main__":
    test_query = "What does Mark Douglas say about market probabilities and risk?"
    print(f"🔍 Searching knowledge base for: '{test_query}'\n")

    output = search_knowledge_base(query=test_query, n_results=3)

    if output["status"] == "success":
        print(f"Found {output['results_count']} matching chunks:\n")
        for idx, item in enumerate(output["results"], 1):
            print(
                f"--- Result {idx} (Source: {item['source']}, Page: {item['page']}) ---" # type: ignore
            )
            print(f"Similarity Score: {item['similarity_score']}") # type: ignore
            print(f"Content: {item['text'][:250]}...\n") # type: ignore
    else:
        print(f"Error: {output['message']}")