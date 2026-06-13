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
from .code_review import CodeReviewSkill
from .coverage import CoverageSkill
from .security import SecuritySkill
from .refactoring import RefactoringSkill
from .documentation import DocumentationSkill
from .self_analysis import SelfAnalysisSkill

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillResult",
    "AnalysisSkill",
    "GenerationSkill",
    "DetectionSkill",
    "ReasoningSkill",
    "SynthesisSkill",
    "CodeReviewSkill",
    "CoverageSkill",
    "SecuritySkill",
    "RefactoringSkill",
    "DocumentationSkill",
    "SelfAnalysisSkill",
]
