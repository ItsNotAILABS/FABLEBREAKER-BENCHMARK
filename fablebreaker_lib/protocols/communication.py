"""
Communication protocols for inter-system messaging.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Types of protocol messages."""
    SUBMISSION = "submission"
    EVALUATION_START = "evaluation_start"
    EVALUATION_COMPLETE = "evaluation_complete"
    CERTIFICATION_ISSUED = "certification_issued"
    CERTIFICATION_REVOKED = "certification_revoked"
    REGRESSION_DETECTED = "regression_detected"
    GOVERNANCE_ACTION = "governance_action"
    AUDIT_REQUEST = "audit_request"
    AUDIT_RESPONSE = "audit_response"
    HEALTH_CHECK = "health_check"


@dataclass
class ProtocolMessage:
    """A structured message in the communication protocol."""
    id: str
    message_type: MessageType
    sender: str
    recipient: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    correlation_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "timestamp_utc": self.timestamp_utc,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


class ProtocolChannel:
    """A message channel for protocol communication."""

    def __init__(self, channel_id: str) -> None:
        self.channel_id = channel_id
        self._messages: list[ProtocolMessage] = []
        self._subscribers: list[str] = []

    def send(self, message: ProtocolMessage) -> None:
        self._messages.append(message)

    def subscribe(self, subscriber_id: str) -> None:
        if subscriber_id not in self._subscribers:
            self._subscribers.append(subscriber_id)

    def messages_for(self, recipient: str) -> list[ProtocolMessage]:
        return [m for m in self._messages if m.recipient == recipient]

    def messages_by_type(self, msg_type: MessageType) -> list[ProtocolMessage]:
        return [m for m in self._messages if m.message_type == msg_type]

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "message_count": self.message_count,
            "subscribers": self._subscribers,
        }
