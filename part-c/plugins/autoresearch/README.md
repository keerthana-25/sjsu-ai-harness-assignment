# autoresearch

A minimal, from-scratch implementation of the
[AutoResearch pattern](../../docs/existing_harnesses.md): an LLM proposes an
edit to one script, the harness runs it, and keeps the edit only if a metric
improved.

## Task contract

Any directory with a `train.py` that prints `METRIC: <float>` to stdout on
its last line (higher is better). The harness never inspects what the script
actually does — same contract every real AutoResearch project in the wild
converges on, whether it's training a language model, tuning a CUDA kernel,
or predicting Bitcoin prices.

## Run it

```sh
export OPENROUTER_API_KEY="sk-or-..."   # same key as Part A/B, free tier works
python3 autoresearch.py --task tasks/digits_classifier --iterations 5
```

Writes `runs/<timestamp>/trajectory.{json,md}` — the full attempt-by-attempt
log (kept/reverted, metric, error) — and leaves `train.py` on the
best-scoring version found.

## Design notes / deviations from Karpathy's original

- **File-backup revert, not `git commit`/`git checkout`.** The original
  pattern commits a real git repo per iteration. Running this inside the
  assignment's own repo would spam commit history for a demo loop, so
  `run_autoresearch` keeps the best-known file content in memory and writes
  it back on revert instead. Same effect (bad edits never survive), no git
  side effects. A task run against its own throwaway git repo could restore
  the original commit-per-iteration behavior with a one-line change.
- **Full-file rewrite, not a diff.** The model returns the complete new file
  each time rather than a patch. Simpler and more robust for a small file —
  no diff-apply failure mode — at the cost of more output tokens per call
  (irrelevant on a free-tier model).
- **A failed LLM call (empty response, rate limit) is recorded as a reverted
  attempt and the loop continues**, rather than crashing the run — free-tier
  endpoints are flaky (see Part B's README for the rate-limit and
  degenerate-output issues hit there), and one bad attempt shouldn't lose
  the rest of the budget.

## Files

| File | Role |
|---|---|
| `autoresearch.py` | The loop: propose → run → measure → keep-or-revert → log |
| `llm.py` | OpenRouter chat-completion call (reuses Part A's client setup) |
| `tasks/digits_classifier/train.py` | Sample task: sklearn digit classification, deliberately weak baseline |
