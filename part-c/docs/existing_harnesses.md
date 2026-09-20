# Existing AutoResearch harnesses (research)

## The pattern

"AutoResearch" originates from Andrej Karpathy's `program.md` — a single
markdown prompt, not a framework — that instructs a coding agent (Claude
Code, Codex, or similar) to run an unattended optimization loop:

> The agent edits one file (`train.py`), runs for a fixed time budget, checks
> whether the metric improved, and either commits the change or reverts it.
> Then it loops forever.

The insight isn't the code — it's that a capable coding agent, wrapped in a
tight **propose → run → measure → keep-or-revert** loop, can be a research
scientist for narrow, metric-driven tasks. The community-curated list
[`WecoAI/awesome-autoresearch`](https://github.com/WecoAI/awesome-autoresearch)
(1k★) tracks concrete implementations across wildly different domains, each
with a public optimization trace:

| Project | Optimizes | Core loop |
|---|---|---|
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) (original) | nanoGPT training loss | Edit `train.py` → run 5 min on GPU → commit/revert |
| [autokernel](https://github.com/RightNow-AI/autokernel) | CUDA kernel TFLOPS | Kernel edits → benchmark → iterate |
| [tennis-xgboost-autoresearch](https://github.com/buildoak/tennis-xgboost-autoresearch) | ATP/WTA match prediction | Feature/hyperparameter tuning → eval → iterate |
| [BTCautoresearch](https://github.com/CBaquero/BTCautoresearch) | BTC price RMSE | Formula discovery → 328 experiments → evaluation |
| [autoresearch-rl](https://github.com/vivekvkashyap/autoresearch-rl) | Qwen GSM8K eval | Hyperparameter search → benchmark → loop |
| [autozyme](https://github.com/ElliotXie/autozyme) | Bioinformatics runtime | Autonomous optimization across 45 tasks, up to 1482x speedup |

Every entry is the same four-stage loop applied to a different metric and a
different file. That's the harness contract worth implementing generically:
**a task is just a script that prints a metric; the harness doesn't need to
know what the metric means.**

## Comparable prior art outside this list

- **AIDE** (Weco AI, [weco-ai/aideml](https://github.com/WecoAI/aideml)) —
  the closest formalized version of this idea: tree-search over solution
  drafts for Kaggle-style ML engineering tasks, scoring each with the
  competition metric. AutoResearch is the "just loop and keep the best"
  simplification of AIDE's tree search.
- **MLE-bench** (OpenAI) — a benchmark (not a harness) for scoring exactly
  this kind of agent on real Kaggle competitions; useful as an evaluation
  target for a harness like this one, not a harness itself.

## What this repo builds (`plugins/autoresearch/`)

A minimal, from-scratch AutoResearch harness, in the spirit of the original
`program.md` but implemented as an actual runnable tool rather than a prompt
handed to an interactive coding agent:

- **Task contract**: any directory with a `train.py` that prints
  `METRIC: <float>` to stdout on success. The harness never inspects what
  the script does — same design choice the whole awesome-autoresearch list
  converges on independently, from CUDA kernels to Bitcoin price formulas.
- **Loop**: propose (LLM rewrites the file) → run (subprocess, timeout) →
  measure (parse the metric) → keep-or-revert (file-backup, not full git,
  see the plugin README for why) → log (JSON + markdown trajectory, mirroring
  the "public optimization trace" every awesome-autoresearch entry links).
- **Model**: routed through OpenRouter's free tier (same setup as Part B),
  so running it costs nothing.

Sample task included: `tasks/digits_classifier/` (scikit-learn's `load_digits`
handwritten-digit dataset, validation accuracy as the metric) — chosen
because it trains in well under a second on CPU with no downloads, so a full
multi-iteration research loop runs in seconds instead of the 5-minute GPU
budget the original uses.
