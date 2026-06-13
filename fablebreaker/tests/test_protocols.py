"""Tests for protocol SDK modules."""

from __future__ import annotations

import unittest

from fablebreaker.protocols import (
    FOUNDATION_DOI,
    FOUNDATION_CITATION,
    OverflowCorridorProtocol,
    ConditionalCascadeProtocol,
    GovernanceCertificationProtocol,
    PerFamilyScoringProtocol,
    APIReproducibilityProtocol,
    ProtocolRegistry,
)
from fablebreaker.protocols.governance_certification import GovernanceRole


class TestFoundation(unittest.TestCase):
    def test_foundation_doi(self) -> None:
        self.assertEqual(FOUNDATION_DOI, "10.5281/zenodo.20589250")

    def test_foundation_citation_contains_doi(self) -> None:
        self.assertIn("10.5281/zenodo.20589250", FOUNDATION_CITATION)

    def test_registry_has_14_papers(self) -> None:
        registry = ProtocolRegistry()
        self.assertEqual(registry.paper_count, 14)

    def test_registry_has_5_journals(self) -> None:
        registry = ProtocolRegistry()
        self.assertEqual(len(registry.journals()), 5)

    def test_registry_by_journal(self) -> None:
        registry = ProtocolRegistry()
        adversarial = registry.by_journal("Journal of Adversarial Evaluation")
        self.assertEqual(len(adversarial), 3)

    def test_registry_by_title(self) -> None:
        registry = ProtocolRegistry()
        results = registry.by_title("Overflow Corridors")
        self.assertEqual(len(results), 1)
        self.assertIn("Overflow Corridors", results[0].title)

    def test_registry_summary(self) -> None:
        registry = ProtocolRegistry()
        summary = registry.summary()
        self.assertEqual(summary["total_papers"], 14)
        self.assertEqual(summary["journals"], 5)


class TestOverflowCorridorProtocol(unittest.TestCase):
    def test_generate_deterministic(self) -> None:
        protocol = OverflowCorridorProtocol()
        r1 = protocol.generate(seed=42, size=20)
        r2 = protocol.generate(seed=42, size=20)
        self.assertEqual(r1.expected_hash, r2.expected_hash)
        self.assertTrue(r1.valid)

    def test_validate_correct(self) -> None:
        protocol = OverflowCorridorProtocol()
        result = protocol.generate(seed=99, size=15)
        from fablebreaker.astlang import evaluate
        value, _ = evaluate(result.expr)
        self.assertTrue(protocol.validate(result.expr, value))

    def test_batch_generation(self) -> None:
        protocol = OverflowCorridorProtocol()
        results = protocol.generate_batch(seed=7, count=5, size_range=(10, 20))
        self.assertEqual(len(results), 5)
        for r in results:
            self.assertTrue(r.valid)

    def test_complexity_bound(self) -> None:
        protocol = OverflowCorridorProtocol()
        bounds = protocol.complexity_bound(70)
        self.assertTrue(bounds["exceeds_64bit"])


class TestConditionalCascadeProtocol(unittest.TestCase):
    def test_generate_deterministic(self) -> None:
        protocol = ConditionalCascadeProtocol()
        r1 = protocol.generate(seed=42, size=15)
        r2 = protocol.generate(seed=42, size=15)
        self.assertEqual(r1.expected_hash, r2.expected_hash)

    def test_validate_correct(self) -> None:
        protocol = ConditionalCascadeProtocol()
        result = protocol.generate(seed=123, size=10)
        from fablebreaker.astlang import evaluate
        value, _ = evaluate(result.expr)
        self.assertTrue(protocol.validate(result.expr, value))

    def test_analyze_branching(self) -> None:
        protocol = ConditionalCascadeProtocol()
        result = protocol.generate(seed=42, size=20)
        analysis = protocol.analyze_branching(result.expr)
        self.assertGreater(analysis["if_zero_count"] + analysis["erase_count"], 0)
        self.assertGreater(analysis["let_count"], 0)


class TestGovernanceCertificationProtocol(unittest.TestCase):
    def test_create_evidence_pack(self) -> None:
        protocol = GovernanceCertificationProtocol()
        gov = protocol.create_governance_version(
            version="1.0.0",
            effective_date="2026-01-01",
            rules_hash="abc123",
            authority="ItsNotAI LABS",
        )
        role = protocol.grant_role(
            operator="operator@example.com",
            role=GovernanceRole.SCORING_OPERATOR,
            granted_by="admin@itsnotai.com",
        )
        pack = protocol.create_evidence_pack(
            suite_id="fablebreaker",
            candidate_name="test_candidate",
            candidate_source_ref="deadbeef",
            certified=True,
            speedup=2.5,
            governance_version=gov,
            operator_role=role,
        )
        self.assertTrue(pack.verify_integrity())
        self.assertTrue(pack.certified)

    def test_role_separation(self) -> None:
        protocol = GovernanceCertificationProtocol()
        role = protocol.grant_role(
            operator="operator@example.com",
            role=GovernanceRole.SCORING_OPERATOR,
            granted_by="admin@itsnotai.com",
        )
        self.assertTrue(protocol.validate_role_separation("author@example.com", role))
        self.assertFalse(protocol.validate_role_separation("operator@example.com", role))

    def test_threat_model(self) -> None:
        self.assertEqual(len(GovernanceCertificationProtocol.THREAT_MODEL), 7)


class TestPerFamilyScoringProtocol(unittest.TestCase):
    def test_compute_basic(self) -> None:
        protocol = PerFamilyScoringProtocol()
        cases = [
            {"id": "case-0", "family": "overflow_corridor"},
            {"id": "case-1", "family": "overflow_corridor"},
            {"id": "case-2", "family": "nested_conditional_cascade"},
        ]
        candidate_times = [0.001, 0.002, 0.0015]
        baseline_times = [0.003, 0.004, 0.003]
        failures: list[dict[str, str]] = []

        report = protocol.compute(cases, candidate_times, baseline_times, failures)
        self.assertTrue(report.certified)
        self.assertEqual(report.aggregate_total, 3)
        self.assertEqual(len(report.families), 2)

    def test_failing_families(self) -> None:
        protocol = PerFamilyScoringProtocol()
        cases = [
            {"id": "case-0", "family": "overflow_corridor"},
            {"id": "case-1", "family": "nested_conditional_cascade"},
        ]
        candidate_times = [0.001, 0.002]
        baseline_times = [0.003, 0.004]
        failures = [{"id": "case-0", "reason": "wrong_hash"}]

        report = protocol.compute(cases, candidate_times, baseline_times, failures)
        self.assertFalse(report.certified)
        failing = report.failing_families()
        self.assertEqual(len(failing), 1)
        self.assertEqual(failing[0].family, "overflow_corridor")

    def test_min_sample_recommendation(self) -> None:
        protocol = PerFamilyScoringProtocol()
        rec = protocol.minimum_sample_recommendation(10)
        self.assertFalse(rec["sufficient"])
        self.assertEqual(rec["additional_needed"], 10)


class TestAPIReproducibilityProtocol(unittest.TestCase):
    def test_endpoint_catalog(self) -> None:
        protocol = APIReproducibilityProtocol()
        catalog = protocol.endpoint_catalog
        self.assertGreater(len(catalog), 0)
        paths = [e.path for e in catalog]
        self.assertIn("/api/v1/health", paths)
        self.assertIn("/api/v1/score", paths)
        self.assertIn("/api/v1/generate", paths)

    def test_connection_failure_handled(self) -> None:
        # Use a port that's not listening
        protocol = APIReproducibilityProtocol(base_url="http://127.0.0.1:19999")
        resp = protocol.health()
        self.assertFalse(resp.ok)
        self.assertEqual(resp.status_code, 0)
        self.assertIn("error", resp.body)


if __name__ == "__main__":
    unittest.main()
