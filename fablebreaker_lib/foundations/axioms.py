"""
Core axioms that define the foundational principles of the FableBreaker system.

Every component in the library must uphold these axioms. Violation of any axiom
invalidates the evaluation, certification, or governance action in question.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Axiom:
    """An immutable foundational principle of the evaluation framework."""

    id: str
    name: str
    statement: str
    implications: tuple[str, ...] = field(default_factory=tuple)
    enforceable: bool = True

    def check(self, context: dict[str, Any]) -> bool:
        """Verify that this axiom holds in the given context.

        Submodules override this with domain-specific checks.
        Base implementation always returns True (axiom assumed held).
        """
        return True

    def __str__(self) -> str:
        return f"[{self.id}] {self.name}: {self.statement}"


CORRECTNESS_FIRST = Axiom(
    id="AX-001",
    name="Correctness Before Speed",
    statement=(
        "No optimization claim is valid without hash-verified "
        "semantic equivalence across all evaluation cases."
    ),
    implications=(
        "A single incorrect output disqualifies the entire submission.",
        "Speed measurements are only reported for fully correct candidates.",
        "Partial correctness receives zero certification.",
    ),
)

REPRODUCIBILITY = Axiom(
    id="AX-002",
    name="Reproducibility Guaranteed",
    statement=(
        "Identical seed values must produce identical datasets and "
        "evaluation outcomes on any conforming platform."
    ),
    implications=(
        "Deterministic RNG seeding is mandatory.",
        "Platform-dependent behavior is a disqualifying defect.",
        "Floating-point operations must be avoided or canonicalized.",
    ),
)

CRYPTOGRAPHIC_INTEGRITY = Axiom(
    id="AX-003",
    name="Cryptographic Integrity",
    statement=(
        "SHA-256 hash locking prevents output forgery and ensures "
        "non-repudiation of evaluation results."
    ),
    implications=(
        "Every output is canonicalized before hashing.",
        "Hash mismatches are treated as evaluation failures.",
        "Evidence packs are HMAC-signed for tamper detection.",
    ),
)

ADVERSARIAL_ROBUSTNESS = Axiom(
    id="AX-004",
    name="Adversarial by Default",
    statement=(
        "Hidden seeds, erasure traps, deep nesting, and overflow cases "
        "are standard components of every evaluation suite."
    ),
    implications=(
        "Candidates must handle pathological inputs gracefully.",
        "Benchmark difficulty scales adversarially with candidate claims.",
        "Public datasets are insufficient for certification.",
    ),
)

SEMANTIC_PRESERVATION = Axiom(
    id="AX-005",
    name="Semantic Preservation",
    statement=(
        "Optimized evaluators must produce bit-identical outputs to the "
        "reference implementation for all valid inputs."
    ),
    implications=(
        "Approximate results are never acceptable.",
        "Observational equivalence is verified via canonical hashing.",
        "Edge cases receive equal verification weight.",
    ),
)

TRANSPARENCY = Axiom(
    id="AX-006",
    name="Transparency of Method",
    statement=(
        "Generator, scorer, and reference evaluator are open source "
        "and auditable by any party."
    ),
    implications=(
        "No security-through-obscurity in the evaluation pipeline.",
        "All certification criteria are publicly documented.",
        "Hidden seeds are secret; the method of generation is not.",
    ),
)

NON_REPUDIATION = Axiom(
    id="AX-007",
    name="Non-Repudiation",
    statement=(
        "Once an evidence pack is generated and signed, neither the "
        "evaluator nor the candidate can deny the recorded outcome."
    ),
    implications=(
        "Timestamps are cryptographically bound to results.",
        "Evidence packs include content hashes of all inputs.",
        "Signature verification is deterministic and public.",
    ),
)

ALL_AXIOMS = (
    CORRECTNESS_FIRST,
    REPRODUCIBILITY,
    CRYPTOGRAPHIC_INTEGRITY,
    ADVERSARIAL_ROBUSTNESS,
    SEMANTIC_PRESERVATION,
    TRANSPARENCY,
    NON_REPUDIATION,
)
