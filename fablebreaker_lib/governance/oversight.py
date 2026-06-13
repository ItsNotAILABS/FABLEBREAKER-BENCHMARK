"""
Oversight structures: review boards, escalation, and oversight actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EscalationLevel(Enum):
    """Levels of escalation in oversight."""
    AUTOMATED = "automated"
    REVIEWER = "reviewer"
    BOARD = "board"
    EXECUTIVE = "executive"


class ReviewDecision(Enum):
    """Decisions from oversight review."""
    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"


@dataclass
class OversightAction:
    """An action taken by the oversight system."""
    id: str
    action_type: str
    actor: str
    target: str
    decision: ReviewDecision
    reason: str = ""
    escalation_level: EscalationLevel = EscalationLevel.AUTOMATED
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "actor": self.actor,
            "target": self.target,
            "decision": self.decision.value,
            "reason": self.reason,
            "escalation_level": self.escalation_level.value,
            "timestamp_utc": self.timestamp_utc,
            "metadata": self.metadata,
        }


class OversightBoard:
    """A governance oversight board that reviews and decides on actions."""

    def __init__(self, board_id: str, name: str, members: list[str] | None = None) -> None:
        self.board_id = board_id
        self.name = name
        self.members = members or []
        self._actions: list[OversightAction] = []
        self._escalation_rules: dict[str, EscalationLevel] = {}

    def add_member(self, member: str) -> None:
        if member not in self.members:
            self.members.append(member)

    def set_escalation_rule(self, trigger: str, level: EscalationLevel) -> None:
        self._escalation_rules[trigger] = level

    def record_action(self, action: OversightAction) -> None:
        self._actions.append(action)

    def review(
        self,
        action_type: str,
        target: str,
        context: dict[str, Any],
        reviewer: str = "system",
    ) -> OversightAction:
        """Perform oversight review and return action."""
        # Determine escalation level
        level = self._escalation_rules.get(action_type, EscalationLevel.AUTOMATED)

        # Auto-approve for automated level with passing context
        if level == EscalationLevel.AUTOMATED and context.get("all_checks_passed", False):
            decision = ReviewDecision.APPROVE
            reason = "Automated approval: all checks passed"
        elif context.get("critical_failure", False):
            decision = ReviewDecision.REJECT
            reason = f"Critical failure detected: {context.get('failure_reason', 'unknown')}"
        else:
            decision = ReviewDecision.DEFER
            reason = "Requires human review"

        action = OversightAction(
            id=f"OA-{len(self._actions) + 1:04d}",
            action_type=action_type,
            actor=reviewer,
            target=target,
            decision=decision,
            reason=reason,
            escalation_level=level,
        )
        self._actions.append(action)
        return action

    @property
    def actions(self) -> list[OversightAction]:
        return list(self._actions)

    def summary(self) -> dict[str, Any]:
        return {
            "board_id": self.board_id,
            "name": self.name,
            "members": self.members,
            "total_actions": len(self._actions),
            "approvals": sum(1 for a in self._actions if a.decision == ReviewDecision.APPROVE),
            "rejections": sum(1 for a in self._actions if a.decision == ReviewDecision.REJECT),
            "pending": sum(1 for a in self._actions if a.decision == ReviewDecision.DEFER),
        }
