"""
app/core/hyde.py - Hypothetical Document Embeddings (HyDE) Generator for NovaAI.
Leverages the local Ollama instance to generate synthetic document passages
before dense vector search in ChromaDB.
"""
import logging
import sys
from pathlib import Path

from ollama import Client, ResponseError

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    CLOUD_BASE_URL,
    CLOUD_MODEL_NAME,
    GROQ_API_KEY,
    MODEL_NAME,
    OLLAMA_HOST,
    USE_CLOUD_LLM,
)
from app.prompts import DEFAULT_HYDE_PROMPT

logger = logging.getLogger(__name__)

class HyDEGenerator:
    """
    Generates hypothetical document passages using local Ollama LLMs
    to improve dense similarity retrieval against ChromaDB collections.
    """
    def __init__(
            self,
            prompt_template: str = DEFAULT_HYDE_PROMPT,
            temperature: float = 0.2,
    ) -> None:
        """
        Args:
            host: Host URL of the local Ollama server.
            model_name: Local model identifier (e.g., 'qwen2.5:7b').
            prompt_template: Formatting prompt with '{query}' placeholder.
            temperature: Low temperature (0.1 - 0.3) for focused factual phrasing.
        """
        if USE_CLOUD_LLM:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url=CLOUD_BASE_URL,
                timeout=30,
            )
            self.model = CLOUD_MODEL_NAME
        else:
            self.client = Client(host=OLLAMA_HOST)
            self.model = MODEL_NAME
            self.prompt_template = prompt_template
            self.temperature = temperature

        self.prompt_template = prompt_template
        self.temperature = temperature


    def generate(self, query: str) -> str:
        """
        Generates a hypothetical passage for a given query.
        Falls back to the raw query on any exception or empty response.

        Args:
            query (str): The raw user search query.

        Returns:
            str: Generated synthetic passage or the original query as fallback.
        """
        # Guard against empty or ultra-short queries
        if not query or len(query) < 4:
            return query

        # Replacing 'query' placeholder in prompt by user query
        formatted_prompt = self.prompt_template.format(query=query)

        try:
            if USE_CLOUD_LLM:
                response = self.client.chat.completions.create( # type: ignore
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {
                            "role": "user",
                            "content": formatted_prompt,
                        }
                    ],
                    temperature=self.temperature,
                )
                hypothetical_doc = response.choices[0].message.content or "{}"
                cleaned_doc = hypothetical_doc.strip()
                
            else: 
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": formatted_prompt,
                        }
                    ],
                    options={
                        "temperature": self.temperature,
                        "num_predict": 180,
                    },
                ) # type: ignore

                hypothetical_doc = response.message.content or ""
                cleaned_doc = hypothetical_doc.strip()

                print("[HyDe] Generated synthetic passage for query")

            if cleaned_doc:
                return cleaned_doc

            logger.warning("[HyDe] Model produced an empty message, falling back to the raw query.")
            return query

        except ResponseError as re:
            logger.warning(f"[HyDE] Ollama API error: ({re}), falling back to the raw query.")
            return query
        
        except Exception as e:  # noqa: BLE001
            logger.warning(f"[HyDE] Unexpected generation failure: ({e}), falling back to the raw query")
            return query

# Singleton instance for direct import across NovaAI tools
hyde_generator = HyDEGenerator()

if __name__ == "__main__":
    test_query = "What does Mark Douglas say about market probabilities and risk?"
    print("--- Testing HyDE Generation locally ---")
    synthetic_doc = hyde_generator.generate(test_query)
    print(f"Query: {test_query}\n")
    print(f"Generated Synthetic Document:\n{synthetic_doc}")