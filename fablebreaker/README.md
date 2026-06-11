# FableBreaker Bench

FableBreaker Bench is a reproducible counter-benchmark packet for evaluator optimization claims.
It targets the weak point of one-off speedup anecdotes: a large number can be real on one workload
and still fail as evidence if correctness, distribution breadth, adversarial cases, and auditability
are not pinned down.

This packet builds a deterministic dataset for a small graph/term rewrite evaluator with dynamic
matching, sharing, erasure, duplication, and garbage-sensitive traps. It is not a clone of HVM5.
It is a self-contained proving ground for the same class of claim: "an agent optimized an evaluator
and achieved a huge speedup." Here, speed only counts after semantic equivalence is proven.

## What This Packet Contains

- `fablebreaker/astlang.py` - the benchmark language, canonicalization, and reference semantics.
- `fablebreaker/generator.py` - deterministic public/hidden dataset generator.
- `fablebreaker/scorer.py` - correctness-first timing harness for candidate evaluators.
- `candidates/baseline_candidate.py` - adapter for the provided reference evaluator.
- `dataset/public.jsonl` - public cases with expected canonical hashes.
- `reports/audit_packet.md` - benchmark target, failure matrix, audit proof object, and next gates.

## Quick Start

```bash
cd /workspace/fablebreaker_bench
python -m fablebreaker.generator --out dataset/public.jsonl --count 240 --seed 823 --split public
python -m fablebreaker.scorer --dataset dataset/public.jsonl --candidate candidates.baseline_candidate
python -m unittest discover -s tests
```

To create a private hidden split:

```bash
python -m fablebreaker.generator --out dataset/hidden_seed_1701.jsonl --count 240 --seed 1701 --split hidden
python -m fablebreaker.scorer --dataset dataset/hidden_seed_1701.jsonl --candidate candidates.baseline_candidate
```

Or run the full audit:

```bash
python tools/run_full_audit.py --candidate candidates.baseline_candidate
```

## Candidate Contract

Create a Python module with:

```python
def evaluate(expr: dict) -> object:
    ...
```

The return value may be native Python data using `int`, `str`, `list`, and `dict`. It is normalized
by the scorer before hashing.

Run it:

```bash
python -m fablebreaker.scorer --dataset dataset/public.jsonl --candidate my_candidate_module
```

## Scoring Law

1. Correctness is binary and comes first.
2. A run with any wrong result receives no speed certification.
3. Speed is reported as distributional evidence: median, p95, total time, and baseline-relative ratio.
4. Public cases are for development; hidden generated cases are for claims.
5. The benchmark rewards robust evaluator design, not memorization of a fixed file.

## Why This Is Stronger Than a Viral Optimization Anecdote

A single benchmark can be cherry-picked. A benchmark packet with generator, semantic hashes, hidden
seeds, adversarial task families, timing distribution, and audit notes gives reviewers enough surface
area to catch false progress.
