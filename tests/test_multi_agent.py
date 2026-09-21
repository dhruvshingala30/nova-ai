"""
tests/test_multi_agent.py - Verification & Benchmark Suite for Multi-Agent Collaboration.

Tests:
1. ResearchAgent + DataAnalystAgent compound delegation.
2. DocVisionAgent RAG retrieval + DataAnalystAgent verification.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.orchestrator import MultiAgentOrchestrator


def run_multi_agent_tests():
    """Runs end-to-end multi-agent verification scenarios."""
    print("=" * 80)
    print("🧪 RUNNING NOVA-AI MULTI-AGENT COLLABORATION TEST SUITE")
    print("=" * 80 + "\n")

    orchestrator = MultiAgentOrchestrator(session_id="test_multi_agent_session")

    test_queries = [
        (
            "Weather + Data Analysis Pipeline",
            "Fetch the current temperature in Mumbai and Delhi, then use Python to calculate their difference.",
        ),
        (
            "Knowledge Base Retrieval",
            "According to the Mark Douglas trading book in my workspace, what is the failure rate percentage for traders?",
        ),
    ]

    for name, query in test_queries:
        print(f"\n--- Running Scenario: {name} ---")
        start_t = time.time()
        try:
            result = orchestrator.run(query)
            elapsed = time.time() - start_t

            # Verify that a valid non-empty response was produced
            assert result and len(result.strip()) > 0, (
                "Empty response returned from orchestrator"
            )

            print(f"✅ PASS: Completed in {elapsed:.2f}s")
            print(f"   Preview: {result[:120]}...\n")
            
        except Exception as e:  # noqa: BLE001
            print(f"❌ FAIL: Exception occurred: {e}")

    print("\n" + "=" * 80)
    print("🎉 MULTI-AGENT EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_multi_agent_tests()
