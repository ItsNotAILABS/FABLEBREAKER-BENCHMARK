"""
Rule engine for evaluating compliance with benchmark and governance rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class Enforcement(Enum):
    """What happens when a rule is violated."""
    DISQUALIFY = "disqualify"
    PENALIZE = "penalize"
    WARN = "warn"
    LOG = "log"


@dataclass(frozen=True)
class Rule:
    """A single enforceable rule in the evaluation framework."""
    id: str
    name: str
    description: str
    enforcement: Enforcement = Enforcement.DISQUALIFY
    category: str = "general"
    check_fn: Callable[[dict[str, Any]], bool] | None = None

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Returns True if the rule is satisfied."""
        if self.check_fn:
            return self.check_fn(context)
        return True


@dataclass
class RuleViolation:
    """Records a rule violation."""
    rule: Rule
    context: dict[str, Any]
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule.id,
            "rule_name": self.rule.name,
            "enforcement": self.rule.enforcement.value,
            "category": self.rule.category,
            "message": self.message,
            "evidence": self.evidence,
        }


class RuleSet:
    """A collection of related rules."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._rules: dict[str, Rule] = {}

    def add(self, rule: Rule) -> None:
        self._rules[rule.id] = rule

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    @property
    def rules(self) -> list[Rule]:
        return list(self._rules.values())

    def evaluate_all(self, context: dict[str, Any]) -> list[RuleViolation]:
        violations: list[RuleViolation] = []
        for rule in self._rules.values():
            if not rule.evaluate(context):
                violations.append(RuleViolation(
                    rule=rule,
                    context=context,
                    message=f"Rule '{rule.name}' violated",
                ))
        return violations


class RuleEngine:
    """Central engine for registering and evaluating rule sets."""

    def __init__(self) -> None:
        self._rule_sets: dict[str, RuleSet] = {}

    def register_rule_set(self, rule_set: RuleSet) -> None:
        self._rule_sets[rule_set.name] = rule_set

    def evaluate(self, context: dict[str, Any], rule_set_name: str | None = None) -> list[RuleViolation]:
        """Evaluate context against rules. If rule_set_name is None, evaluate all."""
        violations: list[RuleViolation] = []
        if rule_set_name:
            rs = self._rule_sets.get(rule_set_name)
            if rs:
                violations.extend(rs.evaluate_all(context))
        else:
            for rs in self._rule_sets.values():
                violations.extend(rs.evaluate_all(context))
        return violations

    def is_compliant(self, context: dict[str, Any], rule_set_name: str | None = None) -> bool:
        """Returns True if no disqualifying violations found."""
        violations = self.evaluate(context, rule_set_name)
        return not any(v.rule.enforcement == Enforcement.DISQUALIFY for v in violations)

    @property
    def rule_sets(self) -> list[str]:
        return list(self._rule_sets.keys())

    def summary(self) -> dict[str, Any]:
        return {
            "total_rule_sets": len(self._rule_sets),
            "rule_sets": {
                name: {
                    "description": rs.description,
                    "rule_count": len(rs.rules),
                }
                for name, rs in self._rule_sets.items()
            },
        }


# Pre-built evaluation rules
HASH_CORRECTNESS_RULE = Rule(
    id="RULE-001",
    name="Hash Correctness",
    description="Candidate output must SHA-256 match the reference output.",
    enforcement=Enforcement.DISQUALIFY,
    category="correctness",
    check_fn=lambda ctx: ctx.get("hash_match", False),
)

STEP_BUDGET_RULE = Rule(
    id="RULE-002",
    name="Step Budget",
    description="Evaluation must complete within the step budget.",
    enforcement=Enforcement.DISQUALIFY,
    category="resource",
    check_fn=lambda ctx: ctx.get("steps", 0) <= ctx.get("max_steps", 2_000_000),
)

DETERMINISM_RULE = Rule(
    id="RULE-003",
    name="Deterministic Output",
    description="Repeated evaluations must produce identical outputs.",
    enforcement=Enforcement.DISQUALIFY,
    category="correctness",
    check_fn=lambda ctx: ctx.get("deterministic", True),
)

NO_SIDE_EFFECTS_RULE = Rule(
    id="RULE-004",
    name="No Side Effects",
    description="Candidate must not perform I/O, network, or filesystem operations.",
    enforcement=Enforcement.DISQUALIFY,
    category="safety",
)

TIMEOUT_RULE = Rule(
    id="RULE-005",
    name="Timeout Compliance",
    description="Candidate must complete evaluation within the time limit.",
    enforcement=Enforcement.DISQUALIFY,
    category="resource",
    check_fn=lambda ctx: ctx.get("elapsed_seconds", 0) <= ctx.get("timeout_seconds", 300),
)
