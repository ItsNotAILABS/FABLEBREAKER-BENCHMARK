# FableBreaker Benchmark Audit Packet

## Benchmark Targets

- Semantic-preserving evaluator optimization.
- Dynamic match behavior under changing tags and nested dispatch.
- Erasure correctness: dead branches must not evaluate hidden failing expressions.
- Duplication correctness: shared payloads must preserve value semantics under projection.
- Distributional speed evidence across families, not one cherry-picked case.
- Hidden-seed reproducibility for independent review.

## Failure Matrix

| Failure | What It Catches | Benchmark Family |
|---|---|---|
| Wrong hash | Any semantic drift | All |
| Evaluating erased payload | Garbage/DEL-bit-style mistakes | `del_erasure_trap`, `branch_balance` |
| Dynamic dispatch shortcut | Optimizing for a fixed tag shape | `dynamic_match_storm` |
| Projection/path collapse | Bad graph/path rewrite assumptions | `deep_pair_projection` |
| Duplicate alias drift | Incorrect sharing or copy behavior | `duplication_aliasing` |
| Hot-loop microbenchmark tunnel vision | Speedups that do not generalize | `modular_arithmetic_net` plus all non-loop families |

## Adversarial Scenarios

1. Public-file memorization: regenerate a hidden split with a new seed before accepting a claim.
2. Fast-but-wrong simplification: scorer certifies no speed if any case fails.
3. Dead-code mishandling: erased `bomb` nodes catch eager evaluation.
4. Cherry-pick pressure: report median, p95, total time, and family coverage.
5. Benchmark gaming: the generator can create larger hidden cases without changing semantics.

## Audit and Proof Objects

- Dataset lines contain `expected_sha256`, `reference_steps`, and `reference_max_depth`.
- The generator seed, split, and count reproduce the dataset.
- The scorer recalculates the baseline hash before testing a candidate.
- Certification requires zero failures across the chosen split.
- Hidden-split command:

```bash
python -m fablebreaker.generator --out dataset/hidden_seed_1701.jsonl --count 240 --seed 1701 --split hidden
```

## Evidence Gaps

- This packet does not prove claims about HVM5 itself; it creates a stronger evaluator-optimization audit surface.
- Native Rust/C/Julia candidate adapters would make performance evidence sharper.
- A future version should include memory-profile sampling and per-family confidence intervals.

## Monitor Next

The next gate is to ask candidate AIs to implement an optimized evaluator against the public split,
then score on two hidden seeds. Any model claiming superiority must provide:

- source code,
- command transcript,
- public score,
- hidden score,
- failure list if not certified,
- explanation of optimization law,
- proof that correctness was measured before speed.
