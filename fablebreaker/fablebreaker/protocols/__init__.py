"""FableBreaker Protocol SDK.

Programmatic interfaces implementing the methodologies described in the
FableBreaker Research Journal (14 papers across 5 journals).

Foundation reference:
    Medina, F. (2026). FableBreaker: A Reproducible Benchmark for
    Semantic-Preserving Evaluator Optimization.
    https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

from .overflow_corridors import OverflowCorridorProtocol
from .conditional_cascades import ConditionalCascadeProtocol
from .governance_certification import GovernanceCertificationProtocol
from .per_family_scoring import PerFamilyScoringProtocol
from .api_reproducibility import APIReproducibilityProtocol
from .foundation import FOUNDATION_DOI, FOUNDATION_CITATION, ProtocolRegistry

__all__ = [
    "OverflowCorridorProtocol",
    "ConditionalCascadeProtocol",
    "GovernanceCertificationProtocol",
    "PerFamilyScoringProtocol",
    "APIReproducibilityProtocol",
    "ProtocolRegistry",
    "FOUNDATION_DOI",
    "FOUNDATION_CITATION",
]
