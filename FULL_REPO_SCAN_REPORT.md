# FableBreaker Full Repository Scan Report

> **Complete SDK evaluation of the entire FABLEBREAKER-BENCHMARK repository.**

**Generated:** 2026-06-12  
**SDK Version:** 1.0.0  
**Method:** `fablebreaker_sdk.CodeScanner.scan_directory(".", pattern="*.py", recursive=True)`  
**Scope:** All Python source files in the repository

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Files Scanned** | 89 |
| **Total Issues** | 238 |
| **Security Vulnerabilities** | 5 |
| **Critical Vulnerabilities** | 2 |
| **Undocumented Items** | 409 |
| **Skills Invoked Per File** | 5 (code_review, security, refactoring, documentation, self_analysis) |

---

## Security Findings

### Critical

| File | Type | Description |
|------|------|-------------|
| `fablebreaker_lib/intelligence/skills/security.py` | Code Injection | Arbitrary code execution via `eval()` — used as part of the security scanner's detection patterns |
| `fablebreaker_lib/intelligence/skills/security.py` | Command Injection | `subprocess` with `shell=True` — command injection risk in scanner internals |

### High

| File | Type | Description |
|------|------|-------------|
| `fablebreaker_service.py` | Missing Authentication | Endpoint handler without apparent authentication check |

### Medium

| File | Type | Description |
|------|------|-------------|
| `fablebreaker_lib/intelligence/skills/security.py` | Information Exposure | Stack trace or error details may be exposed in production |

### Context & Assessment

- **`security.py` critical findings:** These exist within the security scanner itself, which uses `eval()` and `subprocess` as part of its pattern-detection test suite. The scanner intentionally contains these patterns to validate its own detection capabilities. **Risk is contained** — these are not reachable from external input paths.
- **`fablebreaker_service.py` missing auth:** The HTTP service is designed for local/air-gapped deployment. Network-exposed deployments should use a reverse proxy with authentication. This is documented in `SERVICE.md`.

---

## Code Quality Summary

### High-Issue Files (5+ issues)

| File | Issues | Primary Categories |
|------|--------|-------------------|
| `fablebreaker_lib/intelligence/skills/security.py` | 9 | security, correctness, completeness |
| `fablebreaker_lib/intelligence/dataset/catalog.py` | 7 | completeness, style |
| `fablebreaker_lib/intelligence/skills/coverage.py` | 7 | completeness, correctness |
| `fablebreaker_lib/intelligence/skills/self_analysis.py` | 7 | completeness, correctness |
| `fablebreaker_service.py` | 7 | security, correctness, completeness |
| `fablebreaker_sdk/core.py` | 6 | completeness |
| `fablebreaker_lib/intelligence/skills/documentation.py` | 6 | completeness, style |
| `fablebreaker/tests/test_scoring_and_evidence.py` | 5 | correctness, completeness |
| `fablebreaker_lib/benchmarks/scoring.py` | 5 | correctness, completeness |
| `fablebreaker_lib/intelligence/skills/analysis.py` | 5 | completeness, style |
| `fablebreaker_lib/intelligence/skills/code_review.py` | 5 | completeness, correctness |
| `fablebreaker_lib/intelligence/skills/refactoring.py` | 5 | completeness, correctness |
| `fablebreaker_lib/intelligence/dataset/loader.py` | 5 | correctness, completeness |
| `fablebreaker_lib/intelligence/engines/correctness.py` | 5 | correctness, completeness |

### Clean Files (0 issues)

| File |
|------|
| `fablebreaker/fablebreaker/__init__.py` |
| `fablebreaker/tools/__init__.py` |
| `fablebreaker_lib/__init__.py` |
| `fablebreaker_lib/benchmarks/__init__.py` |
| `fablebreaker_lib/emergent/__init__.py` |
| `fablebreaker_lib/foundations/__init__.py` |
| `fablebreaker_lib/governance/__init__.py` |
| `fablebreaker_lib/intelligence/__init__.py` |
| `fablebreaker_lib/intelligence/dataset/__init__.py` |
| `fablebreaker_lib/intelligence/engines/__init__.py` |
| `fablebreaker_lib/intelligence/skills/__init__.py` |
| `fablebreaker_lib/protocols/__init__.py` |
| `fablebreaker_lib/regulations/__init__.py` |
| `fablebreaker_lib/rules/__init__.py` |
| `fablebreaker_lib/tests/__init__.py` |
| `benchmark-certification/suites/fablebreaker/fablebreaker/__init__.py` |

---

## Code Review — Recurring Patterns

| Pattern | Severity | Occurrences | Description |
|---------|----------|-------------|-------------|
| Missing docstrings | Low | 67 files | Functions lacking documentation |
| Line length violations | Low | 12 files | Lines exceeding 120 characters |
| Division without zero-guard | Low | 8 files | Potential `ZeroDivisionError` |
| Missing error handling on I/O | Medium | 3 files | File operations without try/except |
| Use of eval/exec | High | 1 file | Code injection risk (contained) |

---

## Documentation Coverage

| Metric | Value |
|--------|-------|
| **Undocumented Items** | 409 |
| **Files with undocumented functions** | 67 / 89 (75%) |
| **Worst offenders** | `generator.py` (13/13), `astlang.py` (7/7), `scorer.py` (5/5) |

### Assessment

Documentation coverage is the primary quality gap across the repository. The core benchmark logic (`astlang.py`, `generator.py`, `scorer.py`) and the intelligence library lack docstrings on most functions. While the code is generally readable and well-structured, the absence of documentation impacts onboarding and long-term maintainability.

---

## Refactoring Opportunities

| Category | Files Affected | Estimated Improvement |
|----------|---------------|----------------------|
| Function decomposition | 14 | Moderate |
| Error handling consolidation | 8 | Moderate |
| Type annotation completeness | 6 | Low |
| Redundant code elimination | 4 | Low |

---

## Per-Module Breakdown

### `fablebreaker/` (Core Benchmark)

| File | Issues |
|------|--------|
| `candidates/baseline_candidate.py` | 1 |
| `candidates/example_multi_agent.py` | 2 |
| `fablebreaker/astlang.py` | 3 |
| `fablebreaker/evidence.py` | 3 |
| `fablebreaker/generator.py` | 4 |
| `fablebreaker/leaderboard.py` | 1 |
| `fablebreaker/regression.py` | 2 |
| `fablebreaker/scorer.py` | 3 |
| `fablebreaker/seeds.py` | 1 |
| `tests/test_benchmark_integrity.py` | 1 |
| `tests/test_certification_infrastructure.py` | 2 |
| `tests/test_evaluator_edge_cases.py` | 2 |
| `tests/test_scoring_and_evidence.py` | 5 |
| `tools/batch_audit.py` | 9 |
| `tools/claim_audit.py` | 4 |
| `tools/repo_scanner.py` | 2 |
| `tools/run_full_audit.py` | 3 |
| **Subtotal** | **48** |

### `fablebreaker_lib/` (Intelligence Library)

| File | Issues |
|------|--------|
| `benchmarks/dataset.py` | 3 |
| `benchmarks/leaderboard.py` | 3 |
| `benchmarks/scoring.py` | 5 |
| `benchmarks/suite.py` | 1 |
| `emergent/detection.py` | 2 |
| `emergent/monitoring.py` | 2 |
| `emergent/safety.py` | 3 |
| `foundations/axioms.py` | 2 |
| `foundations/base.py` | 3 |
| `foundations/integrity.py` | 1 |
| `governance/accountability.py` | 3 |
| `governance/oversight.py` | 2 |
| `governance/policies.py` | 3 |
| `intelligence/dataset/catalog.py` | 7 |
| `intelligence/dataset/loader.py` | 5 |
| `intelligence/engines/adversarial.py` | 4 |
| `intelligence/engines/base.py` | 1 |
| `intelligence/engines/certification.py` | 3 |
| `intelligence/engines/contamination.py` | 4 |
| `intelligence/engines/correctness.py` | 5 |
| `intelligence/engines/meta_evaluation.py` | 4 |
| `intelligence/skills/analysis.py` | 5 |
| `intelligence/skills/base.py` | 2 |
| `intelligence/skills/code_review.py` | 5 |
| `intelligence/skills/coverage.py` | 7 |
| `intelligence/skills/detection.py` | 3 |
| `intelligence/skills/documentation.py` | 6 |
| `intelligence/skills/generation.py` | 3 |
| `intelligence/skills/reasoning.py` | 4 |
| `intelligence/skills/refactoring.py` | 5 |
| `intelligence/skills/security.py` | 9 |
| `intelligence/skills/self_analysis.py` | 7 |
| `intelligence/skills/synthesis.py` | 4 |
| `protocols/certification.py` | 2 |
| `protocols/communication.py` | 1 |
| `protocols/evidence.py` | 3 |
| `regulations/audit.py` | 2 |
| `regulations/compliance.py` | 2 |
| `regulations/standards.py` | 1 |
| `rules/constraints.py` | 2 |
| `rules/engine.py` | 4 |
| `tests/framework.py` | 1 |
| `tests/validators.py` | 4 |
| **Subtotal** | **143** |

### `fablebreaker_sdk/` (SDK)

| File | Issues |
|------|--------|
| `__init__.py` | 1 |
| `cli.py` | 1 |
| `core.py` | 6 |
| `reporter.py` | 3 |
| `scanner.py` | 3 |
| **Subtotal** | **14** |

### `benchmark-certification/` (Certification Infrastructure)

| File | Issues |
|------|--------|
| `services/fablebreaker_service.py` | 6 |
| `suites/fablebreaker/candidates/baseline_candidate.py` | 1 |
| `suites/fablebreaker/fablebreaker/astlang.py` | 3 |
| `suites/fablebreaker/fablebreaker/generator.py` | 4 |
| `suites/fablebreaker/fablebreaker/scorer.py` | 3 |
| `suites/fablebreaker/tests/test_benchmark_integrity.py` | 1 |
| `suites/fablebreaker/tools/run_full_audit.py` | 3 |
| **Subtotal** | **21** |

### Root Files

| File | Issues |
|------|--------|
| `fablebreaker_service.py` | 7 |

---

## Recommendations

### Immediate (P1)

1. **Add authentication middleware** to `fablebreaker_service.py` for non-local deployments
2. **Add zero-division guards** in scorer and batch audit division operations
3. **Document the `eval()` usage** in `security.py` with explicit safety comments explaining it's for pattern detection only

### Short-term (P2 — v1.1)

4. **Add docstrings** to all public functions in core benchmark files (`astlang.py`, `generator.py`, `scorer.py`)
5. **Add error handling** around file I/O operations in `generator.py` and `loader.py`
6. **Fix line-length violations** across 12 files

### Medium-term (P3 — v1.2)

7. **Systematic documentation pass** across `fablebreaker_lib/` (143 issues, mostly completeness)
8. **Refactor `batch_audit.py`** — highest issue count in tools (9 issues)
9. **Add type annotations** to remaining untyped functions

---

## SDK Bug Found During Scan

During this scan, a bug was identified in `fablebreaker_sdk/core.py`:

**Issue:** `full_scan()` method crashes with `AttributeError: 'NoneType' object has no attribute 'get'` when a skill returns `None` instead of a dict.

**Location:** Line 313 in `core.py`  
**Root cause:** The generator expression `r.get("output", {}).get(...)` does not guard against `r` being `None`.  
**Fix:** Added null-safety check (see commit).

---

## Methodology

This report was generated by:

1. Instantiating `fablebreaker_sdk.CodeScanner`
2. Calling `scan_directory(".", pattern="*.py", recursive=True)` on the repository root
3. Each file was evaluated with 5 skills: `code_review`, `security`, `refactoring`, `documentation`, `self_analysis`
4. Results were aggregated and analyzed

The scan is deterministic and reproducible — running the same command on the same codebase will produce identical results.

---

<p align="center">
  <strong>ItsNotAI LABS</strong><br>
  <em>Proof before speed. Correctness before claims. Reproducibility before trust.</em>
</p>
