"""
Code Review Skill — reviews code for correctness, style, and missed issues.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class CodeReviewSkill(Skill):
    """
    Reviews code for correctness, missed edge cases, security issues,
    and style problems. Helps ensure nothing is missed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="code_review",
            description="Reviews code for correctness, missed edge cases, security "
                        "vulnerabilities, and style issues. Catches what humans miss.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform code review.

        Context should contain:
        - code: source code string to review
        - language: programming language (default: "python")
        - focus: list of focus areas (e.g., ["security", "correctness", "style"])
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        focus = context.get("focus", ["correctness", "security", "style", "completeness"])

        if not code:
            return SkillResult(
                skill_name=self.name,
                success=False,
                reasoning="No code provided for review",
            )

        findings = []

        if "correctness" in focus:
            findings.extend(self._check_correctness(code, language))
        if "security" in focus:
            findings.extend(self._check_security(code, language))
        if "style" in focus:
            findings.extend(self._check_style(code, language))
        if "completeness" in focus:
            findings.extend(self._check_completeness(code, language))

        severity_counts = {}
        for finding in findings:
            sev = finding.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "findings": findings,
                "total_issues": len(findings),
                "severity_breakdown": severity_counts,
                "language": language,
                "lines_reviewed": code.count("\n") + 1,
            },
            confidence=0.85,
            reasoning=f"Reviewed {code.count(chr(10)) + 1} lines, found {len(findings)} issues",
        )

    def _check_correctness(self, code: str, language: str) -> list[dict[str, Any]]:
        """Check for correctness issues."""
        issues = []

        if language == "python":
            # Bare except
            if re.search(r"\bexcept\s*:", code):
                issues.append({
                    "category": "correctness",
                    "severity": "medium",
                    "finding": "Bare except clause catches all exceptions including SystemExit",
                    "suggestion": "Use specific exception types",
                })

            # Mutable default arguments
            if re.search(r"def\s+\w+\([^)]*=\s*(\[\]|\{\})", code):
                issues.append({
                    "category": "correctness",
                    "severity": "high",
                    "finding": "Mutable default argument detected",
                    "suggestion": "Use None as default and initialize inside function",
                })

            # Division without zero check
            if re.search(r"/\s*\w+", code) and "ZeroDivisionError" not in code:
                if "/ 0" not in code and "division" not in code.lower():
                    issues.append({
                        "category": "correctness",
                        "severity": "low",
                        "finding": "Division operation without apparent zero-division guard",
                        "suggestion": "Consider adding zero-division protection",
                    })

        return issues

    def _check_security(self, code: str, language: str) -> list[dict[str, Any]]:  # noqa: W0613
        """Check for security issues."""
        issues = []

        # SQL injection patterns
        if re.search(r"(execute|query)\s*\([^)]*(%s|f\"|\.format)", code):
            issues.append({
                "category": "security",
                "severity": "critical",
                "finding": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries",
            })

        # Hardcoded secrets
        if re.search(r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            issues.append({
                "category": "security",
                "severity": "critical",
                "finding": "Hardcoded secret or credential detected",
                "suggestion": "Use environment variables or secret management",
            })

        # Eval/exec usage
        if re.search(r"\b(eval|exec)\s*\(", code):
            issues.append({
                "category": "security",
                "severity": "high",
                "finding": "Use of eval/exec detected — potential code injection",
                "suggestion": "Use ast.literal_eval or safer alternatives",
            })

        # Subprocess shell=True
        if "shell=True" in code:
            issues.append({
                "category": "security",
                "severity": "high",
                "finding": "subprocess with shell=True — command injection risk",
                "suggestion": "Use shell=False with argument list",
            })

        return issues

    def _check_style(self, code: str, language: str) -> list[dict[str, Any]]:  # noqa: W0613
        """Check for style issues."""
        issues = []
        lines = code.split("\n")

        # Long lines
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append({
                "category": "style",
                "severity": "low",
                "finding": f"{len(long_lines)} lines exceed 120 characters",
                "lines": long_lines[:5],
            })

        # TODO/FIXME/HACK comments
        todo_pattern = re.findall(r"#\s*(TODO|FIXME|HACK|XXX).*", code, re.IGNORECASE)
        if todo_pattern:
            issues.append({
                "category": "style",
                "severity": "info",
                "finding": f"{len(todo_pattern)} TODO/FIXME markers found",
                "suggestion": "Track these as issues or resolve them",
            })

        return issues

    def _check_completeness(self, code: str, language: str) -> list[dict[str, Any]]:
        """Check for completeness issues — things that might be missed."""
        issues = []

        if language == "python":
            # Functions without docstrings
            funcs = re.findall(r"def\s+(\w+)\s*\(", code)
            documented = re.findall(r'def\s+\w+\s*\([^)]*\)[^:]*:\s*\n\s*"""', code)
            undocumented = len(funcs) - len(documented)
            if undocumented > 0 and len(funcs) > 0:
                issues.append({
                    "category": "completeness",
                    "severity": "low",
                    "finding": f"{undocumented}/{len(funcs)} functions lack docstrings",
                    "suggestion": "Add docstrings for public API functions",
                })

            # No type hints
            untyped = re.findall(r"def\s+\w+\s*\([^)]*\)\s*:", code)
            typed = re.findall(r"def\s+\w+\s*\([^)]*\)\s*->", code)
            if len(untyped) > len(typed) and len(untyped) > 0:
                issues.append({
                    "category": "completeness",
                    "severity": "low",
                    "finding": "Some functions lack return type annotations",
                    "suggestion": "Add type hints for better tooling support",
                })

            # No error handling in I/O operations
            if re.search(r"(open|read|write)\s*\(", code) and "try" not in code:
                issues.append({
                    "category": "completeness",
                    "severity": "medium",
                    "finding": "I/O operations without error handling",
                    "suggestion": "Wrap file/network operations in try/except",
                })

        return issues
