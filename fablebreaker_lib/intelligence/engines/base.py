"""
Base engine framework for Fablebreaker Intelligence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EngineStatus(Enum):
    """Engine operational status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class EngineResult:
    """Result from an engine execution."""
    engine_name: str
    status: EngineStatus
    verdict: str = ""
    confidence: float = 0.0
    findings: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "status": self.status.value,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "findings": self.findings,
            "metadata": self.metadata,
            "timestamp_utc": self.timestamp_utc,
        }


class Engine(ABC):
    """
    Base class for all Fablebreaker Intelligence engines.

    An engine is a living, active reasoning component. It doesn't just
    measure — it thinks, evaluates, and produces verdicts.
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._status = EngineStatus.IDLE
        self._run_count = 0

    @property
    def status(self) -> EngineStatus:
        return self._status

    @property
    def run_count(self) -> int:
        return self._run_count

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> EngineResult:
        """Execute the engine against the given context."""

    def run(self, context: dict[str, Any]) -> EngineResult:
        """Run the engine with lifecycle management."""
        self._status = EngineStatus.RUNNING
        try:
            result = self.execute(context)
            self._status = EngineStatus.COMPLETE
            self._run_count += 1
            return result
        except Exception as exc:
            self._status = EngineStatus.ERROR
            return EngineResult(
                engine_name=self.name,
                status=EngineStatus.ERROR,
                verdict=f"Engine error: {exc}",
                confidence=0.0,
            )

    def info(self) -> dict[str, Any]:
        """Get engine information."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self._status.value,
            "run_count": self._run_count,
        }


class EngineRegistry:
    """
    Registry of all active engines in Fablebreaker Intelligence.

    This is the nervous system — it knows what engines exist,
    their status, and can coordinate multi-engine evaluations.
    """

    def __init__(self) -> None:
        self._engines: dict[str, Engine] = {}

    def register(self, engine: Engine) -> None:
        """Register an engine."""
        self._engines[engine.name] = engine

    def get(self, name: str) -> Engine | None:
        """Get an engine by name."""
        return self._engines.get(name)

    def run_engine(self, name: str, context: dict[str, Any]) -> EngineResult:
        """Run a specific engine."""
        engine = self._engines.get(name)
        if not engine:
            return EngineResult(
                engine_name=name,
                status=EngineStatus.ERROR,
                verdict=f"Engine '{name}' not found",
            )
        return engine.run(context)

    def run_all(self, context: dict[str, Any]) -> list[EngineResult]:
        """Run all registered engines against the same context."""
        results = []
        for engine in self._engines.values():
            results.append(engine.run(context))
        return results

    def run_pipeline(self, engine_names: list[str], context: dict[str, Any]) -> list[EngineResult]:
        """Run a specific sequence of engines, passing results forward."""
        results = []
        enriched_context = dict(context)
        for name in engine_names:
            result = self.run_engine(name, enriched_context)
            results.append(result)
            enriched_context[f"engine_result_{name}"] = result.to_dict()
        return results

    @property
    def engine_names(self) -> list[str]:
        return list(self._engines.keys())

    def summary(self) -> dict[str, Any]:
        """Get summary of all registered engines."""
        return {
            "total_engines": len(self._engines),
            "engines": {name: eng.info() for name, eng in self._engines.items()},
            "total_runs": sum(eng.run_count for eng in self._engines.values()),
        }
