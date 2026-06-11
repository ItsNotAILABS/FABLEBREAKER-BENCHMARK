# FableBreaker Benchmark Manifest

## Activated Internal Brains

- CODEX/PARX: executable AST language, parser-free JSON format, compile checks.
- STRU/RTMX: evaluator state model, dynamic matching, erasure, duplication, repeat loops.
- TEST/BENC: correctness hashes, generated cases, scorer, hidden-seed path.
- SIGNAL/SACE: audit packet, proof trail, reproducible commands.

## Connected Surface Interpretation

The linked claim sits in the public model-benchmark surface, but the real production issue is deeper:
speedup claims around evaluator internals are only meaningful when the workload distribution and
semantic preservation are inspectable. This packet turns that public claim into a local proof surface.

## Frequency / Pressure Read

The pressure pattern is hype compression: one high peak number becomes social proof. FableBreaker
expands the compression into a reproducible benchmark contract where correctness, hidden cases, and
failure modes have to survive before speed is allowed to matter.

## Build / Workflow Architecture

1. Generate deterministic public cases from a seed.
2. Store each case with expected canonical output hash and reference stats.
3. Let candidates implement only `evaluate(expr)`.
4. Score candidate output against hashes.
5. Report no speed certification if any case fails.
6. Regenerate hidden splits for independent claims.

## Missing Engines / Modules

- Native adapters for Rust, Julia, TypeScript, and Motoko.
- Memory profile gate for evaluator allocation behavior.
- Per-family confidence interval reporting.
- CI workflow that runs public plus rotating hidden seeds.

## Test + Benchmark Matrix

| Axis | Gate |
|---|---|
| Unit correctness | `python -m unittest discover -s tests` |
| Dataset integrity | generator recomputes expected hashes |
| Candidate correctness | scorer hash match |
| Speed evidence | total, median, p95, baseline-relative |
| Anti-cherry-pick | six workload families |
| Hidden proof | seed-regenerated hidden split |

## Native Suite Opportunity

This can become a larger evaluator-optimization suite:

- Python harness as orchestration layer.
- Julia engine for large synthetic graph generation and statistics.
- Motoko registry canister for signed benchmark manifests and immutable score submissions.
- Nexus registry record for candidate lineage, score provenance, and hidden-seed audit release.

## Proof Signal

The immediate proof signal is modest but real: this packet runs locally, generates data, verifies
hashes, scores a candidate, and produces an audit artifact. It does not ask anyone to believe a
thread; it asks them to run commands.

## Monitor Next

Ask several AIs to optimize `candidates/baseline_candidate.py` or write a new evaluator module.
Accept a claim only if the optimized evaluator passes public and hidden splits with zero failures.
