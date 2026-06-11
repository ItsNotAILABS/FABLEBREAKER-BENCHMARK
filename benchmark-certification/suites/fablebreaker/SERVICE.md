# FableBreaker Service Contract

## Purpose

FableBreaker can run as a local certification service for evaluator-optimization claims.
The service does not execute arbitrary uploaded code. Candidates must already exist as importable
Python modules inside the suite runtime or environment.

## Endpoints

### `GET /health`

Returns service status.

### `GET /manifest`

Returns benchmark suite metadata.

### `POST /generate`

Generates a deterministic dataset.

Example:

```bash
curl -X POST http://127.0.0.1:8787/generate \
  -H 'content-type: application/json' \
  -d '{"seed":1701,"count":240,"split":"hidden","out":"dataset/hidden_seed_1701.jsonl"}'
```

### `GET /score?dataset=dataset/public.jsonl&candidate=candidates.baseline_candidate`

Scores an importable candidate module.

## Security Boundary

This is a local development service. Public hosted scoring should run candidates in isolated
containers or accept only repository submissions that are evaluated by CI.

## Commercial Boundary

The public service can expose manifests, public datasets, reproducible scores, and candidate
submission rules. Private certification can rotate hidden seeds, larger corpora, per-family reports,
memory profiles, and signed evidence packs.
