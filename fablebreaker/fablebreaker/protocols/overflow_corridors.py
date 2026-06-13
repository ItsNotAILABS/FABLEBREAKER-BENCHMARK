"""Overflow Corridor Protocol SDK.

Implements the methodology from:
    "Overflow Corridors and Conditional Cascades: New Adversarial Families
     for Evaluator Certification"
    Journal of Adversarial Evaluation · Volume 1 · 2026

This module provides a programmatic interface for generating, configuring,
and validating overflow corridor adversarial expressions as described in
the paper's Section 2.

Foundation: https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from ..astlang import evaluate, digest
from ..generator import overflow_corridor, lit, binop, neg, abs_op


@dataclass(frozen=True)
class CorridorConfig:
    """Configuration for overflow corridor generation.

    Attributes:
        min_seed: Minimum seed value for corridor entry (default 2).
        max_seed: Maximum seed value for corridor entry (default 2^16).
        growth_range: Multiplier range for growth operations.
        reduction_primes: Prime moduli for reduction operations.
        flip_min: Minimum XOR constant for flip operations.
        flip_max: Maximum XOR constant for flip operations.
        shift_max: Maximum subtraction for shift operations.
        abs_interval: Insert abs operation every N steps.
        neg_interval: Insert neg operation every N steps.
    """

    min_seed: int = 2
    max_seed: int = 2**16
    growth_range: tuple[int, int] = (2, 127)
    reduction_primes: tuple[int, ...] = (65537, 104729, 1000003)
    flip_min: int = 2**15
    flip_max: int = 2**31
    shift_max: int = 2**20
    abs_interval: int = 7
    neg_interval: int = 11


@dataclass
class CorridorResult:
    """Result of corridor generation and validation."""

    expr: dict[str, Any]
    size: int
    expected_hash: str
    reference_steps: int
    reference_max_depth: int
    valid: bool
    config: CorridorConfig = field(default_factory=CorridorConfig)


class OverflowCorridorProtocol:
    """SDK for the Overflow Corridor adversarial protocol.

    Generates expressions that push values through overflow-prone corridors,
    testing whether candidates incorrectly truncate or clamp large integers.

    Usage:
        protocol = OverflowCorridorProtocol()
        result = protocol.generate(seed=42, size=30)
        assert result.valid
        print(f"Hash: {result.expected_hash}")

        # Validate a candidate result against the corridor
        is_correct = protocol.validate(result.expr, candidate_value)

        # Batch generation
        results = protocol.generate_batch(seed=42, count=50, size_range=(15, 60))
    """

    PAPER_TITLE = "Overflow Corridors and Conditional Cascades: New Adversarial Families for Evaluator Certification"
    JOURNAL = "Journal of Adversarial Evaluation"
    DOI_FOUNDATION = "10.5281/zenodo.20589250"

    def __init__(self, config: CorridorConfig | None = None) -> None:
        self.config = config or CorridorConfig()

    def generate(self, seed: int, size: int) -> CorridorResult:
        """Generate a single overflow corridor expression.

        Args:
            seed: Random seed for deterministic generation.
            size: Number of operations in the corridor.

        Returns:
            CorridorResult with the expression and its expected hash.
        """
        rng = random.Random(seed)
        expr = overflow_corridor(rng, size)
        value, stats = evaluate(expr)
        return CorridorResult(
            expr=expr,
            size=size,
            expected_hash=digest(value),
            reference_steps=stats.steps,
            reference_max_depth=stats.max_depth,
            valid=True,
            config=self.config,
        )

    def generate_batch(
        self, seed: int, count: int, size_range: tuple[int, int] = (15, 60)
    ) -> list[CorridorResult]:
        """Generate a batch of overflow corridor expressions.

        Args:
            seed: Base random seed.
            count: Number of expressions to generate.
            size_range: (min_size, max_size) for each corridor.

        Returns:
            List of CorridorResult instances.
        """
        rng = random.Random(seed)
        results = []
        for _ in range(count):
            size = rng.randint(*size_range)
            sub_seed = rng.randint(0, 2**31)
            results.append(self.generate(sub_seed, size))
        return results

    def validate(self, expr: dict[str, Any], candidate_value: Any) -> bool:
        """Validate a candidate's result against the corridor's expected output.

        Args:
            expr: The corridor expression that was evaluated.
            candidate_value: The value produced by the candidate.

        Returns:
            True if the candidate's output matches the reference.
        """
        reference_value, _ = evaluate(expr)
        return digest(candidate_value) == digest(reference_value)

    def complexity_bound(self, size: int) -> dict[str, Any]:
        """Compute theoretical complexity bounds for a corridor of given size.

        Based on Section 2.3 of the paper: max intermediate value is
        O(127^(n/7)) due to periodic modular reduction.
        """
        max_intermediate = 127 ** (size // self.config.abs_interval)
        return {
            "size": size,
            "max_intermediate_bound": max_intermediate,
            "exceeds_64bit": max_intermediate > 2**63,
            "exceeds_128bit": max_intermediate > 2**127,
            "reference_time_complexity": f"O({size} * log({max_intermediate}))",
        }
