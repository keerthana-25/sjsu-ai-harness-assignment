"""
Part C showcase: runs the autoresearch harness on the sample digit-classifier
task and prints the optimization trajectory.

Run:
    export OPENROUTER_API_KEY="sk-or-..."
    python3 demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "plugins" / "autoresearch"))

from autoresearch import run_autoresearch, write_trajectory  # noqa: E402

TASK_DIR = Path(__file__).parent / "plugins" / "autoresearch" / "tasks" / "digits_classifier"
OUT_DIR = Path(__file__).parent / "plugins" / "autoresearch" / "runs" / "demo"

if __name__ == "__main__":
    result = run_autoresearch(TASK_DIR, iterations=5, timeout=30, model=None or __import__("llm").DEFAULT_MODEL)
    write_trajectory(result, OUT_DIR)

    print(f"\n{'=' * 60}")
    print(f"AutoResearch demo complete — best metric: {result['best_metric']:.4f}")
    print(f"{'=' * 60}")
    for h in result["history"]:
        status = "KEPT" if h["kept"] else "reverted"
        metric = f"{h['metric']:.4f}" if h["metric"] is not None else "FAILED"
        print(f"  attempt {h['iteration']}: {status:8s} metric={metric}  {h['note']}")
    print(f"\nFull trajectory: {OUT_DIR}/trajectory.md")
