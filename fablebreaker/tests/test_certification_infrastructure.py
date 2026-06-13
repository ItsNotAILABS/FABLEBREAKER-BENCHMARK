from __future__ import annotations

import json
import os
import random
import tempfile
import unittest
from pathlib import Path

from fablebreaker.astlang import digest, evaluate
from fablebreaker.evidence import generate_evidence_pack, save_evidence_pack
from fablebreaker.generator import make_case
from fablebreaker.leaderboard import Leaderboard
from fablebreaker.regression import RegressionMonitor
from fablebreaker.scorer import score
from fablebreaker.seeds import SeedRegistry, commit_seed


class TestSeedRegistry(unittest.TestCase):
    def test_register_and_retrieve(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            registry = SeedRegistry(path)
            entry = registry.register_seed(1701)
            self.assertEqual(entry.seed, 1701)
            self.assertEqual(entry.commitment, commit_seed(1701))
            self.assertEqual(entry.status, "active")
            active = registry.active_seeds()
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0].seed, 1701)
        finally:
            path.unlink(missing_ok=True)

    def test_rotate_retires_old(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            registry = SeedRegistry(path)
            registry.register_seed(100)
            new_entry = registry.rotate(999)
            self.assertEqual(new_entry.seed, 999)
            active = registry.active_seeds()
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0].seed, 999)
        finally:
            path.unlink(missing_ok=True)

    def test_commitments_are_deterministic(self) -> None:
        c1 = commit_seed(42)
        c2 = commit_seed(42)
        self.assertEqual(c1, c2)
        self.assertNotEqual(commit_seed(42), commit_seed(43))

    def test_persistence(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            registry = SeedRegistry(path)
            registry.register_seed(555)
            registry2 = SeedRegistry(path)
            self.assertEqual(len(registry2.active_seeds()), 1)
            self.assertEqual(registry2.active_seeds()[0].seed, 555)
        finally:
            path.unlink(missing_ok=True)


class TestEvidencePack(unittest.TestCase):
    def _make_score(self, certified: bool = True) -> dict:
        return {
            "cases": 10,
            "correct": 10 if certified else 8,
            "failed": 0 if certified else 2,
            "certified": certified,
            "speedup_vs_reference": 1.5 if certified else 0.0,
            "candidate_median_ms": 0.5,
            "candidate_p95_ms": 1.0,
            "family_breakdown": {},
        }

    def test_generate_certified_pack(self) -> None:
        pack = generate_evidence_pack(
            candidate_name="test_candidate",
            candidate_source_ref="abc123",
            public_score=self._make_score(True),
            hidden_score=self._make_score(True),
            public_seed=823,
            hidden_seed=1701,
        )
        self.assertTrue(pack["overall_certified"])
        self.assertAlmostEqual(pack["overall_speedup"], 1.5)
        self.assertEqual(pack["total_cases"], 20)
        self.assertIn("content_hash", pack)

    def test_generate_failed_pack(self) -> None:
        pack = generate_evidence_pack(
            candidate_name="bad_candidate",
            candidate_source_ref="def456",
            public_score=self._make_score(True),
            hidden_score=self._make_score(False),
            public_seed=823,
            hidden_seed=1701,
        )
        self.assertFalse(pack["overall_certified"])
        self.assertEqual(pack["overall_speedup"], 0.0)

    def test_save_and_read(self) -> None:
        pack = generate_evidence_pack(
            candidate_name="test",
            candidate_source_ref="",
            public_score=self._make_score(True),
            hidden_score=self._make_score(True),
            public_seed=823,
            hidden_seed=1701,
        )
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            save_evidence_pack(pack, path)
            loaded = json.loads(path.read_text())
            self.assertEqual(loaded["candidate_name"], "test")
            self.assertTrue(loaded["overall_certified"])
        finally:
            path.unlink(missing_ok=True)


class TestLeaderboard(unittest.TestCase):
    def _make_pack(self, name: str, speedup: float, certified: bool = True) -> dict:
        return {
            "candidate_name": name,
            "overall_certified": certified,
            "overall_speedup": speedup,
            "total_cases": 480,
            "total_correct": 480 if certified else 470,
            "total_failed": 0 if certified else 10,
            "timestamp_utc": "2024-01-01T00:00:00Z",
            "operator": "test",
            "content_hash": "abc123",
            "candidate_source_ref": "",
        }

    def test_submit_and_rank(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        os.unlink(path)
        try:
            lb = Leaderboard(path)
            lb.submit(self._make_pack("fast", 3.0))
            lb.submit(self._make_pack("faster", 5.0))
            lb.submit(self._make_pack("broken", 10.0, certified=False))
            ranked = lb.ranked(certified_only=True)
            self.assertEqual(len(ranked), 2)
            self.assertEqual(ranked[0].candidate_name, "faster")
            self.assertEqual(ranked[1].candidate_name, "fast")
        finally:
            path.unlink(missing_ok=True)

    def test_to_dict(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        os.unlink(path)
        try:
            lb = Leaderboard(path)
            lb.submit(self._make_pack("alpha", 2.0))
            result = lb.to_dict()
            self.assertEqual(result["total_submissions"], 1)
            self.assertEqual(result["leaderboard"][0]["rank"], 1)
        finally:
            path.unlink(missing_ok=True)


class TestRegressionMonitor(unittest.TestCase):
    def _make_pack(self, speedup: float, certified: bool = True, failed: int = 0) -> dict:
        return {
            "candidate_name": "test_candidate",
            "timestamp_utc": "2024-01-01T00:00:00Z",
            "overall_certified": certified,
            "overall_speedup": speedup,
            "total_cases": 480,
            "total_failed": failed,
            "public_seed": 823,
            "hidden_seed_commitment": "abc",
        }

    def test_record_and_detect_regression(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        os.unlink(path)
        try:
            monitor = RegressionMonitor(path)
            monitor.record_from_pack(self._make_pack(3.0, True))
            result = monitor.detect_regression("test_candidate", self._make_pack(1.0, True))
            self.assertTrue(result["regression"])
            self.assertIn("speedup_dropped", result["issues"][0])
        finally:
            path.unlink(missing_ok=True)

    def test_no_regression_on_improvement(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        os.unlink(path)
        try:
            monitor = RegressionMonitor(path)
            monitor.record_from_pack(self._make_pack(2.0, True))
            result = monitor.detect_regression("test_candidate", self._make_pack(4.0, True))
            self.assertFalse(result["regression"])
        finally:
            path.unlink(missing_ok=True)

    def test_certification_loss_is_regression(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = Path(tmp.name)
        os.unlink(path)
        try:
            monitor = RegressionMonitor(path)
            monitor.record_from_pack(self._make_pack(3.0, True))
            result = monitor.detect_regression("test_candidate", self._make_pack(0.0, False, failed=5))
            self.assertTrue(result["regression"])
            self.assertIn("certification_lost", result["issues"])
        finally:
            path.unlink(missing_ok=True)


class TestScorerFamilyDiagnostics(unittest.TestCase):
    def test_score_produces_family_breakdown(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as tmp:
            rng = random.Random(823)
            for idx in range(10):
                case = make_case(rng, idx, "public")
                tmp.write(json.dumps(case, sort_keys=True) + "\n")
            path = Path(tmp.name)
        try:
            result = score(path, "candidates.baseline_candidate", repeat=1)
            self.assertIn("family_breakdown", result)
            self.assertTrue(result["certified"])
            diag = result["family_breakdown"]
            self.assertGreater(len(diag), 0)
            for family_name, family_data in diag.items():
                self.assertIn("count", family_data)
                self.assertIn("correct", family_data)
                self.assertIn("speedup", family_data)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
