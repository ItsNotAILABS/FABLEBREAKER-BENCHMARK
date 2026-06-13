"""
Meta-Evaluation Engine — evaluates benchmarks themselves.

This is what makes Fablebreaker transcend being a benchmark.
It evaluates the evaluators, scores the scorers, and identifies
weaknesses in the benchmark ecosystem itself.
"""

from __future__ import annotations

from typing import Any

from .base import Engine, EngineResult, EngineStatus


class MetaEvaluationEngine(Engine):
    """
    Evaluates benchmarks themselves — the benchmark of benchmarks.

    This engine uses the knowledge base to analyze whether a benchmark
    is trustworthy, gameable, contaminated, or obsolete.
    """

    def __init__(self) -> None:
        super().__init__(
            name="meta_evaluation",
            description="Evaluates benchmarks themselves. Determines trustworthiness, "
                        "gameability, and validity of evaluation instruments.",
        )

    def execute(self, context: dict[str, Any]) -> EngineResult:
        """
        Evaluate a benchmark's trustworthiness.

        Context should contain:
        - benchmark: dict from the knowledge base
        - or benchmark_name: name to look up
        - saturation_threshold: optional (default 0.95)
        """
        benchmark = context.get("benchmark", {})
        if not benchmark:
            return EngineResult(
                engine_name=self.name,
                status=EngineStatus.COMPLETE,
                verdict="no_benchmark_provided",
                confidence=0.0,
            )

        findings = []
        trust_score = 1.0

        # Check gaming vectors
        gaming_vectors = benchmark.get("gaming_vectors", [])
        if gaming_vectors:
            severity = len(gaming_vectors) / 5.0
            trust_score -= min(0.3, severity * 0.1)
            findings.append({
                "dimension": "gameability",
                "score": 1.0 - min(1.0, severity * 0.2),
                "vectors": gaming_vectors,
                "assessment": f"{len(gaming_vectors)} known gaming vectors identified",
            })

        # Check limitations
        limitations = benchmark.get("limitations", [])
        if limitations:
            trust_score -= min(0.2, len(limitations) * 0.05)
            findings.append({
                "dimension": "completeness",
                "score": max(0.0, 1.0 - len(limitations) * 0.1),
                "limitations": limitations,
                "assessment": f"{len(limitations)} known limitations",
            })

        # Check correctness requirements
        correctness_reqs = benchmark.get("correctness_requirements", [])
        if not correctness_reqs:
            trust_score -= 0.3
            findings.append({
                "dimension": "correctness_enforcement",
                "score": 0.0,
                "assessment": "No formal correctness requirements specified",
            })
        else:
            has_hash = any("hash" in r.lower() or "exact" in r.lower() for r in correctness_reqs)
            has_verification = any("verif" in r.lower() or "proof" in r.lower() for r in correctness_reqs)
            enforcement_score = 0.5
            if has_hash:
                enforcement_score += 0.25
            if has_verification:
                enforcement_score += 0.25
            findings.append({
                "dimension": "correctness_enforcement",
                "score": enforcement_score,
                "requirements": correctness_reqs,
                "has_hash_verification": has_hash,
                "has_formal_verification": has_verification,
            })

        # Check age (older benchmarks more likely contaminated)
        year = benchmark.get("year", 2024)
        age = 2025 - year
        if age >= 4:
            trust_score -= min(0.2, age * 0.03)
            findings.append({
                "dimension": "contamination_risk",
                "score": max(0.0, 1.0 - age * 0.1),
                "age_years": age,
                "assessment": f"Benchmark is {age} years old — higher contamination risk",
            })

        # Check tags for known issues
        tags = benchmark.get("tags", [])
        if "contaminated" in tags or "contamination_risk" in tags:
            trust_score -= 0.25
            findings.append({
                "dimension": "known_contamination",
                "score": 0.2,
                "assessment": "Benchmark has known contamination issues",
            })

        if "saturated" in tags or "saturated_for_frontier" in tags:
            trust_score -= 0.15
            findings.append({
                "dimension": "saturation",
                "score": 0.3,
                "assessment": "Benchmark is saturated — no longer discriminative for frontier models",
            })

        trust_score = max(0.0, min(1.0, trust_score))

        if trust_score >= 0.8:
            verdict = "trustworthy"
        elif trust_score >= 0.5:
            verdict = "use_with_caution"
        else:
            verdict = "unreliable"

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict=verdict,
            confidence=trust_score,
            findings=findings,
            metadata={
                "benchmark_name": benchmark.get("name", "unknown"),
                "trust_score": trust_score,
                "dimensions_evaluated": len(findings),
                "recommendation": self._recommendation(verdict, trust_score),
            },
        )

    def _recommendation(self, verdict: str, score: float) -> str:
        """Generate recommendation based on meta-evaluation."""
        if verdict == "trustworthy":
            return "Benchmark scores from this instrument can be cited with confidence."
        if verdict == "use_with_caution":
            return (
                f"Trust score {score:.2f}. Use benchmark results as one signal among many. "
                "Cross-validate with adversarial evaluation and novel data."
            )
        return (
            f"Trust score {score:.2f}. Benchmark scores should NOT be used as primary evidence. "
            "High contamination risk and/or insufficient correctness enforcement."
        )
