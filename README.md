# FableBreaker Benchmark

**The adversarial evaluation framework where performance claims are worthless without correctness proof.**

[![Pylint](https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK/actions/workflows/pylint.yml/badge.svg)](https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK/actions/workflows/pylint.yml)

---

## Overview

FableBreaker is a rigorous, reproducible benchmark system designed to invalidate false performance claims in AI-generated code optimization. Unlike conventional benchmarks that reward speed in isolation, FableBreaker enforces a foundational constraint:

> **Speedup is certified if and only if semantic correctness survives adversarial, hidden-seed evaluation.**

Any candidate that produces a single incorrect output on any hidden test case receives zero certification — regardless of measured speedup.

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

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **AST Language** | Defines the expression grammar under evaluation | `fablebreaker/fablebreaker/astlang.py` |
| **Generator** | Produces deterministic datasets from seed values | `fablebreaker/fablebreaker/generator.py` |
| **Scorer** | Measures correctness and performance against hash-locked outputs | `fablebreaker/fablebreaker/scorer.py` |
| **Audit Runner** | End-to-end certification pipeline | `fablebreaker/tools/run_full_audit.py` |
| **Service** | HTTP interface for programmatic access | `fablebreaker_service.py` |

---

## Certification Protocol

1. **Public Dataset** — Candidates develop against a known set of expressions with published expected hashes.
2. **Hidden Dataset** — Certification runs against a secret-seed-generated corpus never exposed to candidates.
3. **Hash Verification** — Every output is canonicalized and SHA-256 hashed. A single mismatch disqualifies.
4. **Performance Measurement** — Only hash-verified candidates receive speedup scores (median, p95, baseline ratio).

---

## Quick Start

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

## Research Journal

FableBreaker publishes peer-reviewed research across five principal journals:

| Journal | Focus Area |
|---------|------------|
| **[Journal of Adversarial Evaluation](journal/adversarial-evaluation/index.html)** | Adversarial test generation and evaluator stress testing |
| **[Journal of Benchmark Architecture](journal/benchmark-architecture/index.html)** | Game-resistant evaluation system design |
| **[Journal of Certification Systems](journal/certification-systems/index.html)** | Cryptographic evidence and trust protocols |
| **[Journal of Semantic Preservation](journal/semantic-preservation/index.html)** | Formal verification of evaluator correctness |
| **[Journal of Reproducibility Methods](journal/reproducibility-methods/index.html)** | Deterministic generation and measurement frameworks |

**[Browse the Full Journal →](journal/index.html)**

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
├── benchmark-certification/         # Certification infrastructure
│   ├── suites/                      # Suite implementations
│   ├── services/                    # HTTP service layer
│   ├── certification/               # Evidence and manifests
│   └── manifests/                   # Configuration manifests
├── journal/                         # Research publications (HTML/PDF-style)
│   ├── adversarial-evaluation/      # Journal papers
│   ├── benchmark-architecture/      # Journal papers
│   ├── certification-systems/       # Journal papers
│   ├── semantic-preservation/       # Journal papers
│   └── reproducibility-methods/     # Journal papers
├── benchmark-manifest.json          # Suite registry
├── evidence-pack-template.json      # Evidence pack schema
├── PACKET_POLICY.md                 # Production packet requirements
└── PRODUCT_STRATEGY.md              # Strategic positioning
```

---

## Design Principles

1. **Correctness Before Speed** — No optimization claim is valid without hash-verified semantic equivalence.
2. **Adversarial by Default** — Hidden seeds, erasure traps, deep nesting, and overflow cases are standard.
3. **Reproducibility Guaranteed** — Identical seed produces identical dataset on any conforming platform.
4. **Transparency of Method** — Generator, scorer, and reference evaluator are open source and auditable.
5. **Cryptographic Integrity** — SHA-256 hash locking prevents output forgery and ensures non-repudiation.

---

## Production Packet Policy

All release artifacts conform to `PACKET_POLICY.md`: complete production ZIP archives containing source code, datasets, manifests, score outputs, and human-readable documentation. Every artifact is structured for review by both human researchers and automated systems.

---

## License

This project is licensed under the terms specified in [LICENSE](LICENSE).

---

## Contributing

Candidates, adversarial families, and scoring improvements are accepted via pull request. All submissions must pass the full audit pipeline and maintain hash integrity across public and hidden datasets.

---

<p align="center">
  <strong>ItsNotAI LABS</strong><br>
  <em>Proof before speed. Correctness before claims. Reproducibility before trust.</em>
</p>
