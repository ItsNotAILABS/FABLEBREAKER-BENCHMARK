"""
Generation Skill — creates adversarial test cases, datasets, and challenges.
"""

from __future__ import annotations

import random
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class GenerationSkill(Skill):
    """
    Generates adversarial test cases, evaluation datasets, and challenges.

    This skill allows Fablebreaker to actively create new evaluation
    material — it doesn't just consume benchmarks, it produces them.
    """

    def __init__(self) -> None:
        super().__init__(
            name="generation",
            description="Generates adversarial test cases, evaluation datasets, "
                        "and novel challenges. Active creation of evaluation material.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Generate evaluation material.

        Context should contain:
        - generation_type: "adversarial_cases", "dataset", "challenge"
        - domain: target domain
        - seed: random seed for reproducibility
        - count: number of items to generate
        - difficulty: 1-10
        - gaming_vectors: known vectors to exploit (for adversarial generation)
        """
        gen_type = context.get("generation_type", "adversarial_cases")
        seed = context.get("seed", 42)
        count = context.get("count", 10)
        difficulty = min(10, max(1, context.get("difficulty", 5)))
        domain = context.get("domain", "general")

        if gen_type == "adversarial_cases":
            return self._generate_adversarial(seed, count, difficulty, domain, context)
        if gen_type == "dataset":
            return self._generate_dataset(seed, count, domain, context)
        if gen_type == "challenge":
            return self._generate_challenge(seed, difficulty, domain, context)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown generation type: {gen_type}",
        )

    def _generate_adversarial(
        self, seed: int, count: int, difficulty: int, domain: str, context: dict[str, Any]
    ) -> SkillResult:
        """Generate adversarial test cases."""
        rng = random.Random(seed)
        gaming_vectors = context.get("gaming_vectors", [])

        cases = []
        strategies = [
            "boundary_violation",
            "format_break",
            "semantic_trap",
            "memorization_probe",
            "shortcut_invalidation",
            "hidden_complexity",
            "correctness_inversion",
            "resource_pressure",
        ]

        for idx in range(count):
            strategy = rng.choice(strategies)
            case = {
                "id": f"gen-{seed}-{idx:04d}",
                "strategy": strategy,
                "domain": domain,
                "difficulty": difficulty + rng.randint(-1, 1),
                "seed": seed + idx,
                "exploits_vector": rng.choice(gaming_vectors) if gaming_vectors else None,
                "description": f"Adversarial case using {strategy} strategy at difficulty {difficulty}",
            }
            cases.append(case)

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=cases,
            confidence=0.9,
            reasoning=f"Generated {count} adversarial cases for domain '{domain}' at difficulty {difficulty}",
            artifacts=[{"type": "adversarial_cases", "count": count, "seed": seed}],
        )

    def _generate_dataset(
        self, seed: int, count: int, domain: str, context: dict[str, Any]
    ) -> SkillResult:
        """Generate an evaluation dataset."""
        rng = random.Random(seed)

        splits = {
            "public": int(count * 0.6),
            "hidden": int(count * 0.4),
        }

        dataset_spec = {
            "seed": seed,
            "domain": domain,
            "total_cases": count,
            "splits": splits,
            "families": self._select_families(domain, rng),
            "reproducible": True,
            "hash_locked": True,
        }

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=dataset_spec,
            confidence=1.0,
            reasoning=f"Generated dataset specification for {count} cases in domain '{domain}'",
            artifacts=[{"type": "dataset_spec", "cases": count, "domain": domain}],
        )

    def _generate_challenge(
        self, seed: int, difficulty: int, domain: str, context: dict[str, Any]
    ) -> SkillResult:
        """Generate a complete evaluation challenge."""
        challenge = {
            "seed": seed,
            "domain": domain,
            "difficulty": difficulty,
            "phases": [
                {"name": "public_evaluation", "cases": difficulty * 50},
                {"name": "hidden_evaluation", "cases": difficulty * 100},
                {"name": "adversarial_stress", "cases": difficulty * 25},
            ],
            "certification_criteria": {
                "correctness_threshold": 1.0,
                "adversarial_survival": 0.95,
                "reproducibility_required": True,
            },
            "total_cases": difficulty * 175,
        }

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=challenge,
            confidence=0.95,
            reasoning=f"Generated evaluation challenge at difficulty {difficulty}",
            artifacts=[{"type": "challenge", "difficulty": difficulty}],
        )

    def _select_families(self, domain: str, rng: random.Random) -> list[str]:
        """Select adversarial families appropriate for a domain."""
        families_by_domain = {
            "code": ["overflow_trap", "off_by_one", "type_confusion", "recursion_bomb", "edge_case"],
            "math": ["precision_trap", "symbolic_ambiguity", "proof_gap", "numerical_instability"],
            "language": ["semantic_shift", "negation_trap", "ambiguity_exploit", "context_overflow"],
            "multimodal": ["modality_conflict", "ocr_adversarial", "spatial_confusion"],
            "safety": ["jailbreak_probe", "indirect_harm", "context_manipulation"],
            "general": ["boundary_stress", "hidden_complexity", "correctness_inversion", "format_break"],
        }
        available = families_by_domain.get(domain, families_by_domain["general"])
        count = min(len(available), rng.randint(3, len(available)))
        return rng.sample(available, count)
