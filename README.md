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
| **AST Language** | Defines the expression grammar under evaluation (18+ ops including `if_zero`, `neg`, `abs`, `sub`, `band`, `bor`, `fold_list`, `seq`) | `fablebreaker/fablebreaker/astlang.py` |
| **Generator** | Produces deterministic datasets from seed values across 8 adversarial families | `fablebreaker/fablebreaker/generator.py` |
| **Scorer** | Measures correctness and performance with per-family breakdown and 95% confidence intervals | `fablebreaker/fablebreaker/scorer.py` |
| **Audit Runner** | End-to-end certification pipeline | `fablebreaker/tools/run_full_audit.py` |
| **Service** | Versioned HTTP API (`/api/v1/`) with CORS, rate limiting, and structured logging | `fablebreaker_service.py` |
| **Governance** | Role-based authority model for certification integrity | `GOVERNANCE.md` |

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
python fablebreaker_service.py --host 127.0.0.1 --port 8787 --log-level INFO
```

### Verify the Service (Versioned API)

```bash
curl http://127.0.0.1:8787/api/v1/health
curl http://127.0.0.1:8787/api/v1/manifest
curl http://127.0.0.1:8787/api/v1/status
curl http://127.0.0.1:8787/api/v1/candidates
curl http://127.0.0.1:8787/api/v1/families
```

### Submit a Candidate for Scoring

```bash
curl -X POST http://127.0.0.1:8787/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"candidate": "candidates.baseline_candidate", "dataset": "dataset/public.jsonl"}'
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

FableBreaker publishes peer-reviewed research across five principal journals (14 papers published):

| Journal | Focus Area | Papers |
|---------|------------|--------|
| **[Journal of Adversarial Evaluation](journal/adversarial-evaluation/index.html)** | Adversarial test generation and evaluator stress testing | 3 |
| **[Journal of Benchmark Architecture](journal/benchmark-architecture/index.html)** | Game-resistant evaluation system design | 3 |
| **[Journal of Certification Systems](journal/certification-systems/index.html)** | Cryptographic evidence, trust protocols, and governance | 3 |
| **[Journal of Semantic Preservation](journal/semantic-preservation/index.html)** | Formal verification of evaluator correctness | 2 |
| **[Journal of Reproducibility Methods](journal/reproducibility-methods/index.html)** | Deterministic generation, measurement, and API automation | 3 |

**Foundation Paper:** [https://doi.org/10.5281/zenodo.20589250](https://doi.org/10.5281/zenodo.20589250)

**[Browse the Full Journal →](journal/index.html)** · **[Editorial Board →](journal/editorial-board.html)**

---

## Protocol SDK

All journal protocols are available as importable Python modules in the `fablebreaker.protocols` package:

```python
from fablebreaker.protocols import (
    OverflowCorridorProtocol,      # Adversarial overflow corridor generation
    ConditionalCascadeProtocol,    # Nested conditional cascade generation
    GovernanceCertificationProtocol,  # Governance-aware evidence chains
    PerFamilyScoringProtocol,      # Per-family scoring with confidence intervals
    APIReproducibilityProtocol,    # HTTP API client for benchmark automation
    ProtocolRegistry,              # Registry of all 14 papers and their SDK bindings
    FOUNDATION_DOI,                # "10.5281/zenodo.20589250"
)

# Generate adversarial overflow corridor cases
corridor = OverflowCorridorProtocol()
result = corridor.generate(seed=42, size=30)

# Compute per-family scoring breakdown
scoring = PerFamilyScoringProtocol()
report = scoring.compute(cases, candidate_times, baseline_times, failures)

# Create governance-aware certification evidence
gov_protocol = GovernanceCertificationProtocol()
pack = gov_protocol.create_evidence_pack(...)

# Query the full paper registry
registry = ProtocolRegistry()
print(registry.summary())  # 14 papers across 5 journals
```

---

## Project Structure

```
FABLEBREAKER-BENCHMARK/
├── fablebreaker/                    # Core benchmark suite
│   ├── fablebreaker/                # Evaluator, generator, scorer
│   │   └── protocols/              # Protocol SDK (all 14 paper implementations)
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
├── journal/                         # Research publications (14 papers)
│   ├── adversarial-evaluation/      # 3 papers
│   ├── benchmark-architecture/      # 3 papers
│   ├── certification-systems/       # 3 papers
│   ├── semantic-preservation/       # 2 papers
│   ├── reproducibility-methods/     # 3 papers
│   └── editorial-board.html         # Editorial board & review standards
├── GOVERNANCE.md                    # Project governance model
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
