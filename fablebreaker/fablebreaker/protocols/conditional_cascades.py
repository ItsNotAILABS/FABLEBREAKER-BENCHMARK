"""Conditional Cascade Protocol SDK.

Implements the methodology from:
    "Overflow Corridors and Conditional Cascades: New Adversarial Families
     for Evaluator Certification"
    Journal of Adversarial Evaluation · Volume 1 · 2026

This module provides a programmatic interface for generating, configuring,
and validating nested conditional cascade adversarial expressions as
described in the paper's Section 3.

Foundation: https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from ..astlang import evaluate, digest
from ..generator import nested_conditional_cascade


@dataclass(frozen=True)
class CascadeConfig:
    """Configuration for conditional cascade generation.

    Attributes:
        moduli: Divisors used for if_zero condition testing.
        max_add: Maximum constant for addition in then-branches.
        max_xor: Maximum constant for XOR in else-branches.
        erase_probability: Probability of an erase_gate vs if_zero step.
    """

    moduli: tuple[int, ...] = (2, 3, 5, 7)
    max_add: int = 50
    max_xor: int = 255
    erase_probability: float = 1.0 / 3.0


@dataclass
class CascadeResult:
    """Result of cascade generation and validation."""

    expr: dict[str, Any]
    size: int
    expected_hash: str
    reference_steps: int
    reference_max_depth: int
    valid: bool
    config: CascadeConfig = field(default_factory=CascadeConfig)


class ConditionalCascadeProtocol:
    """SDK for the Conditional Cascade adversarial protocol.

    Generates deeply nested if_zero cascades with erasure traps that test
    whether candidates correctly evaluate both conditional semantics and
    zero-testing across deeply nested structures.

    Usage:
        protocol = ConditionalCascadeProtocol()
        result = protocol.generate(seed=42, size=25)
        assert result.valid

        # Validate candidate output
        is_correct = protocol.validate(result.expr, candidate_value)

        # Batch generation
        results = protocol.generate_batch(seed=42, count=50)
    """

    PAPER_TITLE = "Overflow Corridors and Conditional Cascades: New Adversarial Families for Evaluator Certification"
    JOURNAL = "Journal of Adversarial Evaluation"
    DOI_FOUNDATION = "10.5281/zenodo.20589250"

    def __init__(self, config: CascadeConfig | None = None) -> None:
        self.config = config or CascadeConfig()

    def generate(self, seed: int, size: int) -> CascadeResult:
        """Generate a single nested conditional cascade expression.

        Args:
            seed: Random seed for deterministic generation.
            size: Nesting depth of the cascade.

        Returns:
            CascadeResult with the expression and its expected hash.
        """
        rng = random.Random(seed)
        expr = nested_conditional_cascade(rng, size)
        value, stats = evaluate(expr)
        return CascadeResult(
            expr=expr,
            size=size,
            expected_hash=digest(value),
            reference_steps=stats.steps,
            reference_max_depth=stats.max_depth,
            valid=True,
            config=self.config,
        )

    def generate_batch(
        self, seed: int, count: int, size_range: tuple[int, int] = (10, 50)
    ) -> list[CascadeResult]:
        """Generate a batch of conditional cascade expressions.

        Args:
            seed: Base random seed.
            count: Number of expressions to generate.
            size_range: (min_size, max_size) for each cascade.

        Returns:
            List of CascadeResult instances.
        """
        rng = random.Random(seed)
        results = []
        for _ in range(count):
            size = rng.randint(*size_range)
            sub_seed = rng.randint(0, 2**31)
            results.append(self.generate(sub_seed, size))
        return results

    def validate(self, expr: dict[str, Any], candidate_value: Any) -> bool:
        """Validate a candidate's result against the cascade's expected output.

        Args:
            expr: The cascade expression that was evaluated.
            candidate_value: The value produced by the candidate.

        Returns:
            True if the candidate's output matches the reference.
        """
        reference_value, _ = evaluate(expr)
        return digest(candidate_value) == digest(reference_value)

    def analyze_branching(self, expr: dict[str, Any]) -> dict[str, Any]:
        """Analyze the branching structure of a cascade expression.

        Returns statistics about the conditional structure useful for
        understanding why a candidate might fail on this expression.
        """
        stats = {"if_zero_count": 0, "erase_count": 0, "let_count": 0, "max_depth": 0}
        self._walk(expr, stats, 0)
        return stats

    def _walk(self, expr: dict[str, Any], stats: dict[str, Any], depth: int) -> None:
        """Recursively walk expression to collect structural statistics."""
        if depth > stats["max_depth"]:
            stats["max_depth"] = depth
        op = expr.get("op", "")
        if op == "if_zero":
            stats["if_zero_count"] += 1
            self._walk(expr.get("cond", {}), stats, depth + 1)
            self._walk(expr.get("then", {}), stats, depth + 1)
            self._walk(expr.get("else", {}), stats, depth + 1)
        elif op == "erase":
            stats["erase_count"] += 1
            self._walk(expr.get("body", {}), stats, depth + 1)
        elif op == "let":
            stats["let_count"] += 1
            self._walk(expr.get("value", {}), stats, depth + 1)
            self._walk(expr.get("body", {}), stats, depth + 1)
        elif op in ("add", "sub", "mul", "xor", "mod", "band", "bor"):
            self._walk(expr.get("left", {}), stats, depth + 1)
            self._walk(expr.get("right", {}), stats, depth + 1)
        elif op in ("neg", "abs", "fst", "snd"):
            self._walk(expr.get("value", {}), stats, depth + 1)
