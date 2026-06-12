"""
FableBreaker SDK Core — the main entry point for using FableBreaker as a library.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add parent to path so we can import fablebreaker_lib
SDK_ROOT = Path(__file__).resolve().parent.parent
if str(SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(SDK_ROOT))

from fablebreaker_lib.intelligence.skills import (  # noqa: E402
    SkillRegistry,
    AnalysisSkill,
    GenerationSkill,
    DetectionSkill,
    ReasoningSkill,
    SynthesisSkill,
    CodeReviewSkill,
    CoverageSkill,
    SecuritySkill,
    RefactoringSkill,
    DocumentationSkill,
    SelfAnalysisSkill,
)


class FableBreaker:
    """
    The FableBreaker AI SDK — your adversarial evaluation companion.

    Use FableBreaker to:
    - Review code for bugs, security issues, and missed edge cases
    - Analyze test and documentation coverage
    - Generate adversarial test cases
    - Detect gaming and manipulation in AI evaluations
    - Run self-analysis on your own codebase
    - Produce certification reports

    Example:
        fb = FableBreaker()
        result = fb.review_code(open("myfile.py").read())
        print(result["findings"])
    """

    def __init__(self) -> None:
        self._registry = SkillRegistry()
        self._register_all_skills()

    def _register_all_skills(self) -> None:
        """Register all available skills."""
        skills = [
            AnalysisSkill(),
            GenerationSkill(),
            DetectionSkill(),
            ReasoningSkill(),
            SynthesisSkill(),
            CodeReviewSkill(),
            CoverageSkill(),
            SecuritySkill(),
            RefactoringSkill(),
            DocumentationSkill(),
            SelfAnalysisSkill(),
        ]
        for skill in skills:
            self._registry.register(skill)

    @property
    def skills(self) -> list[str]:
        """List all available skills."""
        return self._registry.skill_names

    @property
    def skill_count(self) -> int:
        """Number of registered skills."""
        return self._registry.total_skills

    def review_code(
        self,
        code: str,
        language: str = "python",
        focus: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Review code for issues.

        Args:
            code: Source code string to review.
            language: Programming language (default: "python").
            focus: Focus areas — any of ["correctness", "security", "style", "completeness"].

        Returns:
            Dict with findings, severity breakdown, and line count.
        """
        context = {
            "code": code,
            "language": language,
            "focus": focus or ["correctness", "security", "style", "completeness"],
        }
        result = self._registry.activate("code_review", context)
        return result.to_dict()

    def scan_security(
        self,
        code: str,
        scan_type: str = "code",
    ) -> dict[str, Any]:
        """
        Scan code for security vulnerabilities.

        Args:
            code: Source code to scan.
            scan_type: Type of scan — "code", "config", "dependencies", "architecture".

        Returns:
            Dict with vulnerabilities, risk score, and severity counts.
        """
        context = {"code": code, "scan_type": scan_type}
        result = self._registry.activate("security", context)
        return result.to_dict()

    def check_coverage(
        self,
        source_files: list[dict[str, str]],
        test_files: list[dict[str, str]] | None = None,
        coverage_type: str = "test",
    ) -> dict[str, Any]:
        """
        Check coverage gaps.

        Args:
            source_files: List of dicts with "name" and "content" keys.
            test_files: List of test file dicts (for test coverage).
            coverage_type: "test", "documentation", "evaluation", "error_handling".

        Returns:
            Dict with coverage percentage and gaps found.
        """
        context = {
            "coverage_type": coverage_type,
            "source_files": source_files,
            "test_files": test_files or [],
        }
        result = self._registry.activate("coverage", context)
        return result.to_dict()

    def suggest_refactoring(
        self,
        code: str,
        language: str = "python",
        threshold_complexity: int = 10,
    ) -> dict[str, Any]:
        """
        Get refactoring suggestions for code.

        Args:
            code: Source code to analyze.
            language: Programming language.
            threshold_complexity: Max acceptable complexity.

        Returns:
            Dict with refactoring opportunities.
        """
        context = {
            "code": code,
            "language": language,
            "threshold_complexity": threshold_complexity,
        }
        result = self._registry.activate("refactoring", context)
        return result.to_dict()

    def audit_documentation(
        self,
        code: str,
        doc_action: str = "analyze",
        module_name: str = "module",
    ) -> dict[str, Any]:
        """
        Audit documentation quality.

        Args:
            code: Source code to check for documentation.
            doc_action: "analyze", "audit", "generate_api", "generate_readme".
            module_name: Name of the module being documented.

        Returns:
            Dict with documentation score and issues.
        """
        context = {"code": code, "doc_action": doc_action, "module_name": module_name}
        result = self._registry.activate("documentation", context)
        return result.to_dict()

    def generate_adversarial(
        self,
        domain: str = "code",
        count: int = 10,
        difficulty: int = 5,
        seed: int = 42,
    ) -> dict[str, Any]:
        """
        Generate adversarial test cases.

        Args:
            domain: Target domain — "code", "math", "language", "safety", etc.
            count: Number of cases to generate.
            difficulty: 1-10 difficulty scale.
            seed: Random seed for reproducibility.

        Returns:
            Dict with generated adversarial cases.
        """
        context = {
            "generation_type": "adversarial_cases",
            "domain": domain,
            "count": count,
            "difficulty": difficulty,
            "seed": seed,
        }
        result = self._registry.activate("generation", context)
        return result.to_dict()

    def detect_gaming(
        self,
        scores: dict[str, Any] | None = None,
        evidence: dict[str, Any] | None = None,
        detection_type: str = "gaming",
    ) -> dict[str, Any]:
        """
        Detect gaming or manipulation in evaluation results.

        Args:
            scores: Benchmark scores to analyze.
            evidence: Supporting evidence for detection.
            detection_type: "contamination", "gaming", "manipulation", "fraud".

        Returns:
            Dict with detection results.
        """
        context = {
            "detection_type": detection_type,
            "scores": scores or {},
            "evidence": evidence or {},
        }
        result = self._registry.activate("detection", context)
        return result.to_dict()

    def self_analyze(
        self,
        source_files: list[dict[str, str]],
        depth: str = "standard",
    ) -> dict[str, Any]:
        """
        Run FableBreaker on your own code (dogfooding).

        This is the key use case: use FableBreaker to evaluate your own
        codebase so you don't miss anything.

        Args:
            source_files: List of dicts with "name" and "content" keys.
            depth: "shallow", "standard", or "deep".

        Returns:
            Dict with self-analysis report and verdict.
        """
        context = {
            "own_source_files": source_files,
            "analysis_depth": depth,
        }
        result = self._registry.activate("self_analysis", context)
        return result.to_dict()

    def full_scan(
        self,
        code: str,
        language: str = "python",
        filename: str = "unknown.py",
    ) -> dict[str, Any]:
        """
        Run ALL skills on a piece of code — the complete FableBreaker treatment.

        Args:
            code: Source code to evaluate.
            language: Programming language.
            filename: Filename for reporting.

        Returns:
            Comprehensive report from all applicable skills.
        """
        results = {}

        # Code review
        results["code_review"] = self.review_code(code, language)

        # Security scan
        results["security"] = self.scan_security(code)

        # Refactoring suggestions
        results["refactoring"] = self.suggest_refactoring(code, language)

        # Documentation audit
        results["documentation"] = self.audit_documentation(code)

        # Self-analysis
        source = [{"name": filename, "content": code}]
        results["self_analysis"] = self.self_analyze(source)

        # Overall summary
        total_issues = sum(
            r.get("output", {}).get("total_issues", 0) or
            r.get("output", {}).get("total_findings", 0) or
            r.get("output", {}).get("total_opportunities", 0) or 0
            for r in results.values()
        )

        results["summary"] = {
            "file": filename,
            "language": language,
            "total_issues_across_all_skills": total_issues,
            "skills_invoked": list(results.keys()),
        }

        return results

    def summary(self) -> dict[str, Any]:
        """Get SDK summary including all skills and their status."""
        return {
            "sdk_version": "1.0.0",
            "skills": self._registry.summary(),
        }
