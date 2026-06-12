"""
Synthesis Skill — combines information to produce intelligence outputs.
"""

from __future__ import annotations

from typing import Any

from .base import Skill, SkillLevel, SkillResult


class SynthesisSkill(Skill):
    """
    Synthesizes information from multiple sources into actionable intelligence.

    This skill combines knowledge base data, engine results, and
    other skill outputs into coherent reports and recommendations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="synthesis",
            description="Combines information from multiple sources into actionable intelligence. "
                        "Produces reports, recommendations, and certification summaries.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Synthesize information.

        Context should contain:
        - synthesis_type: "report", "recommendation", "landscape", "verdict"
        - inputs: list of data sources to synthesize
        """
        synthesis_type = context.get("synthesis_type", "report")
        inputs = context.get("inputs", [])

        if synthesis_type == "report":
            return self._synthesize_report(inputs, context)
        if synthesis_type == "recommendation":
            return self._synthesize_recommendation(inputs, context)
        if synthesis_type == "landscape":
            return self._synthesize_landscape(inputs, context)
        if synthesis_type == "verdict":
            return self._synthesize_verdict(inputs, context)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown synthesis type: {synthesis_type}",
        )

    def _synthesize_report(
        self, inputs: list[Any], context: dict[str, Any]
    ) -> SkillResult:
        """Synthesize a comprehensive evaluation report."""
        report = {
            "title": context.get("title", "Fablebreaker Intelligence Report"),
            "sections": [],
            "executive_summary": "",
            "recommendations": [],
            "confidence": 0.0,
        }

        total_confidence = 0.0
        all_findings = []

        for source in inputs:
            if isinstance(source, dict):
                section = {
                    "source": source.get("engine_name", source.get("skill_name", "unknown")),
                    "verdict": source.get("verdict", source.get("output", "")),
                    "confidence": source.get("confidence", 0.0),
                    "findings_count": len(source.get("findings", [])),
                }
                report["sections"].append(section)
                total_confidence += source.get("confidence", 0.0)
                all_findings.extend(source.get("findings", []))

        if inputs:
            report["confidence"] = total_confidence / len(inputs)

        report["executive_summary"] = (
            f"Synthesized {len(inputs)} sources with {len(all_findings)} total findings. "
            f"Overall confidence: {report['confidence']:.2f}."
        )

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=report,
            confidence=report["confidence"],
            reasoning=f"Synthesized report from {len(inputs)} sources",
            artifacts=[{"type": "report", "sections": len(report["sections"])}],
        )

    def _synthesize_recommendation(
        self, inputs: list[Any], context: dict[str, Any]
    ) -> SkillResult:
        """Synthesize actionable recommendations."""
        recommendations = []
        issues_found = []

        for source in inputs:
            if isinstance(source, dict):
                findings = source.get("findings", [])
                for finding in findings:
                    if isinstance(finding, dict):
                        severity = finding.get("severity", "medium")
                        if severity in ("critical", "high"):
                            issues_found.append(finding)

        # Generate recommendations from issues
        if not issues_found:
            recommendations.append({
                "priority": "low",
                "action": "Continue monitoring — no critical issues detected",
                "rationale": "All evaluation gates passed",
            })
        else:
            for issue in issues_found[:5]:
                recommendations.append({
                    "priority": issue.get("severity", "medium"),
                    "action": f"Address: {issue.get('finding', issue.get('signal', 'unknown issue'))}",
                    "rationale": issue.get("interpretation", issue.get("evidence", "")),
                })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "recommendations": recommendations,
                "total_issues": len(issues_found),
                "critical_issues": sum(1 for i in issues_found if i.get("severity") == "critical"),
            },
            confidence=0.85,
            reasoning=f"Generated {len(recommendations)} recommendations from {len(issues_found)} issues",
        )

    def _synthesize_landscape(
        self, inputs: list[Any], context: dict[str, Any]
    ) -> SkillResult:
        """Synthesize a landscape view of the benchmark ecosystem."""
        domains_covered = set()
        total_benchmarks = 0
        gaming_risk_benchmarks = 0
        trustworthy_benchmarks = 0

        for source in inputs:
            if isinstance(source, dict):
                domains_covered.add(source.get("domain", "unknown"))
                total_benchmarks += 1
                if source.get("gaming_vectors"):
                    gaming_risk_benchmarks += 1
                tags = source.get("tags", [])
                if "contamination_resistant" in tags or "verified" in tags:
                    trustworthy_benchmarks += 1

        landscape = {
            "total_benchmarks": total_benchmarks,
            "domains_covered": sorted(domains_covered),
            "gaming_risk_percentage": (
                gaming_risk_benchmarks / total_benchmarks * 100 if total_benchmarks else 0
            ),
            "trustworthy_percentage": (
                trustworthy_benchmarks / total_benchmarks * 100 if total_benchmarks else 0
            ),
            "ecosystem_health": self._assess_health(
                gaming_risk_benchmarks, trustworthy_benchmarks, total_benchmarks
            ),
        }

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=landscape,
            confidence=0.8,
            reasoning=f"Landscape synthesis of {total_benchmarks} benchmarks across {len(domains_covered)} domains",
        )

    def _synthesize_verdict(
        self, inputs: list[Any], context: dict[str, Any]
    ) -> SkillResult:
        """Synthesize a final verdict from multiple engine/skill results."""
        verdicts = []
        for source in inputs:
            if isinstance(source, dict) and "verdict" in source:
                verdicts.append(source["verdict"])

        positive_verdicts = ["certified", "CERTIFIED", "resilient", "clean", "trustworthy"]
        negative_verdicts = ["failed", "REJECTED", "vulnerable", "contamination_detected", "unreliable"]

        positive_count = sum(1 for v in verdicts if v in positive_verdicts)
        negative_count = sum(1 for v in verdicts if v in negative_verdicts)

        if negative_count > 0:
            final_verdict = "REJECTED"
            confidence = 0.9
        elif positive_count == len(verdicts) and verdicts:
            final_verdict = "CERTIFIED"
            confidence = 0.95
        else:
            final_verdict = "INCONCLUSIVE"
            confidence = 0.5

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "final_verdict": final_verdict,
                "component_verdicts": verdicts,
                "positive_signals": positive_count,
                "negative_signals": negative_count,
            },
            confidence=confidence,
            reasoning=f"Final verdict: {final_verdict} ({positive_count} positive, {negative_count} negative signals)",
        )

    def _assess_health(self, gaming_risk: int, trustworthy: int, total: int) -> str:
        """Assess overall ecosystem health."""
        if total == 0:
            return "unknown"
        risk_pct = gaming_risk / total
        trust_pct = trustworthy / total
        if risk_pct > 0.6:
            return "unhealthy — majority of benchmarks have gaming risks"
        if trust_pct > 0.5:
            return "healthy — majority of benchmarks are trustworthy"
        return "mixed — benchmark ecosystem has significant trust gaps"
