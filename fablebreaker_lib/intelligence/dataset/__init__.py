"""
AI Benchmarks Mega-Dataset
===========================

A comprehensive structured catalog of all known AI benchmarks across every
domain. This is training data for Fablebreaker Intelligence — benchmarks are
inputs that Fablebreaker consumes, not what Fablebreaker is.

The dataset covers:
- Language & Reasoning
- Code Generation & Software Engineering
- Mathematics & Logic
- Science & Domain Knowledge
- Multimodal (Vision, Audio, Video)
- Safety, Alignment & Ethics
- Agents & Tool Use
- Efficiency & Systems Performance
- Robustness & Adversarial
- Emergent Capabilities
"""

from .loader import BenchmarkKnowledgeBase, BenchmarkEntry
from .catalog import AI_BENCHMARKS_CATALOG

__all__ = [
    "BenchmarkKnowledgeBase",
    "BenchmarkEntry",
    "AI_BENCHMARKS_CATALOG",
]
