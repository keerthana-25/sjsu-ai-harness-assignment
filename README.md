# SJSU AI Harness Assignment — 3-Part Portfolio

**Course**: SJSU MSSE / CMPE (Data Science Program)  
**Student**: Keerthana  
**Due**: TBD

---

## Assignment Overview

Build a complete AI coding harness system through 3 progressive parts, from core implementation to advanced features.

### Part A: Basic Coding Harness ✅ COMPLETE

Implement a minimal coding harness from scratch using OpenRouter API.

- **Status**: Complete
- **Location**: `/part-a/`
- **Key Features**:
  - OpenRouter API integration (supports 100+ models)
  - Three tools: bash_tool, read_file, write_file
  - Agent loop with multi-turn tool use
  - ~170 lines of clean Python
  
**To run**:
```bash
cd part-a
pip install openai
export OPENROUTER_API_KEY="sk-your_key"
python part_a_openrouter.py
```

---

### Part B: DeepSeek Harness + Plugins (COMPLETE)

Install and customize DeepSeek harness with 5-7 plugins, including 2 from scratch.

- **Status**: Harness installed, Creator Mode confirmed (shipped `cordis` agent preset), 7 plugins total mounted together (2 from scratch, 5 from the community list — all reviewed and verified live by actually booting the web server, not just config validation), showcase prompt run live end-to-end for free via OpenRouter (DeepSeek's own API needs a funded account, which wasn't required — see Part B README for the free-alternative setup).
- **Location**: `/part-b/` (see its [README](part-b/README.md) for full details)
- **Requirements**:
  - [x] Install DeepSeek harness in Creator Mode
  - [x] Implement 2 plugins from scratch (`session-digest`, `repo-doctor` — unit tested + verified mounting in a live `dsh` profile)
  - [x] Customize with 5-7 plugins (2 from scratch + 5 community plugins, all installed and verified; two had real packaging bugs found and fixed in review — see Part B README)
  - [x] Showcase prompt and demo (run live, $0 cost, via OpenRouter's free-tier models)
  
---

### Part C: Custom ML Harness Plugin (COMPLETE)

Build a custom ML harness plugin for end-to-end auto-research.

- **Status**: Built and run live, end-to-end, for free. Implements the "AutoResearch" pattern (Karpathy's `program.md`, tracked by `WecoAI/awesome-autoresearch`): an LLM proposes an edit to a training script, the harness runs it and keeps or reverts based on the metric. Sample run took a digit classifier from 42.5% to 98.06% accuracy in 5 iterations, fully unattended.
- **Location**: `/part-c/` (see its [README](part-c/README.md) for full details and results)
- **Requirements**:
  - [x] Create custom ML harness plugin (`plugins/autoresearch/` — propose → run → measure → keep-or-revert loop)
  - [x] Use favorite coding assistant (Claude Code, this session)
  - [x] Research existing harnesses on GitHub (`docs/existing_harnesses.md` — real examples: CUDA kernel tuning, Bitcoin price formulas, RL hyperparameter search, etc.)
  - [x] Showcase working implementation (`demo.py`, real trajectory logged in `plugins/autoresearch/runs/demo/`)

---

## Directory Structure

```
sjsu-ai-harness-assignment/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
├── part-a/
│   ├── README.md               # Part A documentation
│   └── part_a_openrouter.py    # Main harness implementation
├── part-b/
│   ├── README.md               # Part B documentation
│   └── plugins/                # session-digest and repo-doctor (built from scratch)
└── part-c/
    ├── README.md               # Part C documentation
    └── plugins/autoresearch/   # the AutoResearch harness (built from scratch)
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip or conda
- OpenRouter API key (for Part A)
- DeepSeek setup (for Part B)

### Quick Start

**Part A (Completed)**:
```bash
cd part-a
pip install -r ../requirements.txt
export OPENROUTER_API_KEY="sk-..."
python part_a_openrouter.py
```

---

## Submission Checklist

- [x] Part A: Code written and tested
- [x] Part A: README with architecture explanation
- [x] Part A: Running instructions
- [x] Part B: DeepSeek harness setup
- [x] Part B: Plugin implementations (2 of 2 from-scratch plugins + 5 of 5 community plugins, all installed and verified live)
- [x] Part B: Demo and documentation (showcase prompt run live for free via OpenRouter)
- [x] Part C: ML harness plugin
- [x] Part C: GitHub research and showcase
- [ ] Overall: Tests and validation
- [ ] Overall: Final README and instructions

---

## References

**Part A**:
- Reference: github.com/dlmastery/simple-coding-harness
- OpenRouter: https://openrouter.ai/

**Part B**:
- DeepSeek Harness: github.com/awesome-dsh-plugin/awesome-dsh-plugin
- Plugin Docs: books.vizuara.ai/read/deepseek-harness

**Part C**:
- AutoResearch: github.com/WecoAI/awesome-autoresearch
- Harness Engineering: harnessengineering.vizuara.ai
- Books: github.com/wquguru/harness-books

---

## License

MIT License — See LICENSE file

---

**Last Updated**: Sept 17, 2026
