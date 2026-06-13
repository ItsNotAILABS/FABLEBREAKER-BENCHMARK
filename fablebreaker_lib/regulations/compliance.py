"""
Compliance engine for checking systems against regulatory standards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class ComplianceCheck:
    """A single compliance check against a regulatory requirement."""
    id: str
    standard_id: str
    requirement: str
    description: str
    check_fn: Callable[[dict[str, Any]], bool] | None = None
    remediation: str = ""
    article_ref: str = ""

    def evaluate(self, context: dict[str, Any]) -> bool:
        if self.check_fn:
            return self.check_fn(context)
        return True


@dataclass
class ComplianceStandard:
    """A regulatory standard composed of multiple compliance checks."""
    id: str
    name: str
    version: str
    description: str
    jurisdiction: str = "international"
    effective_date: str = ""
    checks: list[ComplianceCheck] = field(default_factory=list)

    def add_check(self, check: ComplianceCheck) -> None:
        self.checks.append(check)

    def evaluate(self, context: dict[str, Any]) -> ComplianceReport:
        results: list[dict[str, Any]] = []
        passed = 0
        failed = 0
        for check in self.checks:
            result = check.evaluate(context)
            if result:
                passed += 1
            else:
                failed += 1
            results.append({
                "check_id": check.id,
                "requirement": check.requirement,
                "passed": result,
                "article_ref": check.article_ref,
                "remediation": check.remediation if not result else "",
            })
        return ComplianceReport(
            standard_id=self.id,
            standard_name=self.name,
            total_checks=len(self.checks),
            passed=passed,
            failed=failed,
            compliant=failed == 0,
            results=results,
        )


@dataclass
class ComplianceReport:
    """Result of evaluating a system against a compliance standard."""
    standard_id: str
    standard_name: str
    total_checks: int
    passed: int
    failed: int
    compliant: bool
    results: list[dict[str, Any]] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    @property
    def compliance_rate(self) -> float:
        return self.passed / self.total_checks if self.total_checks > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard_id": self.standard_id,
            "standard_name": self.standard_name,
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "compliant": self.compliant,
            "compliance_rate": self.compliance_rate,
            "results": self.results,
            "timestamp_utc": self.timestamp_utc,
        }


class ComplianceEngine:
    """Central engine for evaluating systems against multiple regulatory standards."""

    def __init__(self) -> None:
        self._standards: dict[str, ComplianceStandard] = {}

    def register_standard(self, standard: ComplianceStandard) -> None:
        self._standards[standard.id] = standard

    def evaluate(self, context: dict[str, Any], standard_id: str | None = None) -> list[ComplianceReport]:
        """Evaluate context against standards."""
        reports: list[ComplianceReport] = []
        if standard_id:
            std = self._standards.get(standard_id)
            if std:
                reports.append(std.evaluate(context))
        else:
            for std in self._standards.values():
                reports.append(std.evaluate(context))
        return reports

    def is_compliant(self, context: dict[str, Any], standard_id: str | None = None) -> bool:
        """Returns True if all relevant standards are satisfied."""
        reports = self.evaluate(context, standard_id)
        return all(r.compliant for r in reports)

    @property
    def standards(self) -> list[str]:
        return list(self._standards.keys())

    def summary(self) -> dict[str, Any]:
        return {
            "registered_standards": len(self._standards),
            "standards": {
                sid: {"name": s.name, "checks": len(s.checks), "jurisdiction": s.jurisdiction}
                for sid, s in self._standards.items()
            },
        }
