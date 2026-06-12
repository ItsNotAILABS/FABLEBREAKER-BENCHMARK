"""
Coverage Skill — identifies gaps in testing and evaluation coverage.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class CoverageSkill(Skill):
    """
    Identifies gaps in testing, evaluation, and documentation coverage.

    Ensures nothing is missed — finds the blind spots that teams
    overlook when building and evaluating AI systems.
    """

    def __init__(self) -> None:
        super().__init__(
            name="coverage",
            description="Identifies gaps in testing, evaluation, and documentation. "
                        "Finds blind spots and ensures nothing important is missed.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Analyze coverage gaps.

        Context should contain:
        - coverage_type: "test", "documentation", "evaluation", "error_handling"
        - source_files: list of source file contents or paths
        - test_files: list of test file contents (for test coverage)
        - modules: list of module descriptions
        """
        coverage_type = context.get("coverage_type", "test")
        source_files = context.get("source_files", [])
        test_files = context.get("test_files", [])

        if coverage_type == "test":
            return self._analyze_test_coverage(source_files, test_files)
        if coverage_type == "documentation":
            return self._analyze_doc_coverage(source_files)
        if coverage_type == "evaluation":
            return self._analyze_eval_coverage(context)
        if coverage_type == "error_handling":
            return self._analyze_error_coverage(source_files)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown coverage type: {coverage_type}",
        )

    def _analyze_test_coverage(
        self, source_files: list[Any], test_files: list[Any]
    ) -> SkillResult:
        """Analyze test coverage gaps."""
        gaps = []
        source_functions = []
        tested_functions = []

        for source in source_files:
            if isinstance(source, dict):
                code = source.get("content", "")
                filename = source.get("name", "unknown")
            else:
                code = str(source)
                filename = "unknown"

            funcs = re.findall(r"def\s+(\w+)\s*\(", code)
            for func in funcs:
                if not func.startswith("_"):
                    source_functions.append({"name": func, "file": filename})

        for test in test_files:
            if isinstance(test, dict):
                code = test.get("content", "")
            else:
                code = str(test)
            tested = re.findall(r"def\s+test_(\w+)", code)
            tested_functions.extend(tested)

        # Find untested public functions
        tested_names = set(tested_functions)
        for func_info in source_functions:
            func_name = func_info["name"]
            if func_name not in tested_names and f"test_{func_name}" not in tested_names:
                gaps.append({
                    "type": "untested_function",
                    "function": func_name,
                    "file": func_info["file"],
                    "severity": "medium",
                })

        coverage_pct = (
            (1.0 - len(gaps) / len(source_functions)) * 100
            if source_functions else 0.0
        )

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "total_public_functions": len(source_functions),
                "tested_functions": len(source_functions) - len(gaps),
                "untested_functions": len(gaps),
                "coverage_percentage": round(coverage_pct, 1),
                "gaps": gaps,
            },
            confidence=0.8,
            reasoning=f"Test coverage: {coverage_pct:.1f}% — {len(gaps)} untested functions found",
        )

    def _analyze_doc_coverage(self, source_files: list[Any]) -> SkillResult:
        """Analyze documentation coverage."""
        gaps = []
        total_items = 0
        documented_items = 0

        for source in source_files:
            if isinstance(source, dict):
                code = source.get("content", "")
                filename = source.get("name", "unknown")
            else:
                code = str(source)
                filename = "unknown"

            # Check classes
            classes = re.findall(r"class\s+(\w+)", code)
            for cls in classes:
                total_items += 1
                pattern = rf'class\s+{cls}[^:]*:\s*\n\s*"""'
                if re.search(pattern, code):
                    documented_items += 1
                else:
                    gaps.append({
                        "type": "undocumented_class",
                        "name": cls,
                        "file": filename,
                    })

            # Check public functions
            funcs = re.findall(r"def\s+(\w+)\s*\(", code)
            for func in funcs:
                if not func.startswith("_"):
                    total_items += 1
                    pattern = rf'def\s+{func}\s*\([^)]*\)[^:]*:\s*\n\s*"""'
                    if re.search(pattern, code):
                        documented_items += 1
                    else:
                        gaps.append({
                            "type": "undocumented_function",
                            "name": func,
                            "file": filename,
                        })

        doc_pct = (documented_items / total_items * 100) if total_items else 0.0

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "total_public_items": total_items,
                "documented_items": documented_items,
                "documentation_percentage": round(doc_pct, 1),
                "gaps": gaps,
            },
            confidence=0.85,
            reasoning=f"Documentation coverage: {doc_pct:.1f}% — {len(gaps)} undocumented items",
        )

    def _analyze_eval_coverage(self, context: dict[str, Any]) -> SkillResult:
        """Analyze evaluation coverage — what scenarios are not being tested."""
        benchmarks = context.get("benchmarks", [])

        coverage_map = {}
        missing = []

        critical_domains = [
            "correctness", "adversarial", "contamination",
            "performance", "robustness", "safety",
        ]

        for domain in critical_domains:
            covered = any(
                domain in str(b.get("tags", [])).lower() or
                domain in str(b.get("name", "")).lower()
                for b in benchmarks if isinstance(b, dict)
            )
            coverage_map[domain] = covered
            if not covered:
                missing.append({
                    "domain": domain,
                    "severity": "high" if domain in ("correctness", "safety") else "medium",
                    "recommendation": f"Add evaluation coverage for {domain}",
                })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "coverage_map": coverage_map,
                "missing_domains": missing,
                "domains_covered": sum(1 for v in coverage_map.values() if v),
                "domains_total": len(critical_domains),
            },
            confidence=0.8,
            reasoning=f"Evaluation coverage: {sum(1 for v in coverage_map.values() if v)}/{len(critical_domains)} domains covered",
        )

    def _analyze_error_coverage(self, source_files: list[Any]) -> SkillResult:
        """Analyze error handling coverage."""
        gaps = []

        for source in source_files:
            if isinstance(source, dict):
                code = source.get("content", "")
                filename = source.get("name", "unknown")
            else:
                code = str(source)
                filename = "unknown"

            # File operations without error handling
            if re.search(r"\bopen\s*\(", code):
                if "try" not in code or "IOError" not in code and "OSError" not in code:
                    gaps.append({
                        "type": "unhandled_io",
                        "file": filename,
                        "severity": "medium",
                    })

            # Network calls without timeout
            if re.search(r"requests\.(get|post|put|delete)\(", code):
                if "timeout" not in code:
                    gaps.append({
                        "type": "no_timeout",
                        "file": filename,
                        "severity": "high",
                    })

            # JSON parsing without error handling
            if "json.loads" in code or "json.load" in code:
                if "JSONDecodeError" not in code and "ValueError" not in code:
                    gaps.append({
                        "type": "unhandled_json_parse",
                        "file": filename,
                        "severity": "medium",
                    })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "error_handling_gaps": gaps,
                "total_gaps": len(gaps),
            },
            confidence=0.75,
            reasoning=f"Found {len(gaps)} error handling gaps",
        )
