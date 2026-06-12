"""
Reasoning Skill — multi-step reasoning about AI evaluation.
"""

from __future__ import annotations

from typing import Any

from .base import Skill, SkillLevel, SkillResult


class ReasoningSkill(Skill):
    """
    Multi-step reasoning about AI evaluation, claims, and evidence.

    This skill gives Fablebreaker the ability to think through complex
    evaluation scenarios, chain evidence, and reach conclusions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="reasoning",
            description="Multi-step reasoning about AI evaluation, evidence chains, "
                        "and certification decisions. Thinks through complex scenarios.",
            level=SkillLevel.EXPERT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform reasoning.

        Context should contain:
        - reasoning_type: "evidence_chain", "certification_decision", "comparative", "diagnostic"
        - premises: list of factual premises
        - question: what to reason about
        """
        reasoning_type = context.get("reasoning_type", "evidence_chain")
        premises = context.get("premises", [])
        question = context.get("question", "")

        if reasoning_type == "evidence_chain":
            return self._reason_evidence_chain(premises, question)
        if reasoning_type == "certification_decision":
            return self._reason_certification(context)
        if reasoning_type == "comparative":
            return self._reason_comparative(context)
        if reasoning_type == "diagnostic":
            return self._reason_diagnostic(context)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown reasoning type: {reasoning_type}",
        )

    def _reason_evidence_chain(
        self, premises: list[Any], question: str
    ) -> SkillResult:
        """Chain evidence to reach a conclusion."""
        if not premises:
            return SkillResult(
                skill_name=self.name,
                success=False,
                reasoning="No premises provided for evidence chain reasoning",
            )

        chain = []
        confidence = 1.0

        for idx, premise in enumerate(premises):
            if isinstance(premise, dict):
                strength = premise.get("strength", 0.8)
                claim = premise.get("claim", str(premise))
            else:
                strength = 0.7
                claim = str(premise)

            confidence *= strength
            chain.append({
                "step": idx + 1,
                "premise": claim,
                "strength": strength,
                "cumulative_confidence": confidence,
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "question": question,
                "chain": chain,
                "conclusion_confidence": confidence,
                "chain_length": len(chain),
                "weakest_link": min(chain, key=lambda x: x["strength"]) if chain else None,
            },
            confidence=confidence,
            reasoning=f"Evidence chain of {len(chain)} steps with final confidence {confidence:.3f}",
        )

    def _reason_certification(self, context: dict[str, Any]) -> SkillResult:
        """Reason about whether to certify a claim."""
        correctness = context.get("correctness_passed", False)
        adversarial = context.get("adversarial_passed", True)
        contamination_clean = context.get("contamination_clean", True)
        reproducible = context.get("reproducible", False)

        reasons_for = []
        reasons_against = []

        if correctness:
            reasons_for.append("Correctness verification passed")
        else:
            reasons_against.append("Correctness verification FAILED — absolute disqualifier")

        if adversarial:
            reasons_for.append("Survived adversarial evaluation")
        else:
            reasons_against.append("Failed adversarial evaluation")

        if contamination_clean:
            reasons_for.append("No contamination detected")
        else:
            reasons_against.append("Contamination signals detected")

        if reproducible:
            reasons_for.append("Results are reproducible")
        else:
            reasons_against.append("Results not verified as reproducible")

        should_certify = correctness and adversarial and contamination_clean

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "decision": "CERTIFY" if should_certify else "REJECT",
                "reasons_for": reasons_for,
                "reasons_against": reasons_against,
                "decisive_factor": (
                    "All gates passed" if should_certify
                    else reasons_against[0] if reasons_against else "Unknown"
                ),
            },
            confidence=0.95 if should_certify else 0.9,
            reasoning=(
                f"Decision: {'CERTIFY' if should_certify else 'REJECT'}. "
                f"{len(reasons_for)} supporting, {len(reasons_against)} opposing factors."
            ),
        )

    def _reason_comparative(self, context: dict[str, Any]) -> SkillResult:
        """Compare multiple systems or benchmarks."""
        items = context.get("items", [])
        criteria = context.get("criteria", ["correctness", "robustness", "efficiency"])

        if len(items) < 2:
            return SkillResult(
                skill_name=self.name,
                success=False,
                reasoning="Need at least 2 items for comparative reasoning",
            )

        comparison = {
            "items_compared": len(items),
            "criteria": criteria,
            "rankings": {},
        }

        for criterion in criteria:
            crit = criterion
            ranked = sorted(
                items,
                key=lambda x, c=crit: x.get(c, 0) if isinstance(x, dict) else 0,
                reverse=True,
            )
            comparison["rankings"][criterion] = [
                item.get("name", f"item_{idx}") if isinstance(item, dict) else str(item)
                for idx, item in enumerate(ranked)
            ]

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=comparison,
            confidence=0.8,
            reasoning=f"Compared {len(items)} items across {len(criteria)} criteria",
        )

    def _reason_diagnostic(self, context: dict[str, Any]) -> SkillResult:
        """Diagnose why a system failed evaluation."""
        failures = context.get("failures", [])

        if not failures:
            return SkillResult(
                skill_name=self.name,
                success=True,
                output={"diagnosis": "No failures to diagnose"},
                confidence=1.0,
                reasoning="No failures present",
            )

        # Categorize failures
        categories: dict[str, list[Any]] = {}
        for failure in failures:
            category = failure.get("family", failure.get("type", "unknown"))
            if category not in categories:
                categories[category] = []
            categories[category].append(failure)

        primary_weakness = max(categories, key=lambda k: len(categories[k]))

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "total_failures": len(failures),
                "failure_categories": {k: len(v) for k, v in categories.items()},
                "primary_weakness": primary_weakness,
                "diagnosis": f"Primary failure pattern: {primary_weakness} "
                             f"({len(categories[primary_weakness])} occurrences)",
                "recommendation": f"Focus remediation on {primary_weakness} handling",
            },
            confidence=0.85,
            reasoning=f"Diagnosed {len(failures)} failures across {len(categories)} categories",
        )
