"""
Audit framework for regulatory compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class AuditSeverity(Enum):
    """Severity of audit findings."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    OBSERVATION = "observation"


@dataclass
class AuditCheck:
    """A single audit check in the framework."""
    id: str
    category: str
    title: str
    description: str
    check_fn: Callable[[dict[str, Any]], tuple[bool, str]] | None = None
    severity: AuditSeverity = AuditSeverity.MAJOR
    standard_ref: str = ""

    def execute(self, context: dict[str, Any]) -> tuple[bool, str]:
        if self.check_fn:
            return self.check_fn(context)
        return True, "No automated check defined"


@dataclass
class AuditReport:
    """Complete audit report."""
    framework_name: str
    target_system: str
    auditor: str = "automated"
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    findings: list[dict[str, Any]] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total_checks if self.total_checks > 0 else 0.0

    @property
    def clean(self) -> bool:
        return self.failed == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework_name": self.framework_name,
            "target_system": self.target_system,
            "auditor": self.auditor,
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "clean": self.clean,
            "findings": self.findings,
            "timestamp_utc": self.timestamp_utc,
        }


class AuditFramework:
    """A complete audit framework with checks and reporting."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._checks: list[AuditCheck] = []

    def add_check(self, check: AuditCheck) -> None:
        self._checks.append(check)

    def audit(self, target_system: str, context: dict[str, Any], auditor: str = "automated") -> AuditReport:
        """Execute all audit checks and generate report."""
        findings: list[dict[str, Any]] = []
        passed = 0
        failed = 0

        for check in self._checks:
            result, message = check.execute(context)
            if result:
                passed += 1
            else:
                failed += 1
                findings.append({
                    "check_id": check.id,
                    "category": check.category,
                    "title": check.title,
                    "severity": check.severity.value,
                    "message": message,
                    "standard_ref": check.standard_ref,
                })

        return AuditReport(
            framework_name=self.name,
            target_system=target_system,
            auditor=auditor,
            total_checks=len(self._checks),
            passed=passed,
            failed=failed,
            findings=findings,
        )

    @property
    def checks(self) -> list[AuditCheck]:
        return list(self._checks)
