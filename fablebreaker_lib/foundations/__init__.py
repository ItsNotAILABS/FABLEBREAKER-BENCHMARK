"""
Foundations Module
==================

Core principles, axioms, and base abstractions that underpin the entire
FableBreaker evaluation framework.

This module defines the fundamental invariants that all other modules depend on:
- Correctness before speed
- Reproducibility guarantees
- Cryptographic integrity
- Adversarial robustness
- Semantic preservation
"""

from .axioms import (
    Axiom,
    CORRECTNESS_FIRST,
    REPRODUCIBILITY,
    CRYPTOGRAPHIC_INTEGRITY,
    ADVERSARIAL_ROBUSTNESS,
    SEMANTIC_PRESERVATION,
    TRANSPARENCY,
    NON_REPUDIATION,
    ALL_AXIOMS,
)
from .base import (
    EvaluationContext,
    CertificationResult,
    Severity,
    Finding,
    AuditTrail,
)
from .integrity import (
    ContentHasher,
    HashChain,
    IntegrityEnvelope,
)

__all__ = [
    "Axiom",
    "CORRECTNESS_FIRST",
    "REPRODUCIBILITY",
    "CRYPTOGRAPHIC_INTEGRITY",
    "ADVERSARIAL_ROBUSTNESS",
    "SEMANTIC_PRESERVATION",
    "TRANSPARENCY",
    "NON_REPUDIATION",
    "ALL_AXIOMS",
    "EvaluationContext",
    "CertificationResult",
    "Severity",
    "Finding",
    "AuditTrail",
    "ContentHasher",
    "HashChain",
    "IntegrityEnvelope",
]
