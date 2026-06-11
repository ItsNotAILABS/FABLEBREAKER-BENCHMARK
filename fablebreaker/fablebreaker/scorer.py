from __future__ import annotations

import argparse
import importlib
import json
import statistics
import time
from collections import defaultdict
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


def _family_diagnostics(
    family_results: dict[str, dict[str, list]],
) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    for family, data in sorted(family_results.items()):
        ct = data["candidate_times"]
        bt = data["baseline_times"]
        total_cases = len(ct)
        failed = len(data["failures"])
        correct = total_cases - failed
        total_baseline = sum(bt)
        total_candidate = sum(ct)
        family_certified = failed == 0
        speedup = total_baseline / total_candidate if total_candidate > 0 and family_certified else 0.0
        diagnostics[family] = {
            "cases": total_cases,
            "correct": correct,
            "failed": failed,
            "certified": family_certified,
            "speedup_vs_reference": speedup,
            "candidate_median_ms": statistics.median(ct) * 1000 if ct else 0,
            "candidate_p95_ms": percentile(ct, 0.95) * 1000,
            "baseline_median_ms": statistics.median(bt) * 1000 if bt else 0,
            "baseline_p95_ms": percentile(bt, 0.95) * 1000,
            "failures": data["failures"][:5],
        }
    return diagnostics


def score(dataset: Path, candidate_module: str, repeat: int) -> dict[str, Any]:
    candidate = importlib.import_module(candidate_module)
    if not hasattr(candidate, "evaluate"):
        raise SystemExit(f"{candidate_module} must expose evaluate(expr: dict) -> object")

    cases = load_cases(dataset)
    candidate_times: list[float] = []
    baseline_times: list[float] = []
    failures: list[dict[str, Any]] = []

    family_results: dict[str, dict[str, list]] = defaultdict(
        lambda: {"candidate_times": [], "baseline_times": [], "failures": []}
    )

    for case in cases:
        expr = case["expr"]
        expected = case["expected_sha256"]
        family = case.get("family", "unknown")

        base_start = time.perf_counter()
        for _ in range(repeat):
            baseline_value, _ = evaluate(expr)
        base_elapsed = (time.perf_counter() - base_start) / repeat
        baseline_times.append(base_elapsed)
        family_results[family]["baseline_times"].append(base_elapsed)
        if digest(baseline_value) != expected:
            raise AssertionError(f"dataset reference mismatch: {case['id']}")

        start = time.perf_counter()
        try:
            for _ in range(repeat):
                result = candidate.evaluate(expr)
            elapsed = (time.perf_counter() - start) / repeat
            result_hash = digest(canonical(result))
            if result_hash != expected:
                failure = {"id": case["id"], "reason": "wrong_hash", "got": result_hash, "expected": expected}
                failures.append(failure)
                family_results[family]["failures"].append(failure)
            candidate_times.append(elapsed)
            family_results[family]["candidate_times"].append(elapsed)
        except Exception as exc:  # noqa: BLE001 - benchmark harness must capture candidate failures.
            elapsed = (time.perf_counter() - start) / repeat
            candidate_times.append(elapsed)
            family_results[family]["candidate_times"].append(elapsed)
            failure = {"id": case["id"], "reason": type(exc).__name__, "message": str(exc)}
            failures.append(failure)
            family_results[family]["failures"].append(failure)

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
        "family_diagnostics": _family_diagnostics(family_results),
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
