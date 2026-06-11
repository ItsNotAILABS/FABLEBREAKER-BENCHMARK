from __future__ import annotations

from fablebreaker.astlang import canonical, evaluate as reference_evaluate


def evaluate(expr: dict) -> object:
    value, _stats = reference_evaluate(expr)
    return canonical(value)
