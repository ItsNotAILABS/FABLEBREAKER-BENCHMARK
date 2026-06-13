"""
Accountability structures: responsibility tracking and incident management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ResponsibleParty:
    """A party accountable for system behavior."""
    id: str
    name: str
    role: str
    scope: str
    contact: str = ""
    escalation_target: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "scope": self.scope,
            "contact": self.contact,
            "escalation_target": self.escalation_target,
        }


@dataclass
class IncidentReport:
    """Report of a governance or safety incident."""
    id: str
    title: str
    severity: str
    category: str
    description: str
    affected_candidates: list[str] = field(default_factory=list)
    root_cause: str = ""
    remediation: str = ""
    status: str = "open"
    responsible_party: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    resolved_at: str = ""

    def resolve(self, resolution: str) -> None:
        self.status = "resolved"
        self.remediation = resolution
        self.resolved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "affected_candidates": self.affected_candidates,
            "root_cause": self.root_cause,
            "remediation": self.remediation,
            "status": self.status,
            "responsible_party": self.responsible_party,
            "timestamp_utc": self.timestamp_utc,
            "resolved_at": self.resolved_at,
        }


@dataclass
class AccountabilityRecord:
    """A single record in the accountability chain."""
    action: str
    actor: str
    target: str
    outcome: str
    justification: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "outcome": self.outcome,
            "justification": self.justification,
            "timestamp_utc": self.timestamp_utc,
        }


class AccountabilityChain:
    """Immutable chain of accountability records."""

    def __init__(self) -> None:
        self._records: list[AccountabilityRecord] = []
        self._parties: dict[str, ResponsibleParty] = {}

    def register_party(self, party: ResponsibleParty) -> None:
        self._parties[party.id] = party

    def record(
        self,
        action: str,
        actor: str,
        target: str,
        outcome: str,
        justification: str = "",
    ) -> AccountabilityRecord:
        record = AccountabilityRecord(
            action=action,
            actor=actor,
            target=target,
            outcome=outcome,
            justification=justification,
        )
        self._records.append(record)
        return record

    def records_for(self, actor: str) -> list[AccountabilityRecord]:
        return [r for r in self._records if r.actor == actor]

    def records_affecting(self, target: str) -> list[AccountabilityRecord]:
        return [r for r in self._records if r.target == target]

    @property
    def all_records(self) -> list[AccountabilityRecord]:
        return list(self._records)

    @property
    def parties(self) -> list[ResponsibleParty]:
        return list(self._parties.values())

    def summary(self) -> dict[str, Any]:
        return {
            "total_records": len(self._records),
            "registered_parties": len(self._parties),
            "parties": {pid: p.to_dict() for pid, p in self._parties.items()},
            "recent_actions": [r.to_dict() for r in self._records[-10:]],
        }
