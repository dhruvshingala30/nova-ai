"""
test_eval_suite.py - Automated Evaluation Test Suite for NovaAI.

Runs zero-shot intent routing benchmarks, schema validation tests,
multi-step planning evaluations, and sandbox security checks.
"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import NovaAI
from app.core.workspace_manager import workspace


class NovaEvalHarness:
    """
    Benchmark runner for agent routing, planning, and tool execution.
    """
    def __init__(self) -> None:
        self.results = []

    def record(self, test_name: str, passed: bool, details: str, latency: float):
        self.results.append({
            "name": test_name,
            "passed": passed,
            "details": details,
            "latency": f"{latency:.2f}s"
        })

    def run_routing_test(self, query: str, expected_step: str, expected_tool: str | None = None):
        """
        Tests the initial reasoning step and tool selection of the agent.
        """
        agent = NovaAI(session_id=f"eval_{int(time.time()*1000)}")
        agent.add_message(
            role="user",
            content=query,
        )

        parsed = agent.chat()

        if parsed.STEP != expected_step:
            return False, f"Expected step '{expected_step}', got '{parsed.STEP}'."

        if expected_tool and parsed.TOOL != expected_tool:
            return False, f"Expected tool '{expected_tool}', got '{parsed.TOOL}'."

        return True, f"Correctly selected '{parsed.STEP}'" + (f" -> {parsed.TOOL}" if expected_tool else "")

    def run_all(self):
        print("\n" + "=" * 80)
        print("🧪 STARTING NOVA-AI AUTOMATED EVALUATION SUITE")
        print("=" * 80 + "\n")

        # ---------------------------------------------------------
        # 1. TOOL ROUTING EVALUATIONS
        # ---------------------------------------------------------
        test_cases = [
            (
                "Weather Tool Routing",
                "What is the current temperature in Paris right now?",
                "TOOL",
                "get_weather",
            ),
            (
                "Code Interpreter Math Routing",
                "Calculate the determinant of matrix [[4, 2], [1, 7]] using python",
                "TOOL",
                "run_python_code",
            ),
            (
                "Workspace File Discovery Routing",
                "What files are currently in my workspace directory?",
                "TOOL",
                "list_workspace_files",
            ),
            (
                "Knowledge Base Document Search Routing",
                "According to the Mark Douglas trading book, what is the failure rate percentage?",
                "TOOL",
                "search_knowledge_base",
            ),
            (
                "Compound Multi-Step Planner Trigger",
                "Compare the weather in London and Tokyo, then compute the difference using Python",
                "PLAN",
                None,
            ),
        ]

        for name, query, exp_step, exp_tool in test_cases:
            start_t = time.time()
            try:
                passed, details = self.run_routing_test(query, exp_step, exp_tool)
            except Exception as e:  # noqa: BLE001
                passed = False
                details = f"Exception: {str(e)}"  # noqa: RUF010
            latency = time.time() - start_t
            self.record(name, passed, details, latency)

        # ---------------------------------------------------------
        # 2. WORKSPACE SECURITY & PATH RESOLUTION EVALUATIONS
        # ---------------------------------------------------------
        start_t = time.time()
        try:
            # Test path alias stripping
            path = str(PROJECT_ROOT / "nova_workspace/users.csv")
            safe_p = workspace.resolve_safe_path(path)
            passed = safe_p.name == "users.csv"
            details = f"Resolved alias correctly to: {safe_p.name}"
        except Exception as e:  # noqa: BLE001
            passed = False
            details = f"Path alias resolution failed: {str(e)}"  # noqa: RUF010
        self.record(
            "Workspace Path Alias Normalization", passed, details, time.time() - start_t
        )

        start_t = time.time()
        try:
            # Test Path Traversal Protection
            workspace.resolve_safe_path("../../etc/passwd")
            passed = False
            details = "Failed: Did not raise PermissionError on traversal attack."
        except PermissionError:
            passed = True
            details = "Blocked path traversal attack successfully."
        except Exception as e:  # noqa: BLE001
            passed = False
            details = f"Unexpected error on traversal test: {str(e)}"  # noqa: RUF010
        self.record(
            "Workspace Traversal Security Guard", passed, details, time.time() - start_t
        )

        # ---------------------------------------------------------
        # PRINT SUMMARY REPORT
        # ---------------------------------------------------------
        print("\n" + "=" * 80)
        print("📊 EVALUATION RESULTS SUMMARY")
        print("=" * 80)
        print(f"{'Test Name':<42} | {'Status':<8} | {'Latency':<8} | {'Details'}")
        print("-" * 80)

        all_passed = True
        for res in self.results:
            status_icon = "✅ PASS" if res["passed"] else "❌ FAIL"
            if not res["passed"]:
                all_passed = False
            print(
                f"{res['name']:<42} | {status_icon:<8} | {res['latency']:<8} | {res['details']}"
            )

        print("=" * 80)
        if all_passed:
            print("🎉 ALL TEST CASES PASSED SUCCESSFULLY!\n")
        else:
            print("⚠️ SOME BENCHMARK TESTS FAILED. CHECK LOGS ABOVE.\n")


if __name__ == "__main__":
    harness = NovaEvalHarness()
    harness.run_all()