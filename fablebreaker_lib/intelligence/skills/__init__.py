"""
Fablebreaker Intelligence Skills
==================================

Domain-specific capabilities that Fablebreaker can invoke.
Skills are active abilities — they let Fablebreaker act in the world,
not just observe it.

Each skill represents a distinct capability domain that Fablebreaker
can activate on demand.
"""

from .base import Skill, SkillRegistry, SkillResult
from .analysis import AnalysisSkill
from .generation import GenerationSkill
from .detection import DetectionSkill
from .reasoning import ReasoningSkill
from .synthesis import SynthesisSkill

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillResult",
    "AnalysisSkill",
    "GenerationSkill",
    "DetectionSkill",
    "ReasoningSkill",
    "SynthesisSkill",
]
