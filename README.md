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

### Part B: DeepSeek Harness + Plugins (IN PROGRESS)

Install and customize DeepSeek harness with 5-7 plugins, including 2 from scratch.

- **Status**: Harness installed, Creator Mode confirmed (shipped `cordis` agent preset), 2 custom plugins built and verified end-to-end. Live agent run pending a `DEEPSEEK_API_KEY`.
- **Location**: `/part-b/` (see its [README](part-b/README.md) for full details)
- **Requirements**:
  - [x] Install DeepSeek harness in Creator Mode
  - [x] Implement 2 plugins from scratch (`session-digest`, `repo-doctor` — unit tested + verified mounting in a live `dsh` profile)
  - [ ] Customize with 5-7 plugins (2 done; 5 more picked from the course list, install commands documented, not yet installed)
  - [ ] Showcase prompt and demo (prompt written; needs `DEEPSEEK_API_KEY` to run live)
  
---

### Part C: Custom ML Harness Plugin (PENDING)

Build a custom ML harness plugin for end-to-end auto-research.

- **Status**: Pending
- **Location**: `/part-c/`
- **Requirements**:
  - Create custom ML harness plugin
  - Use favorite coding assistant (open or closed source)
  - Research existing harnesses on GitHub
  - Showcase working implementation

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
    ├── README.md               # Part C documentation (pending)
    └── plugins/                # ML harness plugins (pending)
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
- [x] Part B: Plugin implementations (2 of 2 from-scratch plugins done; 5 pre-built plugins picked, not yet installed)
- [ ] Part B: Demo and documentation (showcase prompt written; needs `DEEPSEEK_API_KEY` to run live)
- [ ] Part C: ML harness plugin
- [ ] Part C: GitHub research and showcase
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
