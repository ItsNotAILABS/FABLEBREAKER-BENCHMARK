"""
Benchmark suite definitions and registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class SuiteConfig:
    """Configuration for a benchmark suite."""
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    candidate_contract: str = "Python module exposing evaluate(expr: dict) -> object"
    certification_rule: str = "Any wrong hash disables speed certification."
    default_seed: int = 823
    default_count: int = 240
    max_steps: int = 2_000_000
    adversarial_families: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BenchmarkSuite:
    """A complete benchmark suite with generation, scoring, and certification."""

    def __init__(self, config: SuiteConfig) -> None:
        self.config = config
        self._generators: dict[str, Callable] = {}
        self._validators: list[Callable] = []

    @property
    def id(self) -> str:
        return self.config.id

    @property
    def name(self) -> str:
        return self.config.name

    def register_family(self, family_name: str, generator: Callable) -> None:
        """Register an adversarial family generator."""
        self._generators[family_name] = generator
        if family_name not in self.config.adversarial_families:
            self.config.adversarial_families.append(family_name)

    def register_validator(self, validator: Callable) -> None:
        """Register a post-evaluation validator."""
        self._validators.append(validator)

    @property
    def families(self) -> list[str]:
        return list(self._generators.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.config.id,
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "candidate_contract": self.config.candidate_contract,
            "certification_rule": self.config.certification_rule,
            "adversarial_families": self.config.adversarial_families,
            "metadata": self.config.metadata,
        }


class SuiteRegistry:
    """Global registry of benchmark suites."""

    _instance: SuiteRegistry | None = None
    _suites: dict[str, BenchmarkSuite]

    def __init__(self) -> None:
        self._suites = {}

    @classmethod
    def instance(cls) -> SuiteRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, suite: BenchmarkSuite) -> None:
        self._suites[suite.id] = suite

    def get(self, suite_id: str) -> BenchmarkSuite | None:
        return self._suites.get(suite_id)

    def list_suites(self) -> list[str]:
        return list(self._suites.keys())

    def all(self) -> list[BenchmarkSuite]:
        return list(self._suites.values())
