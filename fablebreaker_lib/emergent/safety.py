"""
Safety boundaries and envelope enforcement for emergent behavior containment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SafetyBoundary:
    """A safety boundary that must not be crossed."""
    id: str
    name: str
    description: str
    metric: str
    min_value: float | None = None
    max_value: float | None = None
    hard_limit: bool = True

    def check(self, value: float) -> tuple[bool, str]:
        """Check if value is within boundary. Returns (within_bounds, message)."""
        if self.min_value is not None and value < self.min_value:
            return False, f"{self.name}: {value} below minimum {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"{self.name}: {value} exceeds maximum {self.max_value}"
        return True, ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metric": self.metric,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "hard_limit": self.hard_limit,
        }


@dataclass
class BoundaryViolation:
    """Record of a safety boundary violation."""
    boundary: SafetyBoundary
    actual_value: float
    candidate_name: str
    message: str
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_id": self.boundary.id,
            "boundary_name": self.boundary.name,
            "metric": self.boundary.metric,
            "actual_value": self.actual_value,
            "candidate_name": self.candidate_name,
            "message": self.message,
            "hard_limit": self.boundary.hard_limit,
            "timestamp_utc": self.timestamp_utc,
        }


class SafetyEnvelope:
    """A collection of safety boundaries forming a safe operating envelope."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._boundaries: list[SafetyBoundary] = []

    def add_boundary(self, boundary: SafetyBoundary) -> None:
        self._boundaries.append(boundary)

    def check(self, metrics: dict[str, float], candidate_name: str = "") -> list[BoundaryViolation]:
        """Check all boundaries against provided metrics."""
        violations: list[BoundaryViolation] = []
        for boundary in self._boundaries:
            if boundary.metric in metrics:
                within, message = boundary.check(metrics[boundary.metric])
                if not within:
                    violations.append(BoundaryViolation(
                        boundary=boundary,
                        actual_value=metrics[boundary.metric],
                        candidate_name=candidate_name,
                        message=message,
                    ))
        return violations

    def is_safe(self, metrics: dict[str, float]) -> bool:
        """Check if metrics are within all hard boundaries."""
        violations = self.check(metrics)
        return not any(v.boundary.hard_limit for v in violations)

    @property
    def boundaries(self) -> list[SafetyBoundary]:
        return list(self._boundaries)


class SafetyMonitor:
    """Monitors safety boundaries across all candidates."""

    def __init__(self) -> None:
        self._envelopes: dict[str, SafetyEnvelope] = {}
        self._violations: list[BoundaryViolation] = []

    def register_envelope(self, envelope: SafetyEnvelope) -> None:
        self._envelopes[envelope.name] = envelope

    def check_candidate(self, candidate_name: str, metrics: dict[str, float]) -> list[BoundaryViolation]:
        """Check candidate against all safety envelopes."""
        all_violations: list[BoundaryViolation] = []
        for envelope in self._envelopes.values():
            violations = envelope.check(metrics, candidate_name)
            all_violations.extend(violations)
            self._violations.extend(violations)
        return all_violations

    def is_safe(self, candidate_name: str, metrics: dict[str, float]) -> bool:
        violations = self.check_candidate(candidate_name, metrics)
        return not any(v.boundary.hard_limit for v in violations)

    @property
    def all_violations(self) -> list[BoundaryViolation]:
        return list(self._violations)

    def summary(self) -> dict[str, Any]:
        return {
            "envelopes": list(self._envelopes.keys()),
            "total_violations": len(self._violations),
            "hard_violations": sum(1 for v in self._violations if v.boundary.hard_limit),
        }


# Pre-built safety envelope for FableBreaker evaluations
EVALUATION_SAFETY_ENVELOPE = SafetyEnvelope("evaluation")
EVALUATION_SAFETY_ENVELOPE.add_boundary(SafetyBoundary(
    id="SB-001", name="Step Budget", description="Maximum evaluation steps",
    metric="steps", max_value=2_000_000, hard_limit=True,
))
EVALUATION_SAFETY_ENVELOPE.add_boundary(SafetyBoundary(
    id="SB-002", name="Time Limit", description="Maximum evaluation time",
    metric="elapsed_seconds", max_value=300.0, hard_limit=True,
))
EVALUATION_SAFETY_ENVELOPE.add_boundary(SafetyBoundary(
    id="SB-003", name="Recursion Depth", description="Maximum recursion depth",
    metric="max_depth", max_value=10_000, hard_limit=True,
))
EVALUATION_SAFETY_ENVELOPE.add_boundary(SafetyBoundary(
    id="SB-004", name="Memory Usage", description="Maximum memory in MB",
    metric="memory_mb", max_value=1024, hard_limit=True,
))
