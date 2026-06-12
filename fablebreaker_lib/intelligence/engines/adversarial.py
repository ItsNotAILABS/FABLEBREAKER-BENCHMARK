"""
Adversarial Engine — generates and applies adversarial pressure.

This engine creates adversarial test cases, identifies weaknesses,
and ensures that systems survive hostile conditions.
"""

from __future__ import annotations

import random
from typing import Any

from .base import Engine, EngineResult, EngineStatus


class AdversarialEngine(Engine):
    """
    Generates adversarial pressure to test AI system robustness.

    Uses knowledge of gaming vectors and benchmark limitations
    from the knowledge base to craft targeted attacks.
    """

    def __init__(self) -> None:
        super().__init__(
            name="adversarial",
            description="Adversarial test generation and application engine. "
                        "Crafts targeted attacks based on known gaming vectors.",
        )
        self._attack_families = [
            "data_contamination_probe",
            "format_exploitation",
            "shortcut_detection",
            "boundary_stress",
            "semantic_perturbation",
            "hidden_seed_injection",
            "output_forgery_detection",
            "determinism_violation",
            "resource_exhaustion",
            "correctness_inversion",
        ]

    def execute(self, context: dict[str, Any]) -> EngineResult:
        """
        Generate or apply adversarial evaluation.

        Context can contain:
        - mode: "generate" (create attacks) or "evaluate" (test against attacks)
        - target_domain: domain to attack (from knowledge base)
        - gaming_vectors: known vulnerabilities to exploit
        - seed: random seed for reproducibility
        - intensity: 1-10 scale of adversarial pressure
        """
        mode = context.get("mode", "generate")
        seed = context.get("seed", 42)
        intensity = min(10, max(1, context.get("intensity", 5)))

        if mode == "generate":
            return self._generate_attacks(context, seed, intensity)
        if mode == "evaluate":
            return self._evaluate_resilience(context)
        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.ERROR,
            verdict=f"Unknown mode: {mode}",
        )

    def _generate_attacks(
        self, context: dict[str, Any], seed: int, intensity: int
    ) -> EngineResult:
        """Generate adversarial test cases."""
        rng = random.Random(seed)
        gaming_vectors = context.get("gaming_vectors", [])
        target_domain = context.get("target_domain", "general")

        num_attacks = intensity * 5
        selected_families = rng.choices(self._attack_families, k=num_attacks)

        attacks = []
        for idx, family in enumerate(selected_families):
            attack = {
                "id": f"adv-{seed}-{idx:04d}",
                "family": family,
                "target_domain": target_domain,
                "intensity": intensity,
                "description": self._describe_attack(family, gaming_vectors),
                "seed": seed + idx,
            }
            attacks.append(attack)

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict="attacks_generated",
            confidence=1.0,
            findings=attacks,
            metadata={
                "total_attacks": len(attacks),
                "families_used": list(set(selected_families)),
                "intensity": intensity,
                "target_domain": target_domain,
                "gaming_vectors_exploited": gaming_vectors[:5],
            },
        )

    def _evaluate_resilience(self, context: dict[str, Any]) -> EngineResult:
        """Evaluate a system's resilience against adversarial attacks."""
        attacks = context.get("attacks", [])
        results = context.get("attack_results", [])

        if not attacks or not results:
            return EngineResult(
                engine_name=self.name,
                status=EngineStatus.COMPLETE,
                verdict="no_attacks_to_evaluate",
                confidence=0.0,
            )

        survived = sum(1 for r in results if r.get("survived", False))
        total = len(results)
        survival_rate = survived / total if total > 0 else 0.0

        failed_families: dict[str, int] = {}
        for attack, result in zip(attacks, results):
            if not result.get("survived", False):
                family = attack.get("family", "unknown")
                failed_families[family] = failed_families.get(family, 0) + 1

        verdict = "resilient" if survival_rate >= 1.0 else "vulnerable"

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict=verdict,
            confidence=survival_rate,
            findings=[
                {"family": f, "failures": c}
                for f, c in sorted(failed_families.items(), key=lambda x: x[1], reverse=True)
            ],
            metadata={
                "total_attacks": total,
                "survived": survived,
                "failed": total - survived,
                "survival_rate": survival_rate,
                "weakest_families": list(failed_families.keys())[:5],
            },
        )

    def _describe_attack(self, family: str, gaming_vectors: list[str]) -> str:
        """Generate a description for an attack based on its family."""
        descriptions = {
            "data_contamination_probe": "Tests for memorized benchmark answers via paraphrased inputs",
            "format_exploitation": "Exploits format-specific shortcuts that bypass reasoning",
            "shortcut_detection": "Identifies statistical shortcuts the system relies on",
            "boundary_stress": "Pushes inputs to extreme boundaries of expected ranges",
            "semantic_perturbation": "Applies meaning-preserving perturbations that break fragile systems",
            "hidden_seed_injection": "Uses unseen random seeds to generate novel test cases",
            "output_forgery_detection": "Verifies outputs cannot be trivially forged or cached",
            "determinism_violation": "Checks for non-deterministic behavior across repeated evaluations",
            "resource_exhaustion": "Tests behavior under resource pressure and step limits",
            "correctness_inversion": "Creates cases where the fast answer is wrong",
        }
        base = descriptions.get(family, f"Attack from family: {family}")
        if gaming_vectors:
            base += f" | Exploiting: {gaming_vectors[0]}"
        return base
