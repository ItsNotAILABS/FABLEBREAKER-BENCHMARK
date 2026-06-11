from __future__ import annotations

import random
import unittest

from fablebreaker.astlang import Budget, EvalError, EvalStats, canonical, digest, evaluate


class TestBudgetEnforcement(unittest.TestCase):
    def test_budget_exceeded_on_large_nested_repeat(self) -> None:
        expr = {
            "op": "repeat",
            "count": {"op": "lit", "value": 100000},
            "seed": {"op": "lit", "value": 0},
            "index_name": "i",
            "acc_name": "acc",
            "body": {
                "op": "repeat",
                "count": {"op": "lit", "value": 100},
                "seed": {"op": "var", "name": "acc"},
                "index_name": "j",
                "acc_name": "inner",
                "body": {"op": "add", "left": {"op": "var", "name": "inner"}, "right": {"op": "lit", "value": 1}},
            },
        }
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("budget", str(ctx.exception))

    def test_repeat_count_clamped_to_100000(self) -> None:
        expr = {
            "op": "repeat",
            "count": {"op": "lit", "value": 200000},
            "seed": {"op": "lit", "value": 0},
            "index_name": "i",
            "acc_name": "acc",
            "body": {"op": "var", "name": "acc"},
        }
        value, stats = evaluate(expr)
        self.assertEqual(value, 0)
        # 1 entry + 1 count_eval + 1 seed_eval + 100000*2 (tick + body_eval) = 200003
        self.assertEqual(stats.steps, 200003)

    def test_repeat_negative_count_clamped_to_zero(self) -> None:
        expr = {
            "op": "repeat",
            "count": {"op": "lit", "value": -5},
            "seed": {"op": "lit", "value": 42},
            "index_name": "i",
            "acc_name": "acc",
            "body": {"op": "lit", "value": 999},
        }
        value, _stats = evaluate(expr)
        self.assertEqual(value, 42)

    def test_custom_budget_limit(self) -> None:
        expr = {
            "op": "repeat",
            "count": {"op": "lit", "value": 100},
            "seed": {"op": "lit", "value": 0},
            "index_name": "i",
            "acc_name": "acc",
            "body": {"op": "var", "name": "acc"},
        }
        with self.assertRaises(EvalError):
            evaluate(expr, max_steps=50)


class TestEvaluatorOperations(unittest.TestCase):
    def test_mod_by_zero_uses_abs_max_one(self) -> None:
        expr = {"op": "mod", "left": {"op": "lit", "value": 10}, "right": {"op": "lit", "value": 0}}
        value, _ = evaluate(expr)
        self.assertEqual(value, 0)  # 10 % max(1, abs(0)) = 10 % 1 = 0

    def test_mod_by_negative_uses_abs(self) -> None:
        expr = {"op": "mod", "left": {"op": "lit", "value": 10}, "right": {"op": "lit", "value": -3}}
        value, _ = evaluate(expr)
        self.assertEqual(value, 1)  # 10 % 3 = 1

    def test_xor_operation(self) -> None:
        expr = {"op": "xor", "left": {"op": "lit", "value": 0b1100}, "right": {"op": "lit", "value": 0b1010}}
        value, _ = evaluate(expr)
        self.assertEqual(value, 0b0110)

    def test_unbound_variable_raises(self) -> None:
        expr = {"op": "var", "name": "nonexistent"}
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("unbound", str(ctx.exception))

    def test_fst_on_non_pair_raises(self) -> None:
        expr = {"op": "fst", "value": {"op": "lit", "value": 42}}
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("pair", str(ctx.exception))

    def test_snd_on_non_pair_raises(self) -> None:
        expr = {"op": "snd", "value": {"op": "lit", "value": 42}}
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("pair", str(ctx.exception))

    def test_match_missing_case_raises(self) -> None:
        expr = {
            "op": "match",
            "value": {"op": "tag", "name": "X", "value": {"op": "lit", "value": 1}},
            "bind": "v",
            "cases": {"A": {"op": "lit", "value": 0}},
        }
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("missing match case", str(ctx.exception))

    def test_match_default_case(self) -> None:
        expr = {
            "op": "match",
            "value": {"op": "tag", "name": "X", "value": {"op": "lit", "value": 5}},
            "bind": "v",
            "cases": {"A": {"op": "lit", "value": 0}},
            "default": {"op": "add", "left": {"op": "var", "name": "v"}, "right": {"op": "lit", "value": 10}},
        }
        value, _ = evaluate(expr)
        self.assertEqual(value, 15)

    def test_match_on_non_tagged_raises(self) -> None:
        expr = {
            "op": "match",
            "value": {"op": "lit", "value": 42},
            "bind": "v",
            "cases": {"A": {"op": "lit", "value": 0}},
        }
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("tagged", str(ctx.exception))

    def test_unknown_op_raises(self) -> None:
        expr = {"op": "unknown_op"}
        with self.assertRaises(EvalError) as ctx:
            evaluate(expr)
        self.assertIn("unknown op", str(ctx.exception))

    def test_dup_shares_value(self) -> None:
        expr = {
            "op": "dup",
            "value": {"op": "lit", "value": 7},
            "left_name": "a",
            "right_name": "b",
            "body": {"op": "add", "left": {"op": "var", "name": "a"}, "right": {"op": "var", "name": "b"}},
        }
        value, _ = evaluate(expr)
        self.assertEqual(value, 14)

    def test_let_scoping(self) -> None:
        expr = {
            "op": "let",
            "name": "x",
            "value": {"op": "lit", "value": 10},
            "body": {
                "op": "let",
                "name": "x",
                "value": {"op": "lit", "value": 20},
                "body": {"op": "var", "name": "x"},
            },
        }
        value, _ = evaluate(expr)
        self.assertEqual(value, 20)


class TestCanonicalAndDigest(unittest.TestCase):
    def test_canonical_idempotent_for_int(self) -> None:
        self.assertEqual(canonical(42), 42)
        self.assertEqual(canonical(canonical(42)), 42)

    def test_canonical_idempotent_for_pair(self) -> None:
        val = ("pair", 1, 2)
        c1 = canonical(val)
        c2 = canonical(c1)
        self.assertEqual(c1, c2)

    def test_canonical_idempotent_for_tag(self) -> None:
        val = ("tag", "A", 42)
        c1 = canonical(val)
        c2 = canonical(c1)
        self.assertEqual(c1, c2)

    def test_canonical_nested_pair(self) -> None:
        val = ("pair", ("pair", 1, 2), ("tag", "X", 3))
        result = canonical(val)
        self.assertEqual(result, {"pair": [{"pair": [1, 2]}, {"tag": "X", "value": 3}]})

    def test_canonical_raises_on_unsupported(self) -> None:
        with self.assertRaises(TypeError):
            canonical(3.14)

    def test_digest_deterministic(self) -> None:
        val = ("pair", 1, ("tag", "A", 2))
        h1 = digest(val)
        h2 = digest(val)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_digest_different_for_different_values(self) -> None:
        h1 = digest(1)
        h2 = digest(2)
        self.assertNotEqual(h1, h2)


class TestGeneratorReproducibility(unittest.TestCase):
    def test_same_seed_produces_same_cases(self) -> None:
        from fablebreaker.generator import make_case

        rng1 = random.Random(12345)
        rng2 = random.Random(12345)
        for i in range(20):
            c1 = make_case(rng1, i, "public")
            c2 = make_case(rng2, i, "public")
            self.assertEqual(c1["expected_sha256"], c2["expected_sha256"])
            self.assertEqual(c1["family"], c2["family"])
            self.assertEqual(c1["id"], c2["id"])

    def test_different_seeds_produce_different_cases(self) -> None:
        from fablebreaker.generator import make_case

        rng1 = random.Random(111)
        rng2 = random.Random(222)
        case1 = make_case(rng1, 0, "public")
        case2 = make_case(rng2, 0, "public")
        # Very unlikely to have same hash with different seeds
        self.assertNotEqual(case1["expected_sha256"], case2["expected_sha256"])

    def test_all_families_covered_in_large_sample(self) -> None:
        from fablebreaker.generator import CASE_BUILDERS, make_case

        rng = random.Random(42)
        families_seen = set()
        for i in range(100):
            case = make_case(rng, i, "public")
            families_seen.add(case["family"])
        self.assertEqual(families_seen, set(CASE_BUILDERS.keys()))


class TestDepthTracking(unittest.TestCase):
    def test_depth_tracked_for_nested_lets(self) -> None:
        expr = {"op": "lit", "value": 1}
        for i in range(10):
            expr = {"op": "let", "name": f"x{i}", "value": {"op": "lit", "value": i}, "body": expr}
        _, stats = evaluate(expr)
        self.assertEqual(stats.max_depth, 10)

    def test_depth_tracked_for_pairs(self) -> None:
        expr = {"op": "pair", "left": {"op": "lit", "value": 1}, "right": {"op": "lit", "value": 2}}
        for _ in range(5):
            expr = {"op": "pair", "left": expr, "right": {"op": "lit", "value": 0}}
        _, stats = evaluate(expr)
        self.assertGreaterEqual(stats.max_depth, 6)


if __name__ == "__main__":
    unittest.main()
