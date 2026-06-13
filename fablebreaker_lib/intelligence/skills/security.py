"""
Security Skill — identifies security vulnerabilities and attack surfaces.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class SecuritySkill(Skill):
    """
    Identifies security vulnerabilities, attack surfaces, and
    misconfigurations in code and system designs.
    """

    def __init__(self) -> None:
        super().__init__(
            name="security",
            description="Identifies security vulnerabilities, attack surfaces, "
                        "and misconfigurations. Protects against exploitation.",
            level=SkillLevel.MASTER,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform security analysis.

        Context should contain:
        - scan_type: "code", "config", "dependencies", "architecture"
        - code: source code to scan (for code scan)
        - config: configuration data (for config scan)
        - dependencies: list of dependencies (for dependency scan)
        """
        scan_type = context.get("scan_type", "code")
        code = context.get("code", "")

        if scan_type == "code":
            return self._scan_code(code, context)
        if scan_type == "config":
            return self._scan_config(context)
        if scan_type == "dependencies":
            return self._scan_dependencies(context)
        if scan_type == "architecture":
            return self._scan_architecture(context)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown scan type: {scan_type}",
        )

    def _scan_code(self, code: str, context: dict[str, Any]) -> SkillResult:  # pylint: disable=unused-argument
        """Scan code for security vulnerabilities."""
        vulnerabilities = []

        # Injection vulnerabilities
        if re.search(r"subprocess\.(call|run|Popen)\([^)]*shell\s*=\s*True", code):
            vulnerabilities.append({
                "type": "command_injection",
                "severity": "critical",
                "cwe": "CWE-78",
                "description": "Command injection via shell=True in subprocess",
                "remediation": "Use shell=False with argument list",
            })

        if re.search(r"\beval\s*\(", code):
            vulnerabilities.append({
                "type": "code_injection",
                "severity": "critical",
                "cwe": "CWE-94",
                "description": "Arbitrary code execution via eval()",
                "remediation": "Use ast.literal_eval() or specific parsers",
            })

        # Path traversal
        if re.search(r"open\s*\([^)]*\+", code) or re.search(r"Path\s*\([^)]*\+", code):
            if "sanitize" not in code.lower() and "resolve" not in code:
                vulnerabilities.append({
                    "type": "path_traversal",
                    "severity": "high",
                    "cwe": "CWE-22",
                    "description": "Potential path traversal via string concatenation",
                    "remediation": "Validate and resolve paths, check against allowed directories",
                })

        # Information exposure
        if re.search(r"(traceback|stack_trace|print.*error)", code, re.IGNORECASE):
            if "production" in code.lower() or "prod" in code.lower():
                vulnerabilities.append({
                    "type": "information_exposure",
                    "severity": "medium",
                    "cwe": "CWE-209",
                    "description": "Stack trace or error details may be exposed in production",
                    "remediation": "Use generic error messages in production",
                })

        # Insecure deserialization
        if re.search(r"pickle\.(loads?|Unpickler)", code):
            vulnerabilities.append({
                "type": "insecure_deserialization",
                "severity": "critical",
                "cwe": "CWE-502",
                "description": "Insecure deserialization via pickle",
                "remediation": "Use JSON or other safe serialization formats",
            })

        # Missing authentication checks
        if re.search(r"(route|endpoint|handler)", code, re.IGNORECASE):
            if "auth" not in code.lower() and "token" not in code.lower():
                vulnerabilities.append({
                    "type": "missing_authentication",
                    "severity": "high",
                    "cwe": "CWE-306",
                    "description": "Endpoint handler without apparent authentication check",
                    "remediation": "Add authentication middleware or checks",
                })

        # SSRF potential
        if re.search(r"requests\.(get|post)\s*\([^)]*\w+", code):
            if "allowlist" not in code.lower() and "whitelist" not in code.lower():
                vulnerabilities.append({
                    "type": "ssrf_potential",
                    "severity": "medium",
                    "cwe": "CWE-918",
                    "description": "URL request with potentially user-controlled input",
                    "remediation": "Validate URLs against an allowlist",
                })

        risk_score = min(10.0, sum(
            {"critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}.get(v["severity"], 0)
            for v in vulnerabilities
        ))

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "vulnerabilities": vulnerabilities,
                "total_findings": len(vulnerabilities),
                "risk_score": risk_score,
                "critical_count": sum(1 for v in vulnerabilities if v["severity"] == "critical"),
                "high_count": sum(1 for v in vulnerabilities if v["severity"] == "high"),
            },
            confidence=0.8,
            reasoning=f"Found {len(vulnerabilities)} vulnerabilities, risk score: {risk_score}/10",
        )

    def _scan_config(self, context: dict[str, Any]) -> SkillResult:
        """Scan configuration for security issues."""
        config = context.get("config", {})
        issues = []

        # Check for debug mode
        if config.get("debug") or config.get("DEBUG"):
            issues.append({
                "type": "debug_enabled",
                "severity": "high",
                "description": "Debug mode enabled — may expose sensitive information",
            })

        # Check for default credentials
        if config.get("password") in ("admin", "password", "default", ""):
            issues.append({
                "type": "default_credentials",
                "severity": "critical",
                "description": "Default or empty credentials detected",
            })

        # Check for permissive CORS
        cors = config.get("cors", config.get("CORS", {}))
        if cors and cors.get("origins") == "*":
            issues.append({
                "type": "permissive_cors",
                "severity": "medium",
                "description": "CORS allows all origins",
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={"config_issues": issues, "total_issues": len(issues)},
            confidence=0.85,
            reasoning=f"Found {len(issues)} configuration security issues",
        )

    def _scan_dependencies(self, context: dict[str, Any]) -> SkillResult:
        """Scan dependencies for known vulnerabilities."""
        dependencies = context.get("dependencies", [])
        findings = []

        # Known vulnerable patterns (simplified check)
        risky_patterns = {
            "pyyaml<5.4": "CVE-2020-14343 — arbitrary code execution via yaml.load()",
            "requests<2.20": "CVE-2018-18074 — session cookie exposure",
            "flask<1.0": "Multiple known vulnerabilities in old Flask versions",
            "django<3.2": "Multiple security fixes in Django 3.2+",
        }

        for dep in dependencies:
            if isinstance(dep, dict):
                name = dep.get("name", "")
                version = dep.get("version", "")
            else:
                name = str(dep)
                version = ""

            for pattern, advisory in risky_patterns.items():
                if name.lower() in pattern.lower():
                    findings.append({
                        "dependency": name,
                        "version": version,
                        "advisory": advisory,
                        "severity": "high",
                    })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "dependencies_scanned": len(dependencies),
                "findings": findings,
                "vulnerable_count": len(findings),
            },
            confidence=0.7,
            reasoning=f"Scanned {len(dependencies)} dependencies, found {len(findings)} potential issues",
        )

    def _scan_architecture(self, context: dict[str, Any]) -> SkillResult:
        """Scan architecture for security concerns."""
        components = context.get("components", [])
        concerns = []

        for component in components:
            if isinstance(component, dict):
                if component.get("exposed") and not component.get("authenticated"):
                    concerns.append({
                        "component": component.get("name", "unknown"),
                        "concern": "Exposed without authentication",
                        "severity": "high",
                    })
                if component.get("stores_secrets") and not component.get("encrypted"):
                    concerns.append({
                        "component": component.get("name", "unknown"),
                        "concern": "Stores secrets without encryption",
                        "severity": "critical",
                    })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={"architecture_concerns": concerns, "total_concerns": len(concerns)},
            confidence=0.75,
            reasoning=f"Found {len(concerns)} architectural security concerns",
        )
