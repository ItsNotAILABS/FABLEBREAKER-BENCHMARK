"""Example: How to wrap your own agent code for FableBreaker batch testing.

This file shows how to integrate your own agents (30-100 of them) into
FableBreaker's batch audit system. Each candidate just needs one function:

    def evaluate(expr: dict) -> object

You can:
1. Copy this template for each agent
2. Wrap your real logic inside evaluate()
3. Run: python -m tools.batch_audit --discover candidates

For external repos, FableBreaker's repo_scanner will auto-detect any .py file
with a `def evaluate` function. Just point it at your code:

    python -m tools.batch_audit --scan-dirs /path/to/my/agents/repo
"""
from __future__ import annotations

from fablebreaker.astlang import canonical, evaluate as reference_evaluate


def evaluate(expr: dict) -> object:
    """Wrap your agent's real logic here.

    This example just calls the reference evaluator, but in practice you'd
    replace this with YOUR optimized version — the one your 30 agents produced.

    FableBreaker will:
    - Hash the output with SHA-256
    - Compare against the reference
    - If ANY case mismatches: your agent gets ZERO certification
    - If all correct: measure speedup vs reference

    Example of wrapping real agent code:
        from my_agent_framework import AgentPool
        pool = AgentPool(num_agents=30)
        result = pool.evaluate_expression(expr)
        return canonical(result)
    """
    value, _stats = reference_evaluate(expr)
    return canonical(value)
