"""
Contamination Engine — detects benchmark data contamination.

Identifies when AI systems have been trained on benchmark data,
rendering their scores meaningless. This is a key capability
that makes Fablebreaker more than a benchmark.
"""

from __future__ import annotations

from typing import Any

from .base import Engine, EngineResult, EngineStatus


class ContaminationEngine(Engine):
    """
    Detects data contamination and benchmark gaming.

    Uses patterns from the knowledge base's gaming_vectors to identify
    when a system's performance is inflated by training data leakage
    rather than genuine capability.
    """

    def __init__(self) -> None:
        super().__init__(
            name="contamination",
            description="Data contamination and benchmark gaming detection engine. "
                        "Identifies inflated scores from training data leakage.",
        )
        self._contamination_signals = [
            "verbatim_reproduction",
            "format_specific_performance_spike",
            "paraphrase_sensitivity",
            "ordering_dependence",
            "novel_vs_known_gap",
            "temporal_performance_cliff",
            "cross_benchmark_inconsistency",
            "statistical_impossibility",
        ]

    def execute(self, context: dict[str, Any]) -> EngineResult:
        """
        Analyze a system for contamination signals.

        Context should contain:
        - benchmark_scores: dict of benchmark_name -> score
        - performance_on_novel: score on never-seen-before data
        - performance_on_known: score on published benchmark data
        - paraphrase_scores: optional performance on paraphrased versions
        - temporal_scores: optional dict of time_period -> score
        """
        benchmark_scores = context.get("benchmark_scores", {})
        novel_score = context.get("performance_on_novel")
        known_score = context.get("performance_on_known")
        paraphrase_scores = context.get("paraphrase_scores", {})

        signals_detected = []
        confidence = 0.0

        # Signal 1: Large gap between known benchmark and novel data
        if novel_score is not None and known_score is not None:
            gap = known_score - novel_score
            if gap > 0.15:
                signals_detected.append({
                    "signal": "novel_vs_known_gap",
                    "severity": "high" if gap > 0.3 else "medium",
                    "evidence": {
                        "known_score": known_score,
                        "novel_score": novel_score,
                        "gap": gap,
                    },
                    "interpretation": "System performs significantly better on published data "
                                      "than on novel data, suggesting memorization.",
                })
                confidence += 0.3

        # Signal 2: Paraphrase sensitivity
        if paraphrase_scores and benchmark_scores:
            for bench_name, original_score in benchmark_scores.items():
                para_score = paraphrase_scores.get(bench_name)
                if para_score is not None:
                    drop = original_score - para_score
                    if drop > 0.1:
                        signals_detected.append({
                            "signal": "paraphrase_sensitivity",
                            "severity": "high" if drop > 0.25 else "medium",
                            "evidence": {
                                "benchmark": bench_name,
                                "original_score": original_score,
                                "paraphrase_score": para_score,
                                "drop": drop,
                            },
                            "interpretation": f"Performance drops {drop:.1%} on paraphrased "
                                              f"version of {bench_name}, suggesting format memorization.",
                        })
                        confidence += 0.2

        # Signal 3: Statistical impossibility
        if benchmark_scores:
            perfect_or_near = sum(
                1 for score in benchmark_scores.values() if score > 0.95
            )
            if perfect_or_near > 3:
                signals_detected.append({
                    "signal": "statistical_impossibility",
                    "severity": "high",
                    "evidence": {
                        "near_perfect_benchmarks": perfect_or_near,
                        "scores": benchmark_scores,
                    },
                    "interpretation": "Near-perfect scores on multiple diverse benchmarks "
                                      "is statistically unlikely without contamination.",
                })
                confidence += 0.25

        # Signal 4: Cross-benchmark inconsistency
        if len(benchmark_scores) >= 4:
            scores = list(benchmark_scores.values())
            score_range = max(scores) - min(scores)
            if score_range > 0.4:
                signals_detected.append({
                    "signal": "cross_benchmark_inconsistency",
                    "severity": "medium",
                    "evidence": {
                        "score_range": score_range,
                        "max_score": max(scores),
                        "min_score": min(scores),
                    },
                    "interpretation": "Large variance across benchmarks of similar difficulty "
                                      "suggests selective contamination.",
                })
                confidence += 0.15

        confidence = min(1.0, confidence)
        contaminated = confidence >= 0.5

        verdict = "contamination_detected" if contaminated else "clean"
        if 0.25 <= confidence < 0.5:
            verdict = "contamination_suspected"

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict=verdict,
            confidence=confidence,
            findings=signals_detected,
            metadata={
                "signals_checked": len(self._contamination_signals),
                "signals_triggered": len(signals_detected),
                "contamination_likelihood": confidence,
                "recommendation": self._recommendation(verdict),
            },
        )

    def _recommendation(self, verdict: str) -> str:
        """Generate a recommendation based on the verdict."""
        if verdict == "contamination_detected":
            return (
                "Strong contamination signals detected. Scores on known benchmarks "
                "should not be trusted. Evaluate exclusively on novel, hidden-seed data."
            )
        if verdict == "contamination_suspected":
            return (
                "Possible contamination. Recommend additional evaluation on "
                "paraphrased and novel datasets before trusting scores."
            )
        return "No strong contamination signals. Scores appear credible pending adversarial evaluation."
