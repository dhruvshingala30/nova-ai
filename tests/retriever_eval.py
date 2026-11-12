import json
import os
import sys
from pathlib import Path

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, ErrorConfig
from deepeval.metrics import ContextualPrecisionMetric, ContextualRecallMetric
from deepeval.models import OpenRouterModel
from deepeval.test_case import LLMTestCase

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import GROQ_API_KEY
from app.tools.knowledge_base_search import search_knowledge_base

os.environ["DEEPEVAL_API_TIMEOUT"] = "300"
os.environ["DEEPEVAL_PER_ATTEMPT_TIMEOUT"] = "120"
os.environ["DEEPEVAL_DISABLE_TIMEOUTS"] = "1"
os.environ["DEEPEVAL_SDK_RETRY_PROVIDERS"] = '["*"]'


judge = OpenRouterModel(
    model="openai/gpt-4o-mini",
    api_key=GROQ_API_KEY,
    temperature=0.0,  # Crucial: Keep temperature at 0 for deterministic evaluation
)

async_config = AsyncConfig(
    run_async=True,
    max_concurrent=5,
    throttle_value=2,
)

error_config = ErrorConfig(
    ignore_errors=True,
)

with open("goldens.json") as f:
    goldens = json.load(f)

def build_test_cases():
    test_cases = []
    for item in goldens:
        retrieval_result = search_knowledge_base(query=item["query"], n_results=3)

        # DeepEval requires a list of strings for retrieval_context.
        retrieved_texts = []

        if isinstance(retrieval_result, dict) and retrieval_result.get("success"):
            results_data = retrieval_result.get("results", "")

            if isinstance(results_data, list):
                retrieved_texts = [res["text"] for res in results_data if isinstance(res, dict) and "text" in res]

        test_case = LLMTestCase(
            input=item["query"],
            expected_output=" ".join(item["ideal_answer"]),
            retrieval_context=retrieved_texts,
        )
        test_cases.append(test_case)

    return test_cases


if __name__ == "__main__":
    test_cases = build_test_cases()
    metrics = [
        ContextualPrecisionMetric(
            threshold=0.7,
            model=judge,
            include_reason=True,
        ),
        ContextualRecallMetric(
            threshold=0.7, 
            model=judge,
            include_reason=True,
        ),
    ]

    evaluate(
        test_cases=test_cases,
        metrics=metrics,
        async_config=async_config,
        error_config=error_config,
    )
