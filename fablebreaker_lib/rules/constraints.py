"""
Constraint definitions for benchmark evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Constraint:
    """Base constraint that must be satisfied during evaluation."""
    id: str
    name: str
    description: str
    hard: bool = True  # Hard constraints disqualify; soft constraints warn

    def check(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Check if constraint is satisfied. Returns (satisfied, message)."""
        return True, ""


@dataclass
class TimeConstraint(Constraint):
    """Constraint on execution time."""
    max_seconds: float = 300.0

    def check(self, context: dict[str, Any]) -> tuple[bool, str]:
        elapsed = context.get("elapsed_seconds", 0)
        if elapsed > self.max_seconds:
            return False, f"Exceeded time limit: {elapsed:.2f}s > {self.max_seconds}s"
        return True, ""


@dataclass
class ResourceConstraint(Constraint):
    """Constraint on computational resources."""
    max_steps: int = 2_000_000
    max_memory_mb: int = 1024
    max_depth: int = 10_000

    def check(self, context: dict[str, Any]) -> tuple[bool, str]:
        steps = context.get("steps", 0)
        if steps > self.max_steps:
            return False, f"Exceeded step budget: {steps} > {self.max_steps}"
        depth = context.get("max_depth", 0)
        if depth > self.max_depth:
            return False, f"Exceeded depth limit: {depth} > {self.max_depth}"
        return True, ""


@dataclass
class CorrectnessConstraint(Constraint):
    """Constraint requiring hash-perfect correctness."""
    zero_tolerance: bool = True

    def check(self, context: dict[str, Any]) -> tuple[bool, str]:
        failures = context.get("failures", 0)
        if self.zero_tolerance and failures > 0:
            return False, f"Correctness violation: {failures} failures (zero tolerance)"
        return True, ""


@dataclass
class IntegrityConstraint(Constraint):
    """Constraint on cryptographic integrity of outputs."""

    def check(self, context: dict[str, Any]) -> tuple[bool, str]:
        hash_verified = context.get("hash_verified", False)
        if not hash_verified:
            return False, "Output hash verification failed"
        signature_valid = context.get("signature_valid", True)
        if not signature_valid:
            return False, "Evidence signature verification failed"
        return True, ""


class ConstraintSet:
    """A named collection of constraints applied together."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._constraints: list[Constraint] = []

    def add(self, constraint: Constraint) -> None:
        self._constraints.append(constraint)

    def check_all(self, context: dict[str, Any]) -> list[tuple[Constraint, bool, str]]:
        """Check all constraints. Returns list of (constraint, satisfied, message)."""
        results = []
        for constraint in self._constraints:
            satisfied, message = constraint.check(context)
            results.append((constraint, satisfied, message))
        return results

    def is_satisfied(self, context: dict[str, Any]) -> bool:
        """Returns True only if all hard constraints are satisfied."""
        for constraint in self._constraints:
            if constraint.hard:
                satisfied, _ = constraint.check(context)
                if not satisfied:
                    return False
        return True

    @property
    def constraints(self) -> list[Constraint]:
        return list(self._constraints)


# Pre-built constraint sets
STANDARD_CONSTRAINTS = ConstraintSet(
    name="standard",
    description="Standard evaluation constraints for FableBreaker benchmarks",
)
STANDARD_CONSTRAINTS.add(TimeConstraint(
    id="CON-001", name="Time Limit", description="300 second evaluation limit",
))
STANDARD_CONSTRAINTS.add(ResourceConstraint(
    id="CON-002", name="Resource Budget", description="2M step budget",
))
STANDARD_CONSTRAINTS.add(CorrectnessConstraint(
    id="CON-003", name="Zero Tolerance", description="Zero failures allowed",
))
STANDARD_CONSTRAINTS.add(IntegrityConstraint(
    id="CON-004", name="Integrity", description="Hash integrity required",
))
