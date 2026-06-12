"""
Fablebreaker Intelligence Engines
==================================

Modular evaluation engines that power Fablebreaker's reasoning.
Each engine is a specialized processor that can analyze, evaluate,
and certify different aspects of AI systems.

Engines are what make Fablebreaker alive — they are active, reasoning
components that go beyond static measurement.
"""

from .base import Engine, EngineRegistry, EngineResult
from .correctness import CorrectnessEngine
from .adversarial import AdversarialEngine
from .contamination import ContaminationEngine
from .certification import CertificationEngine
from .meta_evaluation import MetaEvaluationEngine

__all__ = [
    "Engine",
    "EngineRegistry",
    "EngineResult",
    "CorrectnessEngine",
    "AdversarialEngine",
    "ContaminationEngine",
    "CertificationEngine",
    "MetaEvaluationEngine",
]
