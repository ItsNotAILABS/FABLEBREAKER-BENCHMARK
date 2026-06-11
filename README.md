# FABLEBREAKER-BENCHMARK
 benchmark where speedup claims don’t count unless correctness survives hidden adversarial cases.

Benchmark Certification
Benchmark Certification is the repo surface for hard-to-game benchmark suites, hidden corpora, reproducibility artifacts, score evidence, and counter-hype validation systems.

Active Suites
suites/fablebreaker - reproducible evaluator-optimization benchmark for semantic-preserving rewrite/runtime claims.
Service Surfaces
services/fablebreaker_service.py - local HTTP service for generating datasets, scoring candidates, and reading suite manifests.
Quick Start
cd /workspace/benchmark-certification/suites/fablebreaker
python tools/run_full_audit.py --candidate candidates.baseline_candidate
Run as a local service:

cd /workspace/benchmark-certification
python services/fablebreaker_service.py --host 127.0.0.1 --port 8787
Then check:

curl http://127.0.0.1:8787/health
curl http://127.0.0.1:8787/manifest
Repo Role
This repo owns certification evidence, not sovereign backend authority. Future score submissions, signed manifests, and hidden-seed release logs can be mirrored into nexus-registry or backed by motoko-core once public score custody becomes important.

Product Law
Speed claims only count after correctness. Correctness only counts when the dataset, generator, hashes, scorer, and hidden-seed protocol can be inspected.
