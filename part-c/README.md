# Part C: Custom ML Harness Plugin — AutoResearch

**Status**: Built and run live, end-to-end, for free.

## What this is

An implementation of the ["AutoResearch" pattern](docs/existing_harnesses.md):
an LLM-driven **propose → run → measure → keep-or-revert** loop over one ML
training script, originating from Andrej Karpathy's `program.md` and tracked
by [`WecoAI/awesome-autoresearch`](https://github.com/WecoAI/awesome-autoresearch)
(1k★) across a dozen+ real projects — CUDA kernel tuning, Bitcoin price
formulas, RL hyperparameter search, and more. See
[`docs/existing_harnesses.md`](docs/existing_harnesses.md) for the research
behind this, with concrete linked examples.

The harness itself is domain-agnostic: it only requires a `train.py` that
prints `METRIC: <float>`. The included sample task classifies handwritten
digits (scikit-learn's `load_digits`), chosen because it trains in well
under a second on CPU with zero downloads — a full 5-iteration research loop
runs in seconds instead of the original's 5-minute GPU budget per attempt.

## Structure

```
part-c/
├── README.md
├── demo.py                              # showcase: runs the loop, prints the trajectory
├── docs/
│   └── existing_harnesses.md            # research: the AutoResearch pattern + real examples
└── plugins/autoresearch/
    ├── README.md                        # design notes, deviations from the original
    ├── autoresearch.py                  # the loop itself
    ├── llm.py                           # OpenRouter call (same client as Part A)
    └── tasks/digits_classifier/
        └── train.py                     # sample task (starts deliberately weak)
```

## Run it

```sh
export OPENROUTER_API_KEY="sk-or-..."   # same key from Part A/B, free tier
cd part-c
python3 demo.py
```

## Confirmed live run

Baseline: a shallow, untuned decision tree (`max_depth=3`) — deliberately
weak so the loop has obvious room to improve it. Model: OpenRouter's free
`nvidia/nemotron-3-super-120b-a12b:free` (same one that proved reliable for
Part B's showcase). $0 cost.

| Iteration | Status | Metric | Note |
|---|---|---|---|
| 0 | kept | 0.4250 | baseline (shallow decision tree, `max_depth=3`) |
| 1 | kept | 0.9667 | switched to a random forest |
| 2 | reverted | FAILED | provider returned an empty response (`503: Upstream error from Nvidia: Service temporarily overloaded`) — handled gracefully, loop continued |
| 3 | kept | 0.9722 | further tuning |
| 4 | kept | **0.9806** | switched to `ExtraTreesClassifier(n_estimators=200)` |
| 5 | reverted | 0.9806 | no improvement over best |

The agent found this entirely on its own — no hint about which model family to
try. Went from a 42.5%-accuracy stub to a 98.06%-accuracy ensemble classifier
in 5 iterations, correctly reverting both the one run that scored no better
and the one where the model provider itself failed.

Full attempt-by-attempt log: [`plugins/autoresearch/runs/demo/trajectory.md`](plugins/autoresearch/runs/demo/trajectory.md).

## What's left

- [ ] Try a second, structurally different task (e.g. a regression metric)
      to confirm the harness generalizes beyond classification accuracy
- [ ] Optionally restore real git commit/revert per iteration (see the
      plugin README's design notes) if this ever runs against its own repo
