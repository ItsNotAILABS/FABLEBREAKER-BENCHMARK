# Production Packet Policy

All benchmark and certification packets going forward must ship as full production ZIP artifacts.
They must be usable and readable by both humans and AI reviewers.

## Required Free/Public Contents

Every public packet must include:

- `dataset/`
- `candidates/`
- `tools/`
- all required `.py` files
- manifests
- score outputs
- public dataset generator
- scorer and reference evaluator
- all public adversarial families
- baseline candidate
- audit runner
- proof docs and readable audit notes

## Public Release Law

Give away the public trust layer for free:

- public dataset generator
- scorer and reference evaluator
- adversarial families
- baseline candidate
- audit runner
- manifests
- proof docs
- zero-dependency local execution path where feasible

The free packet should be strong enough for independent builders, AI reviewers, and open-source
communities to inspect, run, reproduce, and challenge.

## Paid Tier Boundary

Keep these for paid or deeper private certification later:

- rotating hidden seeds
- hosted leaderboard
- private custom suites
- signed evidence packs
- CI integration
- larger hidden corpora
- memory/allocation profiles
- enterprise benchmark design

## Reality Check Baseline

The FableBreaker packet is the current template:

- deterministic generator,
- semantic hashes,
- erasure traps,
- hidden split,
- self-audit passing 480/480 cases,
- Python-only zero-dependency design,
- direct response to audit caveats in evaluator-optimization hype.

Future packets should preserve this strength or explicitly explain why a deviation is necessary.
