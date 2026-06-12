"""
FableBreaker AI SDK
====================

The downloadable AI evaluation, certification, and intelligence toolkit.

Install:
    pip install fablebreaker-sdk

Usage:
    from fablebreaker_sdk import FableBreaker

    fb = FableBreaker()
    report = fb.analyze_code("path/to/your/code.py")
    print(report)

The SDK provides:
- Code review and security scanning
- Coverage gap analysis
- Self-analysis (dogfooding) capabilities
- Adversarial test generation
- Certification and evidence production
- Refactoring suggestions
- Documentation auditing
"""

__version__ = "1.0.0"
__author__ = "ItsNotAI LABS"

from .core import FableBreaker
from .scanner import CodeScanner
from .reporter import ReportGenerator

__all__ = [
    "FableBreaker",
    "CodeScanner",
    "ReportGenerator",
    "__version__",
]
