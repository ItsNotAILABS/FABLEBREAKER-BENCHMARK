"""Foundation paper reference and protocol registry.

This module provides the canonical citation for the FableBreaker benchmark
system and a registry that maps each journal paper to its corresponding
SDK protocol implementation.

Foundation paper:
    Medina, F. (2026). FableBreaker: A Reproducible Benchmark for
    Semantic-Preserving Evaluator Optimization.
    DOI: https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FOUNDATION_DOI = "10.5281/zenodo.20589250"
FOUNDATION_URL = f"https://doi.org/10.5281/zenodo.{FOUNDATION_DOI.split('.')[-1]}"
FOUNDATION_CITATION = (
    "Medina, F. (2026). FableBreaker: A Reproducible Benchmark for "
    "Semantic-Preserving Evaluator Optimization. "
    f"https://doi.org/{FOUNDATION_DOI}"
)


@dataclass(frozen=True)
class PaperReference:
    """Reference to a journal paper with its SDK protocol binding."""

    title: str
    journal: str
    volume: int
    year: int
    authors: str
    protocol_module: str
    doi: str = ""
    foundation_doi: str = FOUNDATION_DOI


# Complete registry of all 14 papers in the journal system
PAPER_REGISTRY: list[PaperReference] = [
    # Adversarial Evaluation (3 papers)
    PaperReference(
        title="Hidden-Seed Adversarial Generation for Evaluator Stress Testing",
        journal="Journal of Adversarial Evaluation",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.generator",
    ),
    PaperReference(
        title="A Taxonomy of Evaluator Evasion Strategies in Code Optimization Benchmarks",
        journal="Journal of Adversarial Evaluation",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.generator",
    ),
    PaperReference(
        title="Overflow Corridors and Conditional Cascades: New Adversarial Families for Evaluator Certification",
        journal="Journal of Adversarial Evaluation",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.protocols.overflow_corridors",
    ),
    # Benchmark Architecture (3 papers)
    PaperReference(
        title="Game-Resistant Benchmark Design: Architectural Principles for Ungameable Evaluation",
        journal="Journal of Benchmark Architecture",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.scorer",
    ),
    PaperReference(
        title="Scoring Protocol Integrity Under Adversarial Candidate Submission",
        journal="Journal of Benchmark Architecture",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.scorer",
    ),
    PaperReference(
        title="Per-Family Scoring and Statistical Confidence in Multi-Family Benchmark Architectures",
        journal="Journal of Benchmark Architecture",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.protocols.per_family_scoring",
    ),
    # Certification Systems (3 papers)
    PaperReference(
        title="Cryptographic Evidence Chains for Performance Claim Certification",
        journal="Journal of Certification Systems",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.astlang",
    ),
    PaperReference(
        title="The Hidden-Seed Rotation Protocol: Temporal Integrity in Benchmark Certification",
        journal="Journal of Certification Systems",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.generator",
    ),
    PaperReference(
        title="Governance-Aware Certification: Embedding Trust Hierarchies in Benchmark Evidence Chains",
        journal="Journal of Certification Systems",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.protocols.governance_certification",
    ),
    # Semantic Preservation (2 papers)
    PaperReference(
        title="Formal Verification of Evaluator Equivalence Under Rewriting Transformations",
        journal="Journal of Semantic Preservation",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.astlang",
    ),
    PaperReference(
        title="Hash-Based Collision Resistance in Semantic Output Verification",
        journal="Journal of Semantic Preservation",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.astlang",
    ),
    # Reproducibility Methods (3 papers)
    PaperReference(
        title="Deterministic Test Generation via Seed-Controlled Stochastic AST Synthesis",
        journal="Journal of Reproducibility Methods",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.generator",
    ),
    PaperReference(
        title="Eliminating Measurement Variance in Performance Benchmarks: A Statistical Framework",
        journal="Journal of Reproducibility Methods",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.scorer",
    ),
    PaperReference(
        title="API-Driven Reproducibility: HTTP Service Architectures for Benchmark Automation",
        journal="Journal of Reproducibility Methods",
        volume=1, year=2026, authors="Freddy Medina",
        protocol_module="fablebreaker.protocols.api_reproducibility",
    ),
]


@dataclass
class ProtocolRegistry:
    """Registry of all protocol SDK implementations mapped to their papers.

    Usage:
        registry = ProtocolRegistry()
        papers = registry.by_journal("Journal of Adversarial Evaluation")
        paper = registry.by_title("Overflow Corridors")
    """

    papers: list[PaperReference] = field(default_factory=lambda: list(PAPER_REGISTRY))

    @property
    def foundation_doi(self) -> str:
        """Return the foundation paper DOI."""
        return FOUNDATION_DOI

    @property
    def paper_count(self) -> int:
        """Return total number of registered papers."""
        return len(self.papers)

    def by_journal(self, journal: str) -> list[PaperReference]:
        """Return all papers in a specific journal."""
        return [p for p in self.papers if p.journal == journal]

    def by_title(self, substring: str) -> list[PaperReference]:
        """Return papers whose title contains the given substring (case-insensitive)."""
        lower = substring.lower()
        return [p for p in self.papers if lower in p.title.lower()]

    def journals(self) -> list[str]:
        """Return sorted list of unique journal names."""
        return sorted(set(p.journal for p in self.papers))

    def summary(self) -> dict[str, Any]:
        """Return summary statistics for the registry."""
        journals = self.journals()
        return {
            "foundation_doi": FOUNDATION_DOI,
            "foundation_citation": FOUNDATION_CITATION,
            "total_papers": self.paper_count,
            "journals": len(journals),
            "papers_by_journal": {j: len(self.by_journal(j)) for j in journals},
        }
