"""
Detection Skill — identifies gaming, contamination, and manipulation.
"""

from __future__ import annotations

from typing import Any

from .base import Skill, SkillLevel, SkillResult


class DetectionSkill(Skill):
    """
    Detects gaming, contamination, manipulation, and fraud in AI evaluations.

    This skill gives Fablebreaker the ability to catch cheaters,
    identify inflated claims, and expose benchmark theater.
    """

    def __init__(self) -> None:
        super().__init__(
            name="detection",
            description="Detects gaming, contamination, manipulation, and fraud "
                        "in AI evaluations and performance claims.",
            level=SkillLevel.MASTER,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Detect gaming or manipulation.

        Context should contain:
        - detection_type: "contamination", "gaming", "manipulation", "fraud"
        - evidence: supporting evidence to analyze
        - scores: benchmark scores to check
        """
        detection_type = context.get("detection_type", "gaming")
        evidence = context.get("evidence", {})
        scores = context.get("scores", {})

        if detection_type == "contamination":
            return self._detect_contamination(scores, evidence)
        if detection_type == "gaming":
            return self._detect_gaming(scores, evidence)
        if detection_type == "manipulation":
            return self._detect_manipulation(evidence)
        if detection_type == "fraud":
            return self._detect_fraud(scores, evidence)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown detection type: {detection_type}",
        )

    def _detect_contamination(
        self, scores: dict[str, Any], evidence: dict[str, Any]
    ) -> SkillResult:
        """Detect data contamination."""
        red_flags = []

        # Check for suspicious score patterns
        if scores:
            high_scores = [k for k, v in scores.items() if isinstance(v, (int, float)) and v > 0.95]
            if len(high_scores) >= 3:
                red_flags.append({
                    "indicator": "multiple_near_perfect_scores",
                    "severity": "high",
                    "benchmarks": high_scores,
                })

        # Check for known-vs-novel gap
        known = evidence.get("known_benchmark_score")
        novel = evidence.get("novel_data_score")
        if known is not None and novel is not None and known - novel > 0.15:
            red_flags.append({
                "indicator": "known_novel_gap",
                "severity": "high",
                "gap": known - novel,
            })

        # Check for format sensitivity
        original = evidence.get("original_format_score")
        reformatted = evidence.get("reformatted_score")
        if original is not None and reformatted is not None and original - reformatted > 0.1:
            red_flags.append({
                "indicator": "format_sensitivity",
                "severity": "medium",
                "drop": original - reformatted,
            })

        contaminated = len(red_flags) >= 2

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "contamination_detected": contaminated,
                "red_flags": red_flags,
                "confidence": min(1.0, len(red_flags) * 0.3),
            },
            confidence=min(1.0, len(red_flags) * 0.3),
            reasoning=f"Found {len(red_flags)} contamination indicators",
        )

    def _detect_gaming(
        self, scores: dict[str, Any], evidence: dict[str, Any]
    ) -> SkillResult:
        """Detect benchmark gaming strategies."""
        gaming_indicators = []

        # Check for cherry-picking
        if evidence.get("selected_benchmarks") and evidence.get("omitted_benchmarks"):
            selected = evidence["selected_benchmarks"]
            omitted = evidence["omitted_benchmarks"]
            if len(omitted) > len(selected):
                gaming_indicators.append({
                    "strategy": "cherry_picking",
                    "severity": "high",
                    "evidence": f"Showing {len(selected)} benchmarks, hiding {len(omitted)}",
                })

        # Check for metric gaming
        if evidence.get("metric_choice_suspicious"):
            gaming_indicators.append({
                "strategy": "metric_selection",
                "severity": "medium",
                "evidence": "Non-standard or favorable metric chosen",
            })

        # Check for dataset version gaming
        if evidence.get("uses_outdated_baseline"):
            gaming_indicators.append({
                "strategy": "weak_baseline",
                "severity": "medium",
                "evidence": "Comparison against outdated or weak baseline",
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "gaming_detected": len(gaming_indicators) > 0,
                "strategies_identified": gaming_indicators,
            },
            confidence=min(1.0, len(gaming_indicators) * 0.35),
            reasoning=f"Identified {len(gaming_indicators)} gaming strategies",
        )

    def _detect_manipulation(self, evidence: dict[str, Any]) -> SkillResult:
        """Detect result manipulation."""
        manipulation_signals = []

        if evidence.get("results_not_reproducible"):
            manipulation_signals.append({
                "signal": "irreproducibility",
                "severity": "critical",
            })

        if evidence.get("selective_reporting"):
            manipulation_signals.append({
                "signal": "selective_reporting",
                "severity": "high",
            })

        if evidence.get("post_hoc_filtering"):
            manipulation_signals.append({
                "signal": "post_hoc_filtering",
                "severity": "high",
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "manipulation_detected": len(manipulation_signals) > 0,
                "signals": manipulation_signals,
            },
            confidence=min(1.0, len(manipulation_signals) * 0.4),
            reasoning=f"Found {len(manipulation_signals)} manipulation signals",
        )

    def _detect_fraud(
        self, scores: dict[str, Any], evidence: dict[str, Any]
    ) -> SkillResult:
        """Detect outright fraud in benchmark results."""
        fraud_indicators = []

        if evidence.get("fabricated_data"):
            fraud_indicators.append({
                "indicator": "data_fabrication",
                "severity": "critical",
            })

        if evidence.get("impossible_results"):
            fraud_indicators.append({
                "indicator": "impossible_results",
                "severity": "critical",
            })

        if evidence.get("tampered_baselines"):
            fraud_indicators.append({
                "indicator": "baseline_tampering",
                "severity": "critical",
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "fraud_detected": len(fraud_indicators) > 0,
                "indicators": fraud_indicators,
            },
            confidence=min(1.0, len(fraud_indicators) * 0.5),
            reasoning=f"Found {len(fraud_indicators)} fraud indicators",
        )
