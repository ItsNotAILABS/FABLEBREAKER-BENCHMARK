from __future__ import annotations

import random
import unittest

from fablebreaker.astlang import EvalError, digest, evaluate
from fablebreaker.generator import make_case


class BenchmarkIntegrityTests(unittest.TestCase):
    def test_generated_cases_match_expected_hashes(self) -> None:
        rng = random.Random(823)
        for idx in range(30):
            case = make_case(rng, idx, "public")
            value, stats = evaluate(case["expr"])
            self.assertEqual(digest(value), case["expected_sha256"])
            self.assertEqual(stats.steps, case["reference_steps"])

    def test_erasure_does_not_evaluate_dead_payload(self) -> None:
        expr = {
            "op": "erase",
            "value": {"op": "bomb", "label": "must-not-fire"},
            "body": {"op": "lit", "value": 823},
        }
        value, _stats = evaluate(expr)
        self.assertEqual(value, 823)

    def test_bomb_fires_when_not_erased(self) -> None:
        with self.assertRaises(EvalError):
            evaluate({"op": "bomb", "label": "live"})


if __name__ == "__main__":
    unittest.main()
