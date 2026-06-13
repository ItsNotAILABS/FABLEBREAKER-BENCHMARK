"""
Base classes and data structures used across the entire library.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Severity(Enum):
    """Severity levels for findings and violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """A single finding from any evaluation, audit, or governance check."""
    id: str
    severity: Severity
    category: str
    title: str
    description: str
    source_module: str
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "source_module": self.source_module,
            "evidence": self.evidence,
            "timestamp_utc": self.timestamp_utc,
            "remediation": self.remediation,
        }


@dataclass
class AuditTrail:
    """Immutable record of actions taken during an evaluation or governance process."""
    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: str, actor: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "action": action,
            "actor": actor,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "details": details or {},
        }
        self.entries.append(entry)

    def hash_chain(self) -> str:
        payload = json.dumps(self.entries, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": self.entries,
            "chain_hash": self.hash_chain(),
            "total_entries": len(self.entries),
        }


@dataclass
class EvaluationContext:
    """Context for running an evaluation, carrying configuration and state."""
    suite_id: str
    seed: int
    candidate_name: str
    operator: str = "system"
    max_steps: int = 2_000_000
    timeout_seconds: float = 300.0
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_trail: AuditTrail = field(default_factory=AuditTrail)

    def record_action(self, action: str, details: dict[str, Any] | None = None) -> None:
        self.audit_trail.record(action, self.operator, details)


@dataclass
class CertificationResult:
    """The outcome of a certification process."""
    certified: bool
    candidate_name: str
    suite_id: str
    speedup: float = 0.0
    total_cases: int = 0
    total_correct: int = 0
    total_failed: int = 0
    findings: list[Finding] = field(default_factory=list)
    evidence_hash: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.total_correct / self.total_cases

    def to_dict(self) -> dict[str, Any]:
        return {
            "certified": self.certified,
            "candidate_name": self.candidate_name,
            "suite_id": self.suite_id,
            "speedup": self.speedup,
            "total_cases": self.total_cases,
            "total_correct": self.total_correct,
            "total_failed": self.total_failed,
            "pass_rate": self.pass_rate,
            "findings": [f.to_dict() for f in self.findings],
            "evidence_hash": self.evidence_hash,
            "timestamp_utc": self.timestamp_utc,
        }
