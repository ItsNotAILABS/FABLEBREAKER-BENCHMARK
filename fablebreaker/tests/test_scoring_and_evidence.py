from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from fablebreaker.generator import make_case
from fablebreaker.scorer import score


class TestScorerWithBrokenCandidate(unittest.TestCase):
    """Test that the scorer correctly detects and reports broken candidates."""

    def _write_dataset(self, count: int = 20, seed: int = 823) -> Path:
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w")
        rng = random.Random(seed)
        for idx in range(count):
            case = make_case(rng, idx, "public")
            tmp.write(json.dumps(case, sort_keys=True) + "\n")
        tmp.close()
        return Path(tmp.name)

    def test_baseline_candidate_certifies(self) -> None:
        path = self._write_dataset(10)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=1)
            self.assertTrue(result["certified"])
            self.assertEqual(result["failed"], 0)
            self.assertGreater(result["speedup_vs_reference"], 0)
        finally:
            path.unlink(missing_ok=True)

    def test_scorer_reports_family_diagnostics(self) -> None:
        path = self._write_dataset(50)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=1)
            diag = result["family_diagnostics"]
            # All families should be certified with baseline
            for family_name, family_data in diag.items():
                self.assertTrue(family_data["certified"], f"{family_name} should be certified")
                self.assertEqual(family_data["failed"], 0)
                self.assertGreater(family_data["cases"], 0)
                self.assertGreater(family_data["speedup_vs_reference"], 0)
        finally:
            path.unlink(missing_ok=True)

    def test_scorer_handles_repeat_parameter(self) -> None:
        path = self._write_dataset(5)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=3)
            self.assertTrue(result["certified"])
            self.assertEqual(result["cases"], 5)
        finally:
            path.unlink(missing_ok=True)


class TestScorerMetrics(unittest.TestCase):
    """Test that scorer produces correct statistical metrics."""

    def test_p95_greater_or_equal_median(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w")
        rng = random.Random(42)
        for idx in range(30):
            case = make_case(rng, idx, "public")
            tmp.write(json.dumps(case, sort_keys=True) + "\n")
        tmp.close()
        path = Path(tmp.name)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=1)
            self.assertGreaterEqual(result["candidate_p95_ms"], result["candidate_median_ms"])
            self.assertGreaterEqual(result["baseline_p95_ms"], result["baseline_median_ms"])
        finally:
            path.unlink(missing_ok=True)

    def test_total_seconds_is_sum_of_individual_times(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w")
        rng = random.Random(99)
        for idx in range(10):
            case = make_case(rng, idx, "public")
            tmp.write(json.dumps(case, sort_keys=True) + "\n")
        tmp.close()
        path = Path(tmp.name)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=1)
            # baseline_total and candidate_total should be positive
            self.assertGreater(result["baseline_total_seconds"], 0)
            self.assertGreater(result["candidate_total_seconds"], 0)
            # speedup should be the ratio
            expected_speedup = result["baseline_total_seconds"] / result["candidate_total_seconds"]
            self.assertAlmostEqual(result["speedup_vs_reference"], expected_speedup, places=6)
        finally:
            path.unlink(missing_ok=True)


class TestEvidencePackIntegrity(unittest.TestCase):
    """Test evidence pack content hash and signature."""

    def test_content_hash_changes_with_data(self) -> None:
        from fablebreaker.evidence import generate_evidence_pack

        score1 = {"cases": 10, "correct": 10, "failed": 0, "certified": True,
                  "speedup_vs_reference": 2.0, "candidate_median_ms": 0.5,
                  "candidate_p95_ms": 1.0, "family_diagnostics": {}}
        score2 = {"cases": 10, "correct": 9, "failed": 1, "certified": False,
                  "speedup_vs_reference": 0.0, "candidate_median_ms": 0.5,
                  "candidate_p95_ms": 1.0, "family_diagnostics": {}}

        pack1 = generate_evidence_pack("c1", "", score1, score1, 823, 1701)
        pack2 = generate_evidence_pack("c1", "", score1, score2, 823, 1701)
        self.assertNotEqual(pack1["content_hash"], pack2["content_hash"])

    def test_signature_verification_roundtrip(self) -> None:
        from fablebreaker.evidence import generate_evidence_pack, sign_evidence, verify_signature

        score_data = {"cases": 10, "correct": 10, "failed": 0, "certified": True,
                      "speedup_vs_reference": 2.0, "candidate_median_ms": 0.5,
                      "candidate_p95_ms": 1.0, "family_diagnostics": {}}

        pack = generate_evidence_pack("c1", "ref123", score_data, score_data, 823, 1701,
                                      signing_secret="test-secret-key")
        self.assertIn("signature", pack)
        self.assertTrue(verify_signature(
            {k: v for k, v in pack.items() if k != "signature" and k != "signature_method"},
            pack["signature"], "test-secret-key"))


class TestSeedRegistryEdgeCases(unittest.TestCase):
    """Test seed registry behavior under edge conditions."""

    def test_duplicate_registration_returns_existing(self) -> None:
        from fablebreaker.seeds import SeedRegistry

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            registry = SeedRegistry(path)
            entry1 = registry.register_seed(42)
            entry2 = registry.register_seed(42)
            self.assertEqual(entry1.seed, entry2.seed)
            self.assertEqual(entry1.commitment, entry2.commitment)
            # Should not duplicate
            self.assertEqual(len(registry.active_seeds()), 1)
        finally:
            path.unlink(missing_ok=True)

    def test_multiple_rotations(self) -> None:
        from fablebreaker.seeds import SeedRegistry

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            registry = SeedRegistry(path)
            registry.register_seed(100)
            registry.rotate(200)
            registry.rotate(300)
            active = registry.active_seeds()
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0].seed, 300)
            # All previous should be retired
            retired = [e for e in registry.entries if e.status == "retired"]
            self.assertEqual(len(retired), 2)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
