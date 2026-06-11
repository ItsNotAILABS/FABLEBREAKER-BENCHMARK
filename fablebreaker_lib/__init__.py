"""
FableBreaker Library
====================

A comprehensive Python library for AI evaluation benchmarks, testing,
regulations, rules, foundations, protocols, governance, and emergent
behavior detection.

Modules
-------
- benchmarks: Adversarial evaluation suites and scoring
- tests: Test framework, validators, and integrity checks
- regulations: AI compliance rules, standards, and audit checks
- rules: Evaluation rules, constraints, and enforcement policies
- foundations: Core principles, axioms, and base abstractions
- protocols: Certification, evidence, and communication protocols
- governance: Policies, oversight, accountability, and decision frameworks
- emergent: Emergent behavior detection, monitoring, and safety analysis
"""

__version__ = "1.0.0"
__author__ = "ItsNotAI LABS"

from . import benchmarks
from . import tests
from . import regulations
from . import rules
from . import foundations
from . import protocols
from . import governance
from . import emergent

__all__ = [
    "benchmarks",
    "tests",
    "regulations",
    "rules",
    "foundations",
    "protocols",
    "governance",
    "emergent",
    "__version__",
]
