"""
Base skill framework for Fablebreaker Intelligence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SkillLevel(Enum):
    """Proficiency level of a skill."""
    NOVICE = "novice"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class SkillResult:
    """Result from a skill invocation."""
    skill_name: str
    success: bool
    output: Any = None
    confidence: float = 0.0
    reasoning: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "success": self.success,
            "output": self.output,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "artifacts": self.artifacts,
            "timestamp_utc": self.timestamp_utc,
        }


class Skill(ABC):
    """
    Base class for Fablebreaker Intelligence skills.

    A skill is an active capability — something Fablebreaker can DO,
    not just measure. Skills make Fablebreaker alive.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        level: SkillLevel = SkillLevel.PROFICIENT,
    ) -> None:
        self.name = name
        self.description = description
        self.level = level
        self._invocation_count = 0
        self._success_count = 0

    @property
    def invocation_count(self) -> int:
        return self._invocation_count

    @property
    def success_rate(self) -> float:
        if self._invocation_count == 0:
            return 0.0
        return self._success_count / self._invocation_count

    @abstractmethod
    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """Invoke the skill with the given context."""

    def activate(self, context: dict[str, Any]) -> SkillResult:
        """Activate the skill with lifecycle tracking."""
        self._invocation_count += 1
        result = self.invoke(context)
        if result.success:
            self._success_count += 1
        return result

    def info(self) -> dict[str, Any]:
        """Get skill information."""
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level.value,
            "invocations": self._invocation_count,
            "success_rate": self.success_rate,
        }


class SkillRegistry:
    """
    Registry of all skills available to Fablebreaker Intelligence.

    The skill registry is Fablebreaker's repertoire — the set of
    things it knows how to do.
    """

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def activate(self, name: str, context: dict[str, Any]) -> SkillResult:
        """Activate a skill by name."""
        skill = self._skills.get(name)
        if not skill:
            return SkillResult(
                skill_name=name,
                success=False,
                reasoning=f"Skill '{name}' not found in registry",
            )
        return skill.activate(context)

    def activate_chain(self, skill_names: list[str], context: dict[str, Any]) -> list[SkillResult]:
        """Activate a chain of skills, passing results forward."""
        results = []
        enriched_context = dict(context)
        for name in skill_names:
            result = self.activate(name, enriched_context)
            results.append(result)
            enriched_context[f"skill_result_{name}"] = result.to_dict()
        return results

    @property
    def skill_names(self) -> list[str]:
        return list(self._skills.keys())

    @property
    def total_skills(self) -> int:
        return len(self._skills)

    def summary(self) -> dict[str, Any]:
        """Get summary of all registered skills."""
        return {
            "total_skills": len(self._skills),
            "skills": {name: skill.info() for name, skill in self._skills.items()},
            "total_invocations": sum(s.invocation_count for s in self._skills.values()),
            "skill_levels": {
                name: skill.level.value for name, skill in self._skills.items()
            },
        }
