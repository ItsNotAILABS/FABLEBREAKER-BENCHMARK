from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from .astlang import digest, evaluate


TAGS = ("A", "B", "C", "DEL", "KEEP", "NIL", "WRAP", "SKIP")


def lit(value: int) -> dict[str, Any]:
    return {"op": "lit", "value": int(value)}


def var(name: str) -> dict[str, Any]:
    return {"op": "var", "name": name}


def binop(op: str, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {"op": op, "left": left, "right": right}


def neg(expr: dict[str, Any]) -> dict[str, Any]:
    return {"op": "neg", "value": expr}


def abs_op(expr: dict[str, Any]) -> dict[str, Any]:
    return {"op": "abs", "value": expr}


def if_zero(cond: dict[str, Any], then: dict[str, Any], else_: dict[str, Any]) -> dict[str, Any]:
    return {"op": "if_zero", "cond": cond, "then": then, "else": else_}


def make_case(rng: random.Random, idx: int, split: str) -> dict[str, Any]:
    family = rng.choice(
        [
            "dynamic_match_storm",
            "del_erasure_trap",
            "duplication_aliasing",
            "branch_balance",
            "deep_pair_projection",
            "modular_arithmetic_net",
            "overflow_corridor",
            "nested_conditional_cascade",
        ]
    )
    size = rng.randint(12, 70) if split == "public" else rng.randint(25, 120)
    expr = CASE_BUILDERS[family](rng, size)
    value, stats = evaluate(expr)
    return {
        "id": f"{split}-{idx:04d}-{family}",
        "split": split,
        "family": family,
        "size_hint": size,
        "expr": expr,
        "expected_sha256": digest(value),
        "reference_steps": stats.steps,
        "reference_max_depth": stats.max_depth,
    }


def dynamic_match_storm(rng: random.Random, size: int) -> dict[str, Any]:
    expr: dict[str, Any] = lit(rng.randint(1, 97))
    for i in range(size):
        tag = rng.choice(TAGS[:3])
        expr = {
            "op": "match",
            "value": {"op": "tag", "name": tag, "value": expr},
            "bind": f"x{i}",
            "cases": {
                "A": binop("add", var(f"x{i}"), lit(i + 1)),
                "B": binop("xor", var(f"x{i}"), lit(i * 3 + 7)),
                "C": binop("mod", binop("mul", var(f"x{i}"), lit(3)), lit(997)),
            },
        }
    return expr


def simple_cases(name: str, salt: int) -> dict[str, Any]:
    return {
        "A": binop("add", var(name), lit(salt + 11)),
        "B": binop("xor", var(name), lit((salt * 13) & 255)),
        "C": binop("mod", binop("mul", var(name), lit(salt + 3)), lit(4099)),
    }


def del_erasure_trap(rng: random.Random, size: int) -> dict[str, Any]:
    body: dict[str, Any] = lit(rng.randint(10, 100))
    for i in range(size):
        hidden = {"op": "bomb", "label": f"erased-{i}"}
        body = {
            "op": "erase",
            "value": hidden,
            "body": binop(rng.choice(["add", "xor", "mod"]), body, lit(rng.randint(1, 2048))),
        }
    return body


def duplication_aliasing(rng: random.Random, size: int) -> dict[str, Any]:
    seed = {"op": "pair", "left": lit(rng.randint(1, 50)), "right": lit(rng.randint(51, 100))}
    body: dict[str, Any] = var("root")
    for i in range(size):
        name_l = f"l{i}"
        name_r = f"r{i}"
        projection = {"op": rng.choice(["fst", "snd"]), "value": var(name_l)}
        sibling = {"op": rng.choice(["fst", "snd"]), "value": var(name_r)}
        body = {
            "op": "dup",
            "value": body,
            "left_name": name_l,
            "right_name": name_r,
            "body": {"op": "pair", "left": projection, "right": sibling},
        }
    return {"op": "let", "name": "root", "value": seed, "body": fold_pair_to_int(body, size)}


def fold_pair_to_int(expr: dict[str, Any], size: int) -> dict[str, Any]:
    acc: dict[str, Any] = lit(0)
    current = expr
    for i in range(min(size, 40)):
        name = f"p{i}"
        acc = {
            "op": "let",
            "name": name,
            "value": current,
            "body": binop("add", {"op": "fst", "value": var(name)}, {"op": "snd", "value": var(name)}),
        }
        current = {"op": "pair", "left": acc, "right": lit(i)}
    return acc


def branch_balance(rng: random.Random, size: int) -> dict[str, Any]:
    expr: dict[str, Any] = lit(rng.randint(0, 31))
    for i in range(size):
        tag = "KEEP" if i % 5 else "DEL"
        tagged = {"op": "tag", "name": tag, "value": expr}
        expr = {
            "op": "match",
            "value": tagged,
            "bind": f"q{i}",
            "cases": {
                "KEEP": binop("add", var(f"q{i}"), lit(i + 1)),
                "DEL": {"op": "erase", "value": {"op": "bomb", "label": f"dead-branch-{i}"}, "body": binop("xor", var(f"q{i}"), lit(i + 9))},
            },
        }
    return expr


def deep_pair_projection(rng: random.Random, size: int) -> dict[str, Any]:
    expr: dict[str, Any] = lit(rng.randint(1, 255))
    path = []
    for i in range(size):
        if rng.random() < 0.5:
            expr = {"op": "pair", "left": expr, "right": lit(i)}
            path.append("fst")
        else:
            expr = {"op": "pair", "left": lit(i), "right": expr}
            path.append("snd")
    for step in reversed(path):
        expr = {"op": step, "value": expr}
    return expr


def modular_arithmetic_net(rng: random.Random, size: int) -> dict[str, Any]:
    count = rng.randint(20, 180) + size
    body = binop(
        "mod",
        binop("xor", binop("mul", var("acc"), lit(rng.randint(3, 19))), var("i")),
        lit(rng.choice([257, 997, 4099, 65537])),
    )
    return {
        "op": "repeat",
        "count": lit(count),
        "seed": lit(rng.randint(1, 1000)),
        "index_name": "i",
        "acc_name": "acc",
        "body": body,
    }


def overflow_corridor(rng: random.Random, size: int) -> dict[str, Any]:
    """Generate expressions that push values through overflow-prone corridors.

    Tests candidates that may incorrectly truncate or clamp large integers.
    Uses alternating multiplication and subtraction with large constants.
    """
    expr: dict[str, Any] = lit(rng.randint(2, 2**16))
    for i in range(size):
        choice = rng.choice(["grow", "shrink", "flip", "fold"])
        if choice == "grow":
            expr = binop("mul", expr, lit(rng.randint(2, 127)))
        elif choice == "shrink":
            expr = binop("mod", expr, lit(rng.choice([65537, 104729, 1000003])))
        elif choice == "flip":
            expr = binop("xor", expr, lit(rng.randint(2**15, 2**31)))
        else:
            expr = binop("sub", expr, lit(rng.randint(1, 2**20)))
        if i % 7 == 0:
            expr = abs_op(expr)
        if i % 11 == 0:
            expr = neg(expr)
    return expr


def nested_conditional_cascade(rng: random.Random, size: int) -> dict[str, Any]:
    """Generate deeply nested if_zero cascades with erasure traps.

    Tests candidates that may incorrectly evaluate both branches of conditionals
    or fail to respect zero-testing semantics across deeply nested structures.
    Uses let-bindings to keep evaluation cost linear.
    """
    expr: dict[str, Any] = lit(rng.randint(0, 50))
    for i in range(size):
        name = f"v{i}"
        strategy = rng.choice(["if_zero", "if_zero", "erase_gate"])
        if strategy == "if_zero":
            then_val = binop("add", var(name), lit(rng.randint(1, 50)))
            else_val = binop("xor", var(name), lit(rng.randint(1, 255)))
            body = if_zero(
                binop("mod", var(name), lit(rng.choice([2, 3, 5, 7]))),
                then_val,
                else_val,
            )
            expr = {"op": "let", "name": name, "value": expr, "body": body}
        else:
            body = {
                "op": "erase",
                "value": {"op": "bomb", "label": f"cascade-trap-{i}"},
                "body": binop(rng.choice(["add", "xor"]), var(name), lit(i + 7)),
            }
            expr = {"op": "let", "name": name, "value": expr, "body": body}
    return expr


CASE_BUILDERS = {
    "dynamic_match_storm": dynamic_match_storm,
    "del_erasure_trap": del_erasure_trap,
    "duplication_aliasing": duplication_aliasing,
    "branch_balance": branch_balance,
    "deep_pair_projection": deep_pair_projection,
    "modular_arithmetic_net": modular_arithmetic_net,
    "overflow_corridor": overflow_corridor,
    "nested_conditional_cascade": nested_conditional_cascade,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=240)
    parser.add_argument("--seed", type=int, default=823)
    parser.add_argument("--split", choices=["public", "hidden"], default="public")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for idx in range(args.count):
            handle.write(json.dumps(make_case(rng, idx, args.split), sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
