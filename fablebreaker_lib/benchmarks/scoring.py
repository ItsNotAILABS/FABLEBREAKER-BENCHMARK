"""
Scoring engine for benchmark evaluation.
"""

from __future__ import annotations

import importlib
import statistics
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FamilyDiagnostics:
    """Diagnostics for a single adversarial family."""
    family: str
    cases: int = 0
    correct: int = 0
    failed: int = 0
    certified: bool = False
    speedup: float = 0.0
    candidate_median_ms: float = 0.0
    candidate_p95_ms: float = 0.0
    baseline_median_ms: float = 0.0
    baseline_p95_ms: float = 0.0
    failures: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "cases": self.cases,
            "correct": self.correct,
            "failed": self.failed,
            "certified": self.certified,
            "speedup": self.speedup,
            "candidate_median_ms": self.candidate_median_ms,
            "candidate_p95_ms": self.candidate_p95_ms,
            "baseline_median_ms": self.baseline_median_ms,
            "baseline_p95_ms": self.baseline_p95_ms,
            "failures": self.failures[:5],
        }


@dataclass
class ScoreResult:
    """Complete scoring result for a candidate."""
    dataset: str
    candidate: str
    cases: int = 0
    correct: int = 0
    failed: int = 0
    certified: bool = False
    speedup_vs_reference: float = 0.0
    baseline_total_seconds: float = 0.0
    candidate_total_seconds: float = 0.0
    candidate_median_ms: float = 0.0
    candidate_p95_ms: float = 0.0
    baseline_median_ms: float = 0.0
    baseline_p95_ms: float = 0.0
    family_diagnostics: dict[str, FamilyDiagnostics] = field(default_factory=dict)
    failures: list[dict[str, Any]] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.correct / self.cases if self.cases > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "candidate": self.candidate,
            "cases": self.cases,
            "correct": self.correct,
            "failed": self.failed,
            "certified": self.certified,
            "speedup_vs_reference": self.speedup_vs_reference,
            "pass_rate": self.pass_rate,
            "baseline_total_seconds": self.baseline_total_seconds,
            "candidate_total_seconds": self.candidate_total_seconds,
            "candidate_median_ms": self.candidate_median_ms,
            "candidate_p95_ms": self.candidate_p95_ms,
            "baseline_median_ms": self.baseline_median_ms,
            "baseline_p95_ms": self.baseline_p95_ms,
            "family_diagnostics": {
                k: v.to_dict() for k, v in self.family_diagnostics.items()
            },
            "failures": self.failures[:25],
        }


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
    return ordered[index]


class ScoreEngine:
    """Engine for scoring candidates against a benchmark dataset."""

    def __init__(self, reference_evaluator: Any = None) -> None:
        self._reference = reference_evaluator

    def load_candidate(self, module_path: str) -> Any:
        """Dynamically load a candidate module."""
        module = importlib.import_module(module_path)
        if not hasattr(module, "evaluate"):
            raise ValueError(f"{module_path} must expose evaluate(expr: dict) -> object")
        return module

    def score_candidate(
        self,
        candidate_module: str,
        cases: list[dict[str, Any]],
        repeat: int = 1,
        reference_fn: Any = None,
        hash_fn: Any = None,
        canonical_fn: Any = None,
    ) -> ScoreResult:
        """Score a candidate against evaluation cases.

        This is the core scoring loop that measures both correctness and performance.
        """
        candidate = self.load_candidate(candidate_module)
        candidate_times: list[float] = []
        baseline_times: list[float] = []
        failures: list[dict[str, Any]] = []

        for case in cases:
            expr = case["expr"]
            expected = case["expected_sha256"]

            # Baseline timing
            if reference_fn:
                base_start = time.perf_counter()
                for _ in range(repeat):
                    reference_fn(expr)
                base_elapsed = (time.perf_counter() - base_start) / repeat
                baseline_times.append(base_elapsed)

            # Candidate timing
            start = time.perf_counter()
            try:
                for _ in range(repeat):
                    result = candidate.evaluate(expr)
                elapsed = (time.perf_counter() - start) / repeat

                if hash_fn and canonical_fn:
                    result_hash = hash_fn(canonical_fn(result))
                    if result_hash != expected:
                        failures.append({
                            "id": case.get("id", "unknown"),
                            "reason": "wrong_hash",
                        })

                candidate_times.append(elapsed)
            except Exception as exc:
                elapsed = (time.perf_counter() - start) / repeat
                candidate_times.append(elapsed)
                failures.append({
                    "id": case.get("id", "unknown"),
                    "reason": type(exc).__name__,
                    "message": str(exc),
                })

        total_baseline = sum(baseline_times)
        total_candidate = sum(candidate_times)
        correct = len(cases) - len(failures)
        certified = not failures
        speedup = total_baseline / total_candidate if total_candidate > 0 and certified else 0.0

        return ScoreResult(
            dataset="dynamic",
            candidate=candidate_module,
            cases=len(cases),
            correct=correct,
            failed=len(failures),
            certified=certified,
            speedup_vs_reference=speedup,
            baseline_total_seconds=total_baseline,
            candidate_total_seconds=total_candidate,
            candidate_median_ms=statistics.median(candidate_times) * 1000 if candidate_times else 0,
            candidate_p95_ms=_percentile(candidate_times, 0.95) * 1000,
            baseline_median_ms=statistics.median(baseline_times) * 1000 if baseline_times else 0,
            baseline_p95_ms=_percentile(baseline_times, 0.95) * 1000,
            failures=failures,
        )
