"""Per-Family Scoring and Statistical Confidence Protocol SDK.

Implements the methodology from:
    "Per-Family Scoring and Statistical Confidence in Multi-Family
     Benchmark Architectures"
    Journal of Benchmark Architecture · Volume 1 · 2026

This module provides a programmatic interface for computing per-family
scoring breakdowns, confidence intervals, and statistical significance
as described in the paper.

Foundation: https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FamilyScore:
    """Scoring result for a single adversarial family.

    All timing values are in seconds unless otherwise noted.
    """

    family: str
    case_count: int
    correct_count: int
    pass_rate: float
    speedup: float
    candidate_median_ms: float
    candidate_p95_ms: float
    candidate_p99_ms: float
    ci_95_lower_ms: float
    ci_95_upper_ms: float
    statistically_significant: bool
    min_sample_met: bool


@dataclass
class ScoringReport:
    """Complete per-family scoring report."""

    families: list[FamilyScore]
    aggregate_speedup: float
    aggregate_correct: int
    aggregate_total: int
    certified: bool

    @property
    def family_names(self) -> list[str]:
        """Return sorted list of scored families."""
        return sorted(f.family for f in self.families)

    def get_family(self, name: str) -> FamilyScore | None:
        """Return the score for a specific family."""
        for f in self.families:
            if f.family == name:
                return f
        return None

    def failing_families(self) -> list[FamilyScore]:
        """Return families with pass_rate < 1.0."""
        return [f for f in self.families if f.pass_rate < 1.0]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary matching the scorer output schema."""
        breakdown = {}
        for f in self.families:
            breakdown[f.family] = {
                "count": f.case_count,
                "correct": f.correct_count,
                "pass_rate": f.pass_rate,
                "speedup": f.speedup,
                "candidate_median_ms": f.candidate_median_ms,
                "candidate_p95_ms": f.candidate_p95_ms,
                "candidate_p99_ms": f.candidate_p99_ms,
                "ci_95_ms": [f.ci_95_lower_ms, f.ci_95_upper_ms],
                "statistically_significant": f.statistically_significant,
                "min_sample_met": f.min_sample_met,
            }
        return {
            "family_breakdown": breakdown,
            "aggregate_speedup": self.aggregate_speedup,
            "aggregate_correct": self.aggregate_correct,
            "aggregate_total": self.aggregate_total,
            "certified": self.certified,
        }


# Minimum recommended cases per family for reliable inference (Section 2.2)
MIN_SAMPLE_SIZE = 20


class PerFamilyScoringProtocol:
    """SDK for the Per-Family Scoring protocol.

    Computes per-family scoring breakdowns with confidence intervals,
    determines statistical significance of speedup measurements, and
    provides diagnostic information for targeted optimization.

    Usage:
        protocol = PerFamilyScoringProtocol()

        # Compute from raw timing data
        report = protocol.compute(
            cases=cases,
            candidate_times=candidate_times,
            baseline_times=baseline_times,
            failures=failures,
        )

        # Analyze results
        for family in report.failing_families():
            print(f"{family.family}: {family.pass_rate:.0%} pass rate")

        # Check confidence intervals
        score = report.get_family("overflow_corridor")
        if score and not score.statistically_significant:
            print("Speedup not statistically significant - need more samples")
    """

    PAPER_TITLE = "Per-Family Scoring and Statistical Confidence in Multi-Family Benchmark Architectures"
    JOURNAL = "Journal of Benchmark Architecture"
    DOI_FOUNDATION = "10.5281/zenodo.20589250"
    MIN_SAMPLE_SIZE = MIN_SAMPLE_SIZE

    def compute(
        self,
        cases: list[dict[str, Any]],
        candidate_times: list[float],
        baseline_times: list[float],
        failures: list[dict[str, Any]],
    ) -> ScoringReport:
        """Compute per-family scoring breakdown.

        Args:
            cases: List of benchmark case dictionaries (must have 'id' and 'family').
            candidate_times: Timing measurements for the candidate (seconds).
            baseline_times: Timing measurements for the baseline (seconds).
            failures: List of failure records with 'id' field.

        Returns:
            ScoringReport with per-family breakdown and aggregate statistics.
        """
        failure_ids = {f["id"] for f in failures}
        family_data: dict[str, dict[str, Any]] = {}

        for i, case in enumerate(cases):
            family = case.get("family", "unknown")
            if family not in family_data:
                family_data[family] = {
                    "count": 0,
                    "correct": 0,
                    "candidate_times": [],
                    "baseline_times": [],
                }
            fd = family_data[family]
            fd["count"] += 1
            if case["id"] not in failure_ids:
                fd["correct"] += 1
            if i < len(candidate_times):
                fd["candidate_times"].append(candidate_times[i])
            if i < len(baseline_times):
                fd["baseline_times"].append(baseline_times[i])

        family_scores = []
        for family in sorted(family_data.keys()):
            fd = family_data[family]
            ct = fd["candidate_times"]
            bt = fd["baseline_times"]
            total_bt = sum(bt)
            total_ct = sum(ct)
            pass_rate = fd["correct"] / fd["count"] if fd["count"] > 0 else 0.0
            speedup = total_bt / total_ct if total_ct > 0 and pass_rate == 1.0 else 0.0
            ci_low, ci_high = self.confidence_interval_95(ct)
            bl_ci_low, bl_ci_high = self.confidence_interval_95(bt)

            # Statistical significance: CI of candidate and baseline don't overlap
            significant = self._is_significant(ci_low, ci_high, bl_ci_low, bl_ci_high)

            family_scores.append(FamilyScore(
                family=family,
                case_count=fd["count"],
                correct_count=fd["correct"],
                pass_rate=pass_rate,
                speedup=speedup,
                candidate_median_ms=statistics.median(ct) * 1000 if ct else 0.0,
                candidate_p95_ms=self._percentile(ct, 0.95) * 1000,
                candidate_p99_ms=self._percentile(ct, 0.99) * 1000,
                ci_95_lower_ms=ci_low * 1000,
                ci_95_upper_ms=ci_high * 1000,
                statistically_significant=significant,
                min_sample_met=fd["count"] >= MIN_SAMPLE_SIZE,
            ))

        total_correct = sum(f.correct_count for f in family_scores)
        total_cases = sum(f.case_count for f in family_scores)
        total_bt = sum(baseline_times)
        total_ct = sum(candidate_times)
        certified = len(failures) == 0
        aggregate_speedup = total_bt / total_ct if total_ct > 0 and certified else 0.0

        return ScoringReport(
            families=family_scores,
            aggregate_speedup=aggregate_speedup,
            aggregate_correct=total_correct,
            aggregate_total=total_cases,
            certified=certified,
        )

    @staticmethod
    def confidence_interval_95(values: list[float]) -> tuple[float, float]:
        """Compute 95% confidence interval for the mean using t-approximation.

        Section 2.2: CI = x̄ ± t_{0.025,n-1} · s/√n
        """
        if len(values) < 2:
            return (0.0, 0.0)
        mean = statistics.mean(values)
        stderr = statistics.stdev(values) / math.sqrt(len(values))
        margin = 1.96 * stderr
        return (mean - margin, mean + margin)

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        """Compute a percentile from a list of values."""
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
        return ordered[index]

    @staticmethod
    def _is_significant(
        ci_low_a: float, ci_high_a: float,
        ci_low_b: float, ci_high_b: float,
    ) -> bool:
        """Determine if two confidence intervals don't overlap (Section 2.3)."""
        if ci_low_a == 0.0 and ci_high_a == 0.0:
            return False
        if ci_low_b == 0.0 and ci_high_b == 0.0:
            return False
        return ci_high_a < ci_low_b or ci_high_b < ci_low_a

    def minimum_sample_recommendation(self, current_count: int) -> dict[str, Any]:
        """Provide sample size recommendation for a family.

        Based on Section 2.2: minimum 20 cases per family for reliable inference.
        """
        return {
            "current_count": current_count,
            "minimum_recommended": MIN_SAMPLE_SIZE,
            "sufficient": current_count >= MIN_SAMPLE_SIZE,
            "additional_needed": max(0, MIN_SAMPLE_SIZE - current_count),
        }
