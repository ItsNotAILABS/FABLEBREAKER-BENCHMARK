"""
Refactoring Skill — identifies code that needs improvement and suggests changes.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class RefactoringSkill(Skill):
    """
    Identifies code smells, duplication, and structural issues.
    Suggests refactoring opportunities to improve maintainability.
    """

    def __init__(self) -> None:
        super().__init__(
            name="refactoring",
            description="Identifies code smells, duplication, complexity hotspots, "
                        "and suggests refactoring for better maintainability.",
            level=SkillLevel.PROFICIENT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Analyze code for refactoring opportunities.

        Context should contain:
        - code: source code to analyze
        - language: programming language (default: "python")
        - threshold_complexity: max acceptable complexity (default: 10)
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        threshold = context.get("threshold_complexity", 10)

        if not code:
            return SkillResult(
                skill_name=self.name,
                success=False,
                reasoning="No code provided for refactoring analysis",
            )

        opportunities = []
        opportunities.extend(self._check_complexity(code, threshold))
        opportunities.extend(self._check_duplication(code))
        opportunities.extend(self._check_code_smells(code, language))
        opportunities.extend(self._check_structure(code, language))

        priority_order = {"high": 0, "medium": 1, "low": 2}
        opportunities.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "opportunities": opportunities,
                "total_opportunities": len(opportunities),
                "high_priority": sum(1 for o in opportunities if o.get("priority") == "high"),
                "estimated_improvement": self._estimate_improvement(opportunities),
            },
            confidence=0.8,
            reasoning=f"Found {len(opportunities)} refactoring opportunities",
        )

    def _check_complexity(self, code: str, threshold: int) -> list[dict[str, Any]]:  # pylint: disable=unused-argument
        """Check for excessive complexity."""
        opportunities = []
        lines = code.split("\n")

        # Check function lengths
        func_pattern = re.compile(r"^(\s*)def\s+(\w+)\s*\(")
        current_func = None
        func_start = 0

        for idx, line in enumerate(lines):
            match = func_pattern.match(line)
            if match:
                if current_func and (idx - func_start) > 50:
                    opportunities.append({
                        "type": "long_function",
                        "function": current_func,
                        "lines": idx - func_start,
                        "priority": "high" if (idx - func_start) > 100 else "medium",
                        "suggestion": f"Split {current_func} into smaller functions",
                    })
                current_func = match.group(2)
                func_start = idx

        # Check last function
        if current_func and (len(lines) - func_start) > 50:
            opportunities.append({
                "type": "long_function",
                "function": current_func,
                "lines": len(lines) - func_start,
                "priority": "medium",
                "suggestion": f"Split {current_func} into smaller functions",
            })

        # Check nesting depth
        max_depth = 0
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                depth = (len(line) - len(stripped)) // 4
                max_depth = max(max_depth, depth)

        if max_depth > 5:
            opportunities.append({
                "type": "deep_nesting",
                "max_depth": max_depth,
                "priority": "high",
                "suggestion": "Reduce nesting with early returns or extraction",
            })

        return opportunities

    def _check_duplication(self, code: str) -> list[dict[str, Any]]:
        """Check for code duplication."""
        opportunities = []
        lines = code.split("\n")

        # Simple line-level duplication detection
        line_counts: dict[str, int] = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith("#"):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

        duplicated = {line: count for line, count in line_counts.items() if count >= 3}
        if duplicated:
            opportunities.append({
                "type": "code_duplication",
                "duplicated_lines": len(duplicated),
                "worst_offender": max(duplicated, key=duplicated.get),
                "max_repetitions": max(duplicated.values()),
                "priority": "medium",
                "suggestion": "Extract duplicated code into shared functions",
            })

        return opportunities

    def _check_code_smells(self, code: str, language: str) -> list[dict[str, Any]]:
        """Check for common code smells."""
        opportunities = []

        if language == "python":
            # God class detection
            class_methods = re.findall(r"class\s+(\w+)", code)
            for cls in class_methods:
                # Count methods in class (simplified)
                cls_pattern = rf"class\s+{cls}[^:]*:(.+?)(?=\nclass\s|\Z)"
                match = re.search(cls_pattern, code, re.DOTALL)
                if match:
                    methods = re.findall(r"def\s+\w+", match.group(1))
                    if len(methods) > 15:
                        opportunities.append({
                            "type": "god_class",
                            "class": cls,
                            "method_count": len(methods),
                            "priority": "high",
                            "suggestion": f"Split {cls} into smaller, focused classes",
                        })

            # Long parameter lists
            long_params = re.findall(r"def\s+(\w+)\s*\(([^)]{100,})\)", code)
            for func_name, params in long_params:
                param_count = params.count(",") + 1
                if param_count > 5:
                    opportunities.append({
                        "type": "long_parameter_list",
                        "function": func_name,
                        "param_count": param_count,
                        "priority": "medium",
                        "suggestion": f"Use a dataclass or config object for {func_name} parameters",
                    })

        return opportunities

    def _check_structure(self, code: str, language: str) -> list[dict[str, Any]]:
        """Check structural issues."""
        opportunities = []

        # Check file length
        line_count = code.count("\n") + 1
        if line_count > 500:
            opportunities.append({
                "type": "large_file",
                "lines": line_count,
                "priority": "medium",
                "suggestion": "Consider splitting into multiple modules",
            })

        # Check import count (Python)
        if language == "python":
            imports = re.findall(r"^(?:from|import)\s+", code, re.MULTILINE)
            if len(imports) > 20:
                opportunities.append({
                    "type": "excessive_imports",
                    "import_count": len(imports),
                    "priority": "low",
                    "suggestion": "High import count may indicate the module has too many responsibilities",
                })

        return opportunities

    def _estimate_improvement(self, opportunities: list[dict[str, Any]]) -> str:
        """Estimate the improvement from addressing opportunities."""
        high = sum(1 for o in opportunities if o.get("priority") == "high")
        if high >= 3:
            return "significant — addressing high-priority items will greatly improve maintainability"
        if high >= 1:
            return "moderate — some important structural improvements available"
        if opportunities:
            return "minor — code is generally well-structured with small improvements possible"
        return "none needed — code structure is clean"
