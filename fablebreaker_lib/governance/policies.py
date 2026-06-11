"""
Policy definitions and enforcement engine for governance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class PolicyStatus(Enum):
    """Status of a policy."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class PolicyDecision(Enum):
    """Decision outcome from policy evaluation."""
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    CONDITIONAL = "conditional"


@dataclass
class Policy:
    """A governance policy defining allowed behavior."""
    id: str
    name: str
    description: str
    category: str
    version: str = "1.0"
    status: PolicyStatus = PolicyStatus.ACTIVE
    effective_date: str = ""
    check_fn: Callable[[dict[str, Any]], PolicyDecision] | None = None
    conditions: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)

    def evaluate(self, context: dict[str, Any]) -> PolicyDecision:
        if self.status != PolicyStatus.ACTIVE:
            return PolicyDecision.ALLOW
        if self.check_fn:
            return self.check_fn(context)
        return PolicyDecision.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "status": self.status.value,
            "effective_date": self.effective_date,
            "conditions": self.conditions,
            "exceptions": self.exceptions,
        }


class PolicySet:
    """A collection of related policies."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._policies: dict[str, Policy] = {}

    def add(self, policy: Policy) -> None:
        self._policies[policy.id] = policy

    def get(self, policy_id: str) -> Policy | None:
        return self._policies.get(policy_id)

    @property
    def policies(self) -> list[Policy]:
        return list(self._policies.values())

    @property
    def active_policies(self) -> list[Policy]:
        return [p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]

    def evaluate_all(self, context: dict[str, Any]) -> dict[str, PolicyDecision]:
        return {
            pid: policy.evaluate(context)
            for pid, policy in self._policies.items()
            if policy.status == PolicyStatus.ACTIVE
        }


class PolicyEngine:
    """Central engine for evaluating governance policies."""

    def __init__(self) -> None:
        self._policy_sets: dict[str, PolicySet] = {}

    def register_policy_set(self, policy_set: PolicySet) -> None:
        self._policy_sets[policy_set.name] = policy_set

    def evaluate(self, context: dict[str, Any], policy_set_name: str | None = None) -> dict[str, PolicyDecision]:
        """Evaluate context against policies."""
        results: dict[str, PolicyDecision] = {}
        if policy_set_name:
            ps = self._policy_sets.get(policy_set_name)
            if ps:
                results.update(ps.evaluate_all(context))
        else:
            for ps in self._policy_sets.values():
                results.update(ps.evaluate_all(context))
        return results

    def is_allowed(self, context: dict[str, Any]) -> bool:
        """Returns True if no policies deny the action."""
        results = self.evaluate(context)
        return PolicyDecision.DENY not in results.values()

    def denied_policies(self, context: dict[str, Any]) -> list[str]:
        """Get IDs of policies that deny the action."""
        results = self.evaluate(context)
        return [pid for pid, decision in results.items() if decision == PolicyDecision.DENY]

    @property
    def policy_sets(self) -> list[str]:
        return list(self._policy_sets.keys())

    def summary(self) -> dict[str, Any]:
        return {
            "total_policy_sets": len(self._policy_sets),
            "policy_sets": {
                name: {
                    "description": ps.description,
                    "total_policies": len(ps.policies),
                    "active_policies": len(ps.active_policies),
                }
                for name, ps in self._policy_sets.items()
            },
        }


# Pre-built governance policies
CERTIFICATION_POLICIES = PolicySet("certification", "Policies governing certification issuance")

CERTIFICATION_POLICIES.add(Policy(
    id="GOV-CERT-001",
    name="Mandatory Hidden Evaluation",
    description="Certification requires passing hidden-seed evaluation, not just public.",
    category="certification",
    check_fn=lambda ctx: PolicyDecision.ALLOW if ctx.get("hidden_evaluation_passed") else PolicyDecision.DENY,
    conditions=["Hidden seed evaluation must be executed and passed"],
))

CERTIFICATION_POLICIES.add(Policy(
    id="GOV-CERT-002",
    name="Zero Failure Tolerance",
    description="Any single evaluation failure disqualifies certification.",
    category="certification",
    check_fn=lambda ctx: PolicyDecision.ALLOW if ctx.get("total_failed", 1) == 0 else PolicyDecision.DENY,
    conditions=["Zero failures across all evaluation cases"],
))

CERTIFICATION_POLICIES.add(Policy(
    id="GOV-CERT-003",
    name="Evidence Pack Required",
    description="Certification must be backed by a signed evidence pack.",
    category="certification",
    check_fn=lambda ctx: PolicyDecision.ALLOW if ctx.get("evidence_signed") else PolicyDecision.DENY,
    conditions=["Evidence pack must be generated and HMAC-signed"],
))

DATA_GOVERNANCE_POLICIES = PolicySet("data_governance", "Policies for evaluation data handling")

DATA_GOVERNANCE_POLICIES.add(Policy(
    id="GOV-DATA-001",
    name="Seed Confidentiality",
    description="Hidden evaluation seeds must never be disclosed to candidates.",
    category="data",
    check_fn=lambda ctx: PolicyDecision.ALLOW if not ctx.get("seed_disclosed") else PolicyDecision.DENY,
))

DATA_GOVERNANCE_POLICIES.add(Policy(
    id="GOV-DATA-002",
    name="Dataset Integrity",
    description="Datasets must be regenerated from seed, not stored pre-computed.",
    category="data",
    check_fn=lambda ctx: PolicyDecision.ALLOW if ctx.get("generated_from_seed") else PolicyDecision.DENY,
))
