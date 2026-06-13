"""
FableBreaker Intelligence
=========================

The living intelligence layer of FableBreaker. This is not a benchmark —
FableBreaker is bigger than that. Benchmarks are data that Fablebreaker
Intelligence consumes, evaluates, and transcends.

Submodules
----------
- engines: Modular evaluation engines that power Fablebreaker's reasoning
- skills: Domain-specific capabilities Fablebreaker can invoke
- dataset: The comprehensive AI benchmarks knowledge base
"""

__version__ = "1.0.0"

from . import engines
from . import skills
from . import dataset

__all__ = [
    "engines",
    "skills",
    "dataset",
]
