from __future__ import annotations

import argparse
import importlib
import json
import statistics
import time
from pathlib import Path
from typing import Any

from .astlang import canonical, digest, evaluate


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
    return ordered[index]


def score(dataset: Path, candidate_module: str, repeat: int) -> dict[str, Any]:
    candidate = importlib.import_module(candidate_module)
    if not hasattr(candidate, "evaluate"):
        raise SystemExit(f"{candidate_module} must expose evaluate(expr: dict) -> object")

    cases = load_cases(dataset)
    candidate_times: list[float] = []
    baseline_times: list[float] = []
    failures: list[dict[str, Any]] = []

    for case in cases:
        expr = case["expr"]
        expected = case["expected_sha256"]

        base_start = time.perf_counter()
        for _ in range(repeat):
            baseline_value, _ = evaluate(expr)
        base_elapsed = (time.perf_counter() - base_start) / repeat
        baseline_times.append(base_elapsed)
        if digest(baseline_value) != expected:
            raise AssertionError(f"dataset reference mismatch: {case['id']}")

        start = time.perf_counter()
        try:
            for _ in range(repeat):
                result = candidate.evaluate(expr)
            elapsed = (time.perf_counter() - start) / repeat
            result_hash = digest(canonical(result))
            if result_hash != expected:
                failures.append({"id": case["id"], "reason": "wrong_hash", "got": result_hash, "expected": expected})
            candidate_times.append(elapsed)
        except Exception as exc:  # noqa: BLE001 - benchmark harness must capture candidate failures.
            elapsed = (time.perf_counter() - start) / repeat
            candidate_times.append(elapsed)
            failures.append({"id": case["id"], "reason": type(exc).__name__, "message": str(exc)})

    total_baseline = sum(baseline_times)
    total_candidate = sum(candidate_times)
    correct = len(cases) - len(failures)
    speedup = total_baseline / total_candidate if total_candidate > 0 else 0.0
    certified = not failures

    return {
        "dataset": str(dataset),
        "candidate": candidate_module,
        "cases": len(cases),
        "correct": correct,
        "failed": len(failures),
        "certified": certified,
        "speedup_vs_reference": speedup if certified else 0.0,
        "baseline_total_seconds": total_baseline,
        "candidate_total_seconds": total_candidate,
        "candidate_median_ms": statistics.median(candidate_times) * 1000 if candidate_times else 0,
        "candidate_p95_ms": percentile(candidate_times, 0.95) * 1000,
        "baseline_median_ms": statistics.median(baseline_times) * 1000 if baseline_times else 0,
        "baseline_p95_ms": percentile(baseline_times, 0.95) * 1000,
        "failures": failures[:25],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--json-out")
    args = parser.parse_args()

    result = score(Path(args.dataset), args.candidate, max(1, args.repeat))
    payload = json.dumps(result, indent=2, sort_keys=True)
    print(payload)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
