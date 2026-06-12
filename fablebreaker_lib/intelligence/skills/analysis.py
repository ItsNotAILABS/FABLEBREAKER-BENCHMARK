"""
Analysis Skill — deep analysis of AI systems and claims.
"""

from __future__ import annotations

from typing import Any

from .base import Skill, SkillLevel, SkillResult


class AnalysisSkill(Skill):
    """
    Deep analysis of AI systems, benchmarks, and performance claims.

    Can dissect claims, identify weaknesses in evaluation methodology,
    and produce structured analytical reports.
    """

    def __init__(self) -> None:
        super().__init__(
            name="analysis",
            description="Deep analysis of AI systems, claims, and evaluation methodologies. "
                        "Produces structured reports identifying strengths and weaknesses.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform analysis.

        Context should contain:
        - target: what to analyze (claim, benchmark, system, methodology)
        - data: supporting data for analysis
        - depth: shallow, standard, or deep
        """
        target = context.get("target", {})
        depth = context.get("depth", "standard")

        if not target:
            return SkillResult(
                skill_name=self.name,
                success=False,
                reasoning="No analysis target provided",
            )

        analysis_type = target.get("type", "general")

        if analysis_type == "claim":
            return self._analyze_claim(target, depth)
        if analysis_type == "benchmark":
            return self._analyze_benchmark(target, depth)
        if analysis_type == "system":
            return self._analyze_system(target, depth)
        return self._general_analysis(target, depth)

    def _analyze_claim(self, target: dict[str, Any], depth: str) -> SkillResult:
        """Analyze a performance claim."""
        claim_text = target.get("text", "")
        evidence = target.get("evidence", {})
        methodology = target.get("methodology", "")  # noqa: F841 - reserved for deep analysis

        issues = []
        strengths = []

        # Check for reproducibility
        if not evidence.get("reproducible"):
            issues.append({
                "category": "reproducibility",
                "severity": "high",
                "finding": "No reproducibility evidence provided",
            })
        else:
            strengths.append("Reproducibility evidence present")

        # Check for adversarial testing
        if not evidence.get("adversarial_tested"):
            issues.append({
                "category": "adversarial_coverage",
                "severity": "high",
                "finding": "No adversarial evaluation performed",
            })
        else:
            strengths.append("Adversarial testing performed")

        # Check for correctness verification
        if not evidence.get("correctness_verified"):
            issues.append({
                "category": "correctness",
                "severity": "critical",
                "finding": "No correctness verification — speed claim without semantic proof",
            })
        else:
            strengths.append("Correctness verification present")

        # Check for hidden evaluation
        if not evidence.get("hidden_eval"):
            issues.append({
                "category": "contamination",
                "severity": "medium",
                "finding": "No hidden/unseen evaluation data used",
            })

        credibility = max(0.0, 1.0 - len(issues) * 0.2)

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "claim": claim_text,
                "credibility_score": credibility,
                "issues": issues,
                "strengths": strengths,
                "recommendation": (
                    "Claim is credible" if credibility >= 0.8
                    else "Claim requires additional evidence" if credibility >= 0.5
                    else "Claim should not be trusted without further validation"
                ),
            },
            confidence=credibility,
            reasoning=f"Analyzed claim with {len(issues)} issues and {len(strengths)} strengths found",
        )

    def _analyze_benchmark(self, target: dict[str, Any], depth: str) -> SkillResult:
        """Analyze a benchmark's design and validity."""
        benchmark_data = target.get("data", {})

        dimensions = {
            "correctness_enforcement": self._score_correctness(benchmark_data),
            "contamination_resistance": self._score_contamination_resistance(benchmark_data),
            "adversarial_coverage": self._score_adversarial(benchmark_data),
            "reproducibility": self._score_reproducibility(benchmark_data),
            "scale_adequacy": self._score_scale(benchmark_data),
        }

        overall = sum(dimensions.values()) / len(dimensions) if dimensions else 0.0

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "benchmark_name": benchmark_data.get("name", "unknown"),
                "dimension_scores": dimensions,
                "overall_validity": overall,
                "weakest_dimension": min(dimensions, key=dimensions.get) if dimensions else None,
                "strongest_dimension": max(dimensions, key=dimensions.get) if dimensions else None,
            },
            confidence=overall,
            reasoning=f"Benchmark validity assessment: {overall:.2f}",
        )

    def _analyze_system(self, target: dict[str, Any], depth: str) -> SkillResult:
        """Analyze an AI system's evaluation landscape."""
        return SkillResult(
            skill_name=self.name,
            success=True,
            output={"analysis_type": "system", "depth": depth, "target": target},
            confidence=0.7,
            reasoning="System analysis performed",
        )

    def _general_analysis(self, target: dict[str, Any], depth: str) -> SkillResult:
        """General-purpose analysis."""
        return SkillResult(
            skill_name=self.name,
            success=True,
            output={"analysis_type": "general", "depth": depth, "target": target},
            confidence=0.6,
            reasoning="General analysis performed",
        )

    def _score_correctness(self, data: dict[str, Any]) -> float:
        reqs = data.get("correctness_requirements", [])
        if not reqs:
            return 0.2
        has_hash = any("hash" in r.lower() for r in reqs)
        return 0.9 if has_hash else 0.6

    def _score_contamination_resistance(self, data: dict[str, Any]) -> float:
        tags = data.get("tags", [])
        if "contamination_resistant" in tags:
            return 0.9
        if "contaminated" in tags or "contamination_risk" in tags:
            return 0.2
        return 0.5

    def _score_adversarial(self, data: dict[str, Any]) -> float:
        tags = data.get("tags", [])
        if "adversarial" in tags:
            return 0.8
        return 0.4

    def _score_reproducibility(self, data: dict[str, Any]) -> float:
        if data.get("url"):
            return 0.7
        return 0.4

    def _score_scale(self, data: dict[str, Any]) -> float:
        scale = data.get("scale", "")
        if "1000" in scale or "10,000" in scale or "100,000" in scale:
            return 0.8
        if "100" in scale or "500" in scale:
            return 0.5
        return 0.3
