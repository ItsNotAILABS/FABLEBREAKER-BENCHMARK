"""
Correctness Engine — the heart of Fablebreaker.

Evaluates whether a system's outputs are semantically correct,
not just fast. Speed without correctness is marketing.
"""

from __future__ import annotations

from typing import Any

from .base import Engine, EngineResult, EngineStatus


class CorrectnessEngine(Engine):
    """
    Verifies semantic correctness of AI system outputs.

    This engine enforces Fablebreaker's core principle:
    correctness before speed, proof before claims.
    """

    def __init__(self) -> None:
        super().__init__(
            name="correctness",
            description="Semantic correctness verification engine. "
                        "Enforces hash-locked output equivalence under adversarial conditions.",
        )

    def execute(self, context: dict[str, Any]) -> EngineResult:
        """
        Evaluate correctness of candidate outputs against reference.

        Context should contain:
        - candidate_outputs: list of outputs from the candidate
        - reference_outputs: list of expected outputs
        - hash_function: optional hash function for comparison
        - tolerance: optional numerical tolerance
        """
        candidate_outputs = context.get("candidate_outputs", [])
        reference_outputs = context.get("reference_outputs", [])

        if not candidate_outputs or not reference_outputs:
            return EngineResult(
                engine_name=self.name,
                status=EngineStatus.COMPLETE,
                verdict="insufficient_data",
                confidence=0.0,
                metadata={"reason": "No outputs provided for comparison"},
            )

        if len(candidate_outputs) != len(reference_outputs):
            return EngineResult(
                engine_name=self.name,
                status=EngineStatus.COMPLETE,
                verdict="length_mismatch",
                confidence=1.0,
                findings=[{
                    "type": "output_count_mismatch",
                    "candidate_count": len(candidate_outputs),
                    "reference_count": len(reference_outputs),
                }],
            )

        total = len(candidate_outputs)
        correct = 0
        failures = []

        for idx, (candidate, reference) in enumerate(
            zip(candidate_outputs, reference_outputs)
        ):
            if self._outputs_match(candidate, reference, context):
                correct += 1
            else:
                failures.append({
                    "index": idx,
                    "candidate": str(candidate)[:200],
                    "reference": str(reference)[:200],
                    "type": "semantic_mismatch",
                })

        pass_rate = correct / total if total > 0 else 0.0
        certified = len(failures) == 0

        verdict = "certified" if certified else "failed"

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict=verdict,
            confidence=pass_rate,
            findings=failures[:50],
            metadata={
                "total_cases": total,
                "correct": correct,
                "failed": len(failures),
                "pass_rate": pass_rate,
                "certified": certified,
            },
        )

    def _outputs_match(
        self, candidate: Any, reference: Any, context: dict[str, Any]
    ) -> bool:
        """Compare outputs for semantic equivalence."""
        hash_fn = context.get("hash_function")
        if hash_fn:
            return hash_fn(candidate) == hash_fn(reference)

        tolerance = context.get("tolerance")
        if tolerance and isinstance(candidate, (int, float)) and isinstance(reference, (int, float)):
            return abs(candidate - reference) <= tolerance

        return candidate == reference
