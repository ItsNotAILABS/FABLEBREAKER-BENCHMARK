"""
Benchmarks Module
==================

Adversarial evaluation suites, scoring engines, and dataset generation.

Provides:
- Suite registration and discovery
- Dataset generation with deterministic seeding
- Scoring with hash-locked verification
- Multi-candidate batch evaluation
- Leaderboard generation
"""

from __future__ import annotations

from .suite import (
    BenchmarkSuite,
    SuiteRegistry,
    SuiteConfig,
)
from .scoring import (
    ScoreResult,
    ScoreEngine,
    FamilyDiagnostics,
)
from .dataset import (
    DatasetGenerator,
    DatasetCase,
    AdversarialFamily,
)
from .leaderboard import (
    LeaderboardEntry,
    Leaderboard,
)

__all__ = [
    "BenchmarkSuite",
    "SuiteRegistry",
    "SuiteConfig",
    "ScoreResult",
    "ScoreEngine",
    "FamilyDiagnostics",
    "DatasetGenerator",
    "DatasetCase",
    "AdversarialFamily",
    "LeaderboardEntry",
    "Leaderboard",
]
