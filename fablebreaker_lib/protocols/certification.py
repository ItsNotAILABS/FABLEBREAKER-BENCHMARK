"""
Certification protocol: lifecycle management for candidate certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CertificationPhase(Enum):
    """Phases in the certification lifecycle."""
    SUBMITTED = "submitted"
    PUBLIC_EVALUATION = "public_evaluation"
    HIDDEN_EVALUATION = "hidden_evaluation"
    VERIFICATION = "verification"
    CERTIFIED = "certified"
    REJECTED = "rejected"
    REVOKED = "revoked"


class CertificationOutcome(Enum):
    """Possible outcomes of certification."""
    PASS = "pass"
    FAIL_CORRECTNESS = "fail_correctness"
    FAIL_TIMEOUT = "fail_timeout"
    FAIL_INTEGRITY = "fail_integrity"
    FAIL_REGRESSION = "fail_regression"
    REVOKED = "revoked"


@dataclass
class EvidencePack:
    """A cryptographically sealed evidence package."""
    suite_id: str
    candidate_name: str
    candidate_source_ref: str
    public_score: dict[str, Any]
    hidden_score: dict[str, Any]
    public_seed: int
    hidden_seed_commitment: str
    overall_certified: bool = False
    overall_speedup: float = 0.0
    total_cases: int = 0
    total_correct: int = 0
    total_failed: int = 0
    content_hash: str = ""
    signature: str = ""
    signature_method: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "candidate_name": self.candidate_name,
            "candidate_source_ref": self.candidate_source_ref,
            "public_score": self.public_score,
            "hidden_score": self.hidden_score,
            "public_seed": self.public_seed,
            "hidden_seed_commitment": self.hidden_seed_commitment,
            "overall_certified": self.overall_certified,
            "overall_speedup": self.overall_speedup,
            "total_cases": self.total_cases,
            "total_correct": self.total_correct,
            "total_failed": self.total_failed,
            "content_hash": self.content_hash,
            "signature": self.signature,
            "signature_method": self.signature_method,
            "timestamp_utc": self.timestamp_utc,
            "notes": self.notes,
        }


class CertificationProtocol:
    """Manages the certification lifecycle for candidates.

    Protocol steps:
    1. Candidate submission
    2. Public dataset evaluation (known cases)
    3. Hidden dataset evaluation (secret-seed cases)
    4. Hash verification of all outputs
    5. Performance measurement (only if correct)
    6. Evidence pack generation and signing
    7. Certification decision
    """

    def __init__(self, suite_id: str, public_seed: int = 823, hidden_seed: int = 1701) -> None:
        self.suite_id = suite_id
        self.public_seed = public_seed
        self.hidden_seed = hidden_seed
        self._candidates: dict[str, CertificationPhase] = {}
        self._evidence: dict[str, EvidencePack] = {}

    def submit(self, candidate_name: str) -> CertificationPhase:
        """Submit a candidate for certification."""
        self._candidates[candidate_name] = CertificationPhase.SUBMITTED
        return CertificationPhase.SUBMITTED

    def advance(self, candidate_name: str, phase: CertificationPhase) -> None:
        """Move candidate to next phase."""
        self._candidates[candidate_name] = phase

    def get_phase(self, candidate_name: str) -> CertificationPhase | None:
        return self._candidates.get(candidate_name)

    def certify(self, candidate_name: str, evidence: EvidencePack) -> CertificationOutcome:
        """Issue certification decision based on evidence."""
        self._evidence[candidate_name] = evidence
        if evidence.overall_certified:
            self._candidates[candidate_name] = CertificationPhase.CERTIFIED
            return CertificationOutcome.PASS
        if evidence.total_failed > 0:
            self._candidates[candidate_name] = CertificationPhase.REJECTED
            return CertificationOutcome.FAIL_CORRECTNESS
        self._candidates[candidate_name] = CertificationPhase.REJECTED
        return CertificationOutcome.FAIL_INTEGRITY

    def revoke(self, candidate_name: str, reason: str = "") -> None:
        """Revoke a previously issued certification."""
        self._candidates[candidate_name] = CertificationPhase.REVOKED

    def get_evidence(self, candidate_name: str) -> EvidencePack | None:
        return self._evidence.get(candidate_name)

    def summary(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "total_candidates": len(self._candidates),
            "certified": sum(1 for p in self._candidates.values() if p == CertificationPhase.CERTIFIED),
            "rejected": sum(1 for p in self._candidates.values() if p == CertificationPhase.REJECTED),
            "in_progress": sum(1 for p in self._candidates.values() if p not in (CertificationPhase.CERTIFIED, CertificationPhase.REJECTED, CertificationPhase.REVOKED)),
            "candidates": {name: phase.value for name, phase in self._candidates.items()},
        }
