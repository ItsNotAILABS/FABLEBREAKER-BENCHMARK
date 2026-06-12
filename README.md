<div align="center">

# FableBreaker Benchmark

### The Adversarial Evaluation Framework for AI Code Optimization

*Performance claims are worthless without correctness proof.*

[![CI](https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK/actions/workflows/pylint.yml/badge.svg)](https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Certification Protocol](#certification-protocol)
- [Multi-Agent Batch Testing](#multi-agent-batch-testing)
- [Candidate Contract](#candidate-contract)
- [FableBreaker SDK](#fablebreaker-sdk)
- [Project Structure](#project-structure)
- [Research Publications](#research-publications)
- [Design Principles](#design-principles)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FableBreaker is a rigorous, reproducible benchmark system designed to invalidate false performance claims in AI-generated code optimization. Unlike conventional benchmarks that reward speed in isolation, FableBreaker enforces a foundational constraint:

> **Speedup is certified if and only if semantic correctness survives adversarial, hidden-seed evaluation.**

Any candidate that produces a single incorrect output on any hidden test case receives **zero certification** — regardless of measured speedup.

---

## Key Features

- **Correctness-first certification** — speedup scores are only granted to semantically correct candidates
- **Adversarial test generation** — hidden seeds, erasure traps, deep nesting, and overflow cases
- **Cryptographic verification** — SHA-256 hash locking ensures output integrity and non-repudiation
- **Deterministic reproducibility** — identical seed produces identical dataset on any conforming platform
- **Multi-agent batch evaluation** — test 30–100+ agents in parallel with a single command
- **HTTP service interface** — programmatic access for CI/CD integration
- **Downloadable SDK** — install locally and evaluate your own code

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FableBreaker System                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────┐  │
│  │  Generator   │──▶│   Dataset    │──▶│    Scorer    │  │
│  │ (seed → AST) │   │  (JSONL)    │   │ (hash-lock)  │  │
│  └─────────────┘   └─────────────┘   └──────────────┘  │
│         │                                      │         │
│         ▼                                      ▼         │
│  ┌─────────────┐                     ┌──────────────┐   │
│  │  Adversarial │                     │ Certification│   │
│  │   Families   │                     │    Report    │   │
│  └─────────────┘                     └──────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

| Component | Purpose | Location |
|-----------|---------|----------|
| **AST Language** | Expression grammar under evaluation | `fablebreaker/fablebreaker/astlang.py` |
| **Generator** | Deterministic dataset production from seed values | `fablebreaker/fablebreaker/generator.py` |
| **Scorer** | Correctness and performance measurement via hash-locked outputs | `fablebreaker/fablebreaker/scorer.py` |
| **Audit Runner** | End-to-end certification pipeline | `fablebreaker/tools/run_full_audit.py` |
| **Service** | HTTP interface for programmatic access | `fablebreaker_service.py` |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` package manager

### Run the Full Audit

```bash
cd fablebreaker
python tools/run_full_audit.py --candidate candidates.baseline_candidate
```

### Launch the Certification Service

```bash
python fablebreaker_service.py --host 127.0.0.1 --port 8787
```

### Verify the Service

```bash
curl http://127.0.0.1:8787/health
curl http://127.0.0.1:8787/manifest
```

### Submit a Candidate for Scoring

```bash
curl -X POST http://127.0.0.1:8787/score \
  -H "Content-Type: application/json" \
  -d '{"candidate": "candidates.baseline_candidate", "seed": 823, "count": 100}'
```

---

## Certification Protocol

The certification process follows four stages:

| Stage | Description |
|-------|-------------|
| 1. **Public Dataset** | Candidates develop against a known set of expressions with published expected hashes |
| 2. **Hidden Dataset** | Certification runs against a secret-seed-generated corpus never exposed to candidates |
| 3. **Hash Verification** | Every output is canonicalized and SHA-256 hashed; a single mismatch disqualifies |
| 4. **Performance Measurement** | Only hash-verified candidates receive speedup scores (median, p95, baseline ratio) |

---

## Multi-Agent Batch Testing

FableBreaker supports evaluating **30 to 100+ agents in parallel** with a single command — ideal for verifying which agents produce correct code and which silently break.

### Command Line

```bash
cd fablebreaker

# Auto-discover all candidates in candidates/ directory
python -m tools.batch_audit --discover candidates --count 240 --workers 4

# Test specific candidates
python -m tools.batch_audit --candidates candidates.agent_1 candidates.agent_2 candidates.agent_3

# Scan external repositories for evaluate() functions
python -m tools.batch_audit --scan-dirs /path/to/repo1 /path/to/repo2 /path/to/repo3

# Full swarm test: 100 agents, 1000 cases, multiple hidden seeds
python -m tools.batch_audit --discover candidates \
  --count 1000 \
  --hidden-seeds 1701 9999 31337 42 \
  --workers 8

# Combine all sources
python -m tools.batch_audit \
  --discover candidates \
  --scan-dirs /path/to/agent-repo-1 /path/to/agent-repo-2 \
  --candidates custom.module_1 custom.module_2 \
  --count 500 --workers 8
```

### API Endpoint

```bash
curl -X POST http://127.0.0.1:8787/batch-audit \
  -H "Content-Type: application/json" \
  -d '{
    "candidates": ["candidates.baseline_candidate", "candidates.example_multi_agent"],
    "discover": "candidates",
    "hidden_seeds": [1701, 9999, 31337],
    "count": 240,
    "workers": 4
  }'
```

### Output

The batch audit produces a consolidated report including:

| Report Section | Description |
|---------------|-------------|
| **Ranked Leaderboard** | All agents sorted by certified speedup |
| **Failure Analysis** | Which adversarial families break which agents |
| **Per-Agent Breakdown** | Exact case counts, timing, and error messages |
| **Certification Rate** | Percentage of agents producing correct output |

### Adding Your Agents

| Method | Instructions |
|--------|-------------|
| Local candidates | Place `.py` files in `fablebreaker/candidates/` with a `def evaluate(expr: dict) -> object` function |
| External repos | Point `--scan-dirs` at any directory — FableBreaker auto-discovers files with `evaluate()` |
| Custom modules | Use `--candidates` with any importable Python module path |

See [`candidates/example_multi_agent.py`](fablebreaker/candidates/example_multi_agent.py) for a template.

---

## Candidate Contract

Any candidate module must expose a single function:

```python
def evaluate(expr: dict) -> object:
    """
    Evaluate a FableBreaker AST expression and return the computed value.

    The returned value must be semantically identical to the reference evaluator's
    output for the same input. Verification is performed via SHA-256 hash of the
    canonical serialization.
    """
    ...
```

---

## FableBreaker SDK

FableBreaker is available as a **standalone SDK** for local installation and evaluation.

### Installation

```bash
pip install ./fablebreaker_sdk
```

### Python API

```python
from fablebreaker_sdk import FableBreaker

fb = FableBreaker()
result = fb.full_scan(open("your_code.py").read())
```

### CLI Usage

```bash
fablebreaker scan src/
fablebreaker review myfile.py
fablebreaker security myfile.py
fablebreaker dogfood  # evaluate own code
```

### Available Skills

| Category | Skills |
|----------|--------|
| Analysis | `analysis`, `detection`, `reasoning` |
| Generation | `generation`, `synthesis` |
| Quality | `code_review`, `coverage`, `security` |
| Maintenance | `refactoring`, `documentation`, `self_analysis` |

📖 **[Full SDK Documentation →](fablebreaker_sdk/README.md)**

---

## Project Structure

```
FABLEBREAKER-BENCHMARK/
├── fablebreaker/                    # Core benchmark suite
│   ├── fablebreaker/                # Evaluator, generator, scorer
│   ├── candidates/                  # Candidate implementations
│   ├── dataset/                     # Generated datasets (JSONL)
│   ├── reports/                     # Score outputs
│   ├── tests/                       # Integrity tests
│   └── tools/                       # Audit and utility scripts
├── fablebreaker_sdk/                # Downloadable SDK package
├── benchmark-certification/         # Certification infrastructure
│   ├── suites/                      # Suite implementations
│   ├── services/                    # HTTP service layer
│   ├── certification/               # Evidence and manifests
│   └── manifests/                   # Configuration manifests
├── journal/                         # Research publications
├── benchmark-manifest.json          # Suite registry
├── evidence-pack-template.json      # Evidence pack schema
├── PACKET_POLICY.md                 # Production packet requirements
└── PRODUCT_STRATEGY.md              # Strategic positioning
```

---

## Research Publications

FableBreaker publishes peer-reviewed research across five principal journals:

| Journal | Focus Area |
|---------|------------|
| [Journal of Adversarial Evaluation](journal/adversarial-evaluation/index.html) | Adversarial test generation and evaluator stress testing |
| [Journal of Benchmark Architecture](journal/benchmark-architecture/index.html) | Game-resistant evaluation system design |
| [Journal of Certification Systems](journal/certification-systems/index.html) | Cryptographic evidence and trust protocols |
| [Journal of Semantic Preservation](journal/semantic-preservation/index.html) | Formal verification of evaluator correctness |
| [Journal of Reproducibility Methods](journal/reproducibility-methods/index.html) | Deterministic generation and measurement frameworks |

📚 **[Browse All Publications →](journal/index.html)**

---

## Design Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Correctness Before Speed** | No optimization claim is valid without hash-verified semantic equivalence |
| 2 | **Adversarial by Default** | Hidden seeds, erasure traps, deep nesting, and overflow cases are standard |
| 3 | **Reproducibility Guaranteed** | Identical seed produces identical dataset on any conforming platform |
| 4 | **Transparency of Method** | Generator, scorer, and reference evaluator are open source and auditable |
| 5 | **Cryptographic Integrity** | SHA-256 hash locking prevents output forgery and ensures non-repudiation |

---

## Self-Evaluation (Dogfood)

FableBreaker was evaluated against its own codebase and identified **7 real issues**, including:

- Missing authentication on endpoints
- 15/16 functions lacking docstrings (documentation grade: F)
- Refactoring opportunities
- Zero-division risk

This demonstrates the system operates without self-bias — if it evaluates itself honestly, you can trust it on your code.

📝 **[Full Dogfood Report →](DOGFOOD_REPORT.md)**

---

## Contributing

Contributions are welcome via pull request. Accepted contribution types include:

- New candidate implementations
- Adversarial family definitions
- Scoring improvements
- Documentation enhancements

All submissions must pass the full audit pipeline and maintain hash integrity across public and hidden datasets.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**ItsNotAI LABS**

*Proof before speed. Correctness before claims. Reproducibility before trust.*

</div>
