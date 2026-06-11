from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


class EvalError(RuntimeError):
    pass


@dataclass(frozen=True)
class EvalStats:
    steps: int
    max_depth: int


class Budget:
    def __init__(self, max_steps: int = 2_000_000) -> None:
        self.max_steps = max_steps
        self.steps = 0
        self.max_depth = 0

    def tick(self, depth: int) -> None:
        self.steps += 1
        if depth > self.max_depth:
            self.max_depth = depth
        if self.steps > self.max_steps:
            raise EvalError(f"step budget exceeded: {self.max_steps}")


def canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [canonical(item) for item in value]
    if isinstance(value, tuple):
        tag = value[0]
        if tag == "tag":
            return {"tag": value[1], "value": canonical(value[2])}
        if tag == "pair":
            return {"pair": [canonical(value[1]), canonical(value[2])]}
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in sorted(value.items())}
    raise TypeError(f"cannot canonicalize {type(value).__name__}")


def digest(value: Any) -> str:
    payload = json.dumps(canonical(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate(expr: dict[str, Any], max_steps: int = 2_000_000) -> tuple[Any, EvalStats]:
    budget = Budget(max_steps=max_steps)
    value = _eval(expr, {}, budget, 0)
    return value, EvalStats(steps=budget.steps, max_depth=budget.max_depth)


def _eval(expr: dict[str, Any], env: dict[str, Any], budget: Budget, depth: int) -> Any:
    budget.tick(depth)
    op = expr["op"]

    if op == "lit":
        return int(expr["value"])
    if op == "var":
        name = expr["name"]
        if name not in env:
            raise EvalError(f"unbound variable: {name}")
        return env[name]
    if op == "pair":
        return ("pair", _eval(expr["left"], env, budget, depth + 1), _eval(expr["right"], env, budget, depth + 1))
    if op == "tag":
        return ("tag", expr["name"], _eval(expr["value"], env, budget, depth + 1))
    if op == "add":
        return _as_int(_eval(expr["left"], env, budget, depth + 1)) + _as_int(_eval(expr["right"], env, budget, depth + 1))
    if op == "mul":
        return _as_int(_eval(expr["left"], env, budget, depth + 1)) * _as_int(_eval(expr["right"], env, budget, depth + 1))
    if op == "xor":
        return _as_int(_eval(expr["left"], env, budget, depth + 1)) ^ _as_int(_eval(expr["right"], env, budget, depth + 1))
    if op == "mod":
        right = max(1, abs(_as_int(_eval(expr["right"], env, budget, depth + 1))))
        return _as_int(_eval(expr["left"], env, budget, depth + 1)) % right
    if op == "let":
        next_env = dict(env)
        next_env[expr["name"]] = _eval(expr["value"], env, budget, depth + 1)
        return _eval(expr["body"], next_env, budget, depth + 1)
    if op == "erase":
        # The erased value must not be evaluated. Several cases hide failing or explosive expressions here.
        return _eval(expr["body"], env, budget, depth + 1)
    if op == "dup":
        value = _eval(expr["value"], env, budget, depth + 1)
        next_env = dict(env)
        next_env[expr["left_name"]] = value
        next_env[expr["right_name"]] = value
        return _eval(expr["body"], next_env, budget, depth + 1)
    if op == "fst":
        pair = _eval(expr["value"], env, budget, depth + 1)
        if not isinstance(pair, tuple) or pair[0] != "pair":
            raise EvalError("fst expects pair")
        return pair[1]
    if op == "snd":
        pair = _eval(expr["value"], env, budget, depth + 1)
        if not isinstance(pair, tuple) or pair[0] != "pair":
            raise EvalError("snd expects pair")
        return pair[2]
    if op == "match":
        tagged = _eval(expr["value"], env, budget, depth + 1)
        if not isinstance(tagged, tuple) or tagged[0] != "tag":
            raise EvalError("match expects tagged value")
        _, tag_name, payload = tagged
        cases = expr["cases"]
        if tag_name not in cases:
            if "default" not in expr:
                raise EvalError(f"missing match case: {tag_name}")
            arm = expr["default"]
        else:
            arm = cases[tag_name]
        next_env = dict(env)
        next_env[expr["bind"]] = payload
        return _eval(arm, next_env, budget, depth + 1)
    if op == "repeat":
        count = max(0, min(100_000, _as_int(_eval(expr["count"], env, budget, depth + 1))))
        acc = _eval(expr["seed"], env, budget, depth + 1)
        for i in range(count):
            budget.tick(depth + 1)
            next_env = dict(env)
            next_env[expr["index_name"]] = i
            next_env[expr["acc_name"]] = acc
            acc = _eval(expr["body"], next_env, budget, depth + 1)
        return acc
    if op == "bomb":
        raise EvalError(f"bomb evaluated: {expr.get('label', 'unlabeled')}")
    raise EvalError(f"unknown op: {op}")


def _as_int(value: Any) -> int:
    if not isinstance(value, int):
        raise EvalError(f"expected int, got {type(value).__name__}")
    return value
