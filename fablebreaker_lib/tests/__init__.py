"""
Tests Module
=============

Test framework, validators, and integrity checks for the FableBreaker library.

Provides:
- Test case definitions and test runners
- Validators for all library components
- Integrity self-tests
- Regression test infrastructure
"""

from .framework import (
    TestCase,
    TestSuite,
    TestRunner,
    TestResult,
    TestStatus,
)
from .validators import (
    Validator,
    SchemaValidator,
    HashValidator,
    ConstraintValidator,
    ValidationResult,
)

__all__ = [
    "TestCase",
    "TestSuite",
    "TestRunner",
    "TestResult",
    "TestStatus",
    "Validator",
    "SchemaValidator",
    "HashValidator",
    "ConstraintValidator",
    "ValidationResult",
]
