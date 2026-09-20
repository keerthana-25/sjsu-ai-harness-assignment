"""
AutoResearch harness: an LLM-driven propose -> run -> measure -> keep-or-revert
loop over one task script, in the spirit of Karpathy's program.md pattern
(see ../../docs/existing_harnesses.md).

Task contract: <task_dir>/train.py prints "METRIC: <float>" to stdout on
success (higher is better). The harness never inspects what the script does.

Usage:
    python3 autoresearch.py --task tasks/digits_classifier --iterations 5
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from llm import generate

METRIC_RE = re.compile(r"METRIC:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")

SYSTEM_PROMPT = """You are an ML research agent improving one Python training \
script through repeated small edits. You will be shown the current script and \
its validation metric (higher is better), plus a short history of prior attempts.

Rules:
- Output ONLY the complete new contents of the file. No markdown code fences, \
no explanation, no commentary before or after.
- The script MUST still print "METRIC: <float>" to stdout on its last line of \
output, where float is the metric to maximize.
- Make ONE focused change per attempt (e.g. try a different model, tune one \
hyperparameter, add feature scaling) rather than rewriting everything at once.
- Keep the script fast: it must finish in a few seconds on CPU.
- Do not change what dataset is loaded or what is being predicted."""


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def run_task(train_py: Path, timeout: int) -> tuple[float | None, str]:
    """Run the task script; return (metric_or_None, error_message)."""
    try:
        result = subprocess.run(
            [sys.executable, str(train_py.name)],
            cwd=train_py.parent,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout}s"

    if result.returncode != 0:
        last_line = (result.stderr.strip().splitlines() or ["(no stderr)"])[-1]
        return None, f"exit {result.returncode}: {last_line}"

    match = METRIC_RE.search(result.stdout)
    if not match:
        return None, "no 'METRIC: <float>' line in stdout"
    return float(match.group(1)), ""


def format_history(history: list[dict]) -> str:
    if not history:
        return "(no prior attempts yet)"
    lines = []
    for h in history:
        status = "KEPT" if h["kept"] else "REVERTED"
        metric = f"{h['metric']:.4f}" if h["metric"] is not None else "FAILED"
        lines.append(f"- attempt {h['iteration']}: {status}, metric={metric}"
                     + (f", error={h['error']}" if h["error"] else ""))
    return "\n".join(lines)


def run_autoresearch(task_dir: Path, iterations: int, timeout: int, model: str) -> dict:
    train_py = task_dir / "train.py"
    best_code = train_py.read_text()

    metric, error = run_task(train_py, timeout)
    if metric is None:
        raise RuntimeError(f"baseline train.py failed before any optimization: {error}")
    best_metric = metric
    history = [{"iteration": 0, "metric": metric, "kept": True, "error": "", "note": "baseline"}]
    print(f"[baseline] METRIC={metric:.4f}")

    for i in range(1, iterations + 1):
        current_code = train_py.read_text()
        user_prompt = (
            f"Current script (achieves METRIC={best_metric:.4f}, the best so far):\n\n"
            f"```python\n{current_code}\n```\n\n"
            f"Attempt history:\n{format_history(history)}\n\n"
            "Propose ONE improved version of this script."
        )
        try:
            raw = generate(SYSTEM_PROMPT, user_prompt, model=model)
        except Exception as e:  # provider hiccup, rate limit, etc. - skip this attempt
            note = f"reverted: LLM call failed ({e})"
            print(f"[iter {i}] {note}")
            history.append({"iteration": i, "metric": None, "kept": False, "error": str(e), "note": note})
            continue
        proposed_code = strip_code_fence(raw)

        train_py.write_text(proposed_code)
        metric, error = run_task(train_py, timeout)

        if metric is not None and metric > best_metric:
            note = f"kept: {best_metric:.4f} -> {metric:.4f} (+{metric - best_metric:.4f})"
            best_metric = metric
            best_code = proposed_code
            kept = True
        else:
            train_py.write_text(best_code)  # revert
            if metric is None:
                note = f"reverted: run failed ({error})"
            else:
                note = f"reverted: {metric:.4f} <= best {best_metric:.4f}"
            kept = False

        print(f"[iter {i}] {note}")
        history.append({"iteration": i, "metric": metric, "kept": kept, "error": error, "note": note})

    train_py.write_text(best_code)  # ensure the file ends on the best-known version
    return {
        "task": str(task_dir),
        "model": model,
        "iterations": iterations,
        "best_metric": best_metric,
        "history": history,
    }


def write_trajectory(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "trajectory.json").write_text(json.dumps(result, indent=2))

    lines = [
        f"# AutoResearch trajectory — {result['task']}",
        "",
        f"Model: `{result['model']}`  ",
        f"Iterations: {result['iterations']}  ",
        f"Best metric: **{result['best_metric']:.4f}**",
        "",
        "| Iteration | Status | Metric | Note |",
        "|---|---|---|---|",
    ]
    for h in result["history"]:
        status = "kept" if h["kept"] else "reverted"
        metric = f"{h['metric']:.4f}" if h["metric"] is not None else "FAILED"
        lines.append(f"| {h['iteration']} | {status} | {metric} | {h['note']} |")
    (out_dir / "trajectory.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, type=Path, help="Task directory containing train.py")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=30, help="Per-run timeout in seconds")
    parser.add_argument("--model", default=None, help="OpenRouter model id (defaults to a free model)")
    parser.add_argument("--out", type=Path, default=None, help="Trajectory output dir")
    args = parser.parse_args()

    model = args.model or __import__("llm").DEFAULT_MODEL
    result = run_autoresearch(args.task, args.iterations, args.timeout, model)

    out_dir = args.out or Path("runs") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_trajectory(result, out_dir)
    print(f"\nBest metric: {result['best_metric']:.4f}")
    print(f"Trajectory written to {out_dir}/")


if __name__ == "__main__":
    main()
