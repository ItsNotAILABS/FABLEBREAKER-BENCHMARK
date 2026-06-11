"""
Test framework for running evaluation and validation tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class TestStatus(Enum):
    """Status of a test execution."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a single test case execution."""
    test_id: str
    status: TestStatus
    message: str = ""
    elapsed_ms: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "status": self.status.value,
            "message": self.message,
            "elapsed_ms": self.elapsed_ms,
            "evidence": self.evidence,
        }


@dataclass
class TestCase:
    """A single test case."""
    id: str
    name: str
    description: str
    category: str = "general"
    test_fn: Callable[[], tuple[bool, str]] | None = None
    tags: list[str] = field(default_factory=list)

    def run(self) -> TestResult:
        """Execute this test case."""
        import time
        start = time.perf_counter()
        try:
            if self.test_fn:
                passed, message = self.test_fn()
                status = TestStatus.PASSED if passed else TestStatus.FAILED
            else:
                status = TestStatus.SKIPPED
                message = "No test function defined"
        except Exception as exc:
            status = TestStatus.ERROR
            message = f"{type(exc).__name__}: {exc}"
        elapsed = (time.perf_counter() - start) * 1000

        return TestResult(
            test_id=self.id,
            status=status,
            message=message,
            elapsed_ms=elapsed,
        )


class TestSuite:
    """A collection of test cases."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._tests: list[TestCase] = []

    def add(self, test: TestCase) -> None:
        self._tests.append(test)

    def add_fn(self, test_id: str, name: str, fn: Callable[[], tuple[bool, str]], category: str = "general") -> None:
        """Convenience: add a test function directly."""
        self._tests.append(TestCase(
            id=test_id, name=name, description=name, category=category, test_fn=fn,
        ))

    def run_all(self) -> list[TestResult]:
        return [test.run() for test in self._tests]

    @property
    def tests(self) -> list[TestCase]:
        return list(self._tests)

    @property
    def count(self) -> int:
        return len(self._tests)


class TestRunner:
    """Runs test suites and generates reports."""

    def __init__(self) -> None:
        self._suites: list[TestSuite] = []

    def add_suite(self, suite: TestSuite) -> None:
        self._suites.append(suite)

    def run_all(self) -> dict[str, Any]:
        """Run all registered test suites and return report."""
        suite_results: list[dict[str, Any]] = []
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0

        for suite in self._suites:
            results = suite.run_all()
            passed = sum(1 for r in results if r.status == TestStatus.PASSED)
            failed = sum(1 for r in results if r.status == TestStatus.FAILED)
            errors = sum(1 for r in results if r.status == TestStatus.ERROR)
            skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)

            total_passed += passed
            total_failed += failed
            total_errors += errors
            total_skipped += skipped

            suite_results.append({
                "suite": suite.name,
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "results": [r.to_dict() for r in results],
            })

        return {
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_suites": len(self._suites),
            "total_tests": total_passed + total_failed + total_errors + total_skipped,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "skipped": total_skipped,
            "all_passed": total_failed == 0 and total_errors == 0,
            "suites": suite_results,
        }
