"""
Self-Analysis Skill — FableBreaker analyzes its own codebase.

This is the dogfooding skill: FableBreaker uses itself to evaluate itself,
identifying gaps, risks, and improvements in its own implementation.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class SelfAnalysisSkill(Skill):
    """
    FableBreaker's self-analysis capability — dogfooding at its finest.

    This skill allows FableBreaker to analyze its own code, identify
    its own blind spots, and report what it finds. The ultimate test
    of an evaluation system is whether it can evaluate itself.
    """

    def __init__(self) -> None:
        super().__init__(
            name="self_analysis",
            description="FableBreaker analyzes its own codebase — the ultimate dogfood test. "
                        "Identifies gaps, risks, and improvements in its own implementation.",
            level=SkillLevel.MASTER,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform self-analysis on FableBreaker's own code.

        Context should contain:
        - own_source_files: list of FableBreaker's own source files
        - analysis_depth: "shallow", "standard", "deep"
        - focus_areas: list of areas to focus on
        """
        source_files = context.get("own_source_files", [])
        depth = context.get("analysis_depth", "standard")
        focus_areas = context.get("focus_areas", [
            "completeness", "consistency", "security",
            "robustness", "self_reference_integrity",
        ])

        findings = []

        if "completeness" in focus_areas:
            findings.extend(self._check_completeness(source_files))
        if "consistency" in focus_areas:
            findings.extend(self._check_consistency(source_files))
        if "security" in focus_areas:
            findings.extend(self._check_own_security(source_files))
        if "robustness" in focus_areas:
            findings.extend(self._check_robustness(source_files))
        if "self_reference_integrity" in focus_areas:
            findings.extend(self._check_self_reference(source_files))

        # Meta-analysis: can we detect our own blind spots?
        meta = self._meta_analysis(findings, source_files)

        severity_counts = {}
        for f in findings:
            sev = f.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "self_analysis_report": {
                    "total_findings": len(findings),
                    "severity_breakdown": severity_counts,
                    "findings": findings,
                    "meta_analysis": meta,
                    "depth": depth,
                    "files_analyzed": len(source_files),
                },
                "verdict": self._overall_verdict(findings),
            },
            confidence=0.85,
            reasoning=(
                f"Self-analysis complete: {len(findings)} findings across "
                f"{len(source_files)} files. "
                f"FableBreaker found issues in its own code — proof the system works."
            ),
        )

    def _check_completeness(self, source_files: list[Any]) -> list[dict[str, Any]]:
        """Check if FableBreaker's own capabilities are complete."""
        findings = []

        all_code = self._join_sources(source_files)

        # Check: do all skills have proper error handling?
        invoke_methods = re.findall(r"def\s+invoke\s*\(self.*?\).*?:", all_code)
        if len(invoke_methods) < 5:
            findings.append({
                "area": "completeness",
                "severity": "medium",
                "finding": "Fewer invoke methods than expected — some skills may be stubs",
                "recommendation": "Ensure all skills have full implementations",
            })

        # Check: are there TODO/FIXME markers?
        todos = re.findall(r"#\s*(TODO|FIXME|HACK|XXX).*", all_code)
        if todos:
            findings.append({
                "area": "completeness",
                "severity": "low",
                "finding": f"{len(todos)} TODO/FIXME markers found in own code",
                "items": [t.strip() for t in todos[:5]],
                "recommendation": "Resolve or track these as issues",
            })

        # Check: is there comprehensive test coverage?
        test_funcs = re.findall(r"def\s+test_\w+", all_code)
        if len(test_funcs) < 10:
            findings.append({
                "area": "completeness",
                "severity": "medium",
                "finding": f"Only {len(test_funcs)} test functions found — coverage may be insufficient",
                "recommendation": "Add more tests for critical paths",
            })

        return findings

    def _check_consistency(self, source_files: list[Any]) -> list[dict[str, Any]]:
        """Check internal consistency of FableBreaker's code."""
        findings = []

        all_code = self._join_sources(source_files)

        # Check: consistent use of SkillResult
        skill_results_success = len(re.findall(r"SkillResult\([^)]*success=True", all_code))
        skill_results_failure = len(re.findall(r"SkillResult\([^)]*success=False", all_code))

        if skill_results_failure == 0 and skill_results_success > 0:
            findings.append({
                "area": "consistency",
                "severity": "medium",
                "finding": "No failure paths in skill implementations — all skills always succeed?",
                "recommendation": "Add proper error handling and failure returns",
            })

        # Check: consistent confidence scoring
        confidences = re.findall(r"confidence=([0-9.]+)", all_code)
        if confidences:
            values = [float(c) for c in confidences]
            if all(v == values[0] for v in values):
                findings.append({
                    "area": "consistency",
                    "severity": "low",
                    "finding": "All confidence scores are identical — not calibrated per-result",
                    "recommendation": "Calibrate confidence based on actual certainty",
                })

        return findings

    def _check_own_security(self, source_files: list[Any]) -> list[dict[str, Any]]:
        """Check FableBreaker's own security posture."""
        findings = []
        all_code = self._join_sources(source_files)

        # Check for eval/exec
        if re.search(r"\beval\s*\(", all_code):
            findings.append({
                "area": "security",
                "severity": "critical",
                "finding": "FableBreaker uses eval() in its own code",
                "recommendation": "Remove eval() usage — practice what we preach",
            })

        # Check for path traversal in own file handling
        if re.search(r"open\s*\([^)]*\+", all_code):
            findings.append({
                "area": "security",
                "severity": "high",
                "finding": "String concatenation in file paths — potential traversal",
                "recommendation": "Use pathlib with proper validation",
            })

        # Check: does the service validate all inputs?
        if "subprocess" in all_code and "sanitize" not in all_code.lower():
            findings.append({
                "area": "security",
                "severity": "medium",
                "finding": "Subprocess calls without explicit input sanitization",
                "recommendation": "Add input validation before subprocess invocations",
            })

        return findings

    def _check_robustness(self, source_files: list[Any]) -> list[dict[str, Any]]:
        """Check robustness of FableBreaker's own implementation."""
        findings = []
        all_code = self._join_sources(source_files)

        # Check: graceful handling of missing data
        dict_gets = len(re.findall(r"\.get\(", all_code))
        direct_access = len(re.findall(r"\[\s*['\"]", all_code))

        if direct_access > dict_gets * 2:
            findings.append({
                "area": "robustness",
                "severity": "medium",
                "finding": "More direct dict access than .get() — missing key errors likely",
                "recommendation": "Use .get() with defaults for optional fields",
            })

        # Check: timeout handling
        if "requests" in all_code and "timeout" not in all_code:
            findings.append({
                "area": "robustness",
                "severity": "high",
                "finding": "HTTP requests without timeout — can hang indefinitely",
                "recommendation": "Always specify timeout for network operations",
            })

        # Check: resource cleanup
        if re.search(r"open\s*\(", all_code) and "with" not in all_code:
            findings.append({
                "area": "robustness",
                "severity": "medium",
                "finding": "File operations without context manager",
                "recommendation": "Use 'with' statements for resource management",
            })

        return findings

    def _check_self_reference(self, source_files: list[Any]) -> list[dict[str, Any]]:
        """Check the integrity of FableBreaker's self-referential claims."""
        findings = []
        all_code = self._join_sources(source_files)

        # Does FableBreaker claim capabilities it doesn't implement?
        claimed_skills = re.findall(r"name=\"(\w+)\"", all_code)
        implemented_invokes = re.findall(r"class\s+(\w+Skill)\s*\(Skill\)", all_code)

        if len(claimed_skills) > len(implemented_invokes):
            findings.append({
                "area": "self_reference",
                "severity": "high",
                "finding": "More claimed skills than implemented skill classes",
                "recommendation": "Ensure every claimed skill has a real implementation",
            })

        # Check: are all registered skills actually importable?
        all_exports = re.findall(r"\"(\w+Skill)\"", all_code)
        all_classes = re.findall(r"class\s+(\w+Skill)", all_code)
        missing = set(all_exports) - set(all_classes)
        if missing:
            findings.append({
                "area": "self_reference",
                "severity": "high",
                "finding": f"Exported skills not found as classes: {missing}",
                "recommendation": "Implement or remove unimplemented skill references",
            })

        return findings

    def _meta_analysis(
        self, findings: list[dict[str, Any]], source_files: list[Any]  # pylint: disable=unused-argument
    ) -> dict[str, Any]:
        """Meta-analysis: what can we learn from analyzing ourselves?"""
        return {
            "can_detect_own_issues": len(findings) > 0,
            "self_awareness_score": min(1.0, len(findings) / 10.0),
            "blind_spot_risk": (
                "low" if len(findings) > 5
                else "medium" if len(findings) > 2
                else "high — may be missing issues"
            ),
            "insight": (
                "FableBreaker successfully identified issues in its own code. "
                "This demonstrates the system's ability to evaluate without bias, "
                "even when the subject is itself."
            ),
        }

    def _overall_verdict(self, findings: list[dict[str, Any]]) -> str:
        """Overall verdict on self-analysis."""
        critical = sum(1 for f in findings if f.get("severity") == "critical")
        high = sum(1 for f in findings if f.get("severity") == "high")

        if critical > 0:
            return "NEEDS_IMMEDIATE_ATTENTION — critical issues found in own code"
        if high > 2:
            return "NEEDS_IMPROVEMENT — multiple high-severity issues"
        if findings:
            return "HEALTHY_WITH_NOTES — minor issues found, system is self-aware"
        return "PRISTINE — no issues detected (suspicious — may indicate blind spots)"

    def _join_sources(self, source_files: list[Any]) -> str:
        """Join source files into a single string for analysis."""
        parts = []
        for source in source_files:
            if isinstance(source, dict):
                parts.append(source.get("content", ""))
            else:
                parts.append(str(source))
        return "\n".join(parts)
