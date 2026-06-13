"""
Dataset generation and adversarial family definitions.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class DatasetCase:
    """A single evaluation case in a benchmark dataset."""
    id: str
    split: str
    family: str
    size_hint: int
    expr: dict[str, Any]
    expected_sha256: str
    reference_steps: int = 0
    reference_max_depth: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "split": self.split,
            "family": self.family,
            "size_hint": self.size_hint,
            "expr": self.expr,
            "expected_sha256": self.expected_sha256,
            "reference_steps": self.reference_steps,
            "reference_max_depth": self.reference_max_depth,
        }


@dataclass
class AdversarialFamily:
    """Definition of an adversarial expression family."""
    name: str
    description: str
    difficulty: str = "standard"
    generator: Callable[[random.Random, int], dict[str, Any]] | None = None
    public_size_range: tuple[int, int] = (12, 70)
    hidden_size_range: tuple[int, int] = (25, 120)
    tags: list[str] = field(default_factory=list)

    def generate(self, rng: random.Random, size: int) -> dict[str, Any]:
        if self.generator is None:
            raise NotImplementedError(f"No generator for family '{self.name}'")
        return self.generator(rng, size)


class DatasetGenerator:
    """Deterministic dataset generator from seed values."""

    def __init__(self) -> None:
        self._families: dict[str, AdversarialFamily] = {}

    def register_family(self, family: AdversarialFamily) -> None:
        self._families[family.name] = family

    @property
    def families(self) -> list[str]:
        return list(self._families.keys())

    def generate_cases(
        self,
        seed: int,
        count: int,
        split: str = "public",
        evaluator: Any = None,
        hash_fn: Any = None,
    ) -> list[DatasetCase]:
        """Generate a deterministic set of evaluation cases."""
        rng = random.Random(seed)
        cases: list[DatasetCase] = []
        family_names = list(self._families.keys())

        if not family_names:
            raise ValueError("No adversarial families registered")

        for idx in range(count):
            family_name = rng.choice(family_names)
            family = self._families[family_name]

            size_range = family.public_size_range if split == "public" else family.hidden_size_range
            size = rng.randint(size_range[0], size_range[1])

            expr = family.generate(rng, size)

            expected_hash = ""
            ref_steps = 0
            ref_depth = 0
            if evaluator and hash_fn:
                value, stats = evaluator(expr)
                expected_hash = hash_fn(value)
                ref_steps = stats.steps
                ref_depth = stats.max_depth

            cases.append(DatasetCase(
                id=f"{split}-{idx:04d}-{family_name}",
                split=split,
                family=family_name,
                size_hint=size,
                expr=expr,
                expected_sha256=expected_hash,
                reference_steps=ref_steps,
                reference_max_depth=ref_depth,
            ))

        return cases

    def write_dataset(self, cases: list[DatasetCase], output_path: Path) -> None:
        """Write cases to a JSONL file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            for case in cases:
                handle.write(json.dumps(case.to_dict(), sort_keys=True) + "\n")
