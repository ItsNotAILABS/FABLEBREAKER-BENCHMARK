"""
Certification Engine — issues verdicts on AI system claims.

The final authority that determines whether a performance claim
is certified or rejected. Combines signals from all other engines.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .base import Engine, EngineResult, EngineStatus


class CertificationEngine(Engine):
    """
    Issues certification verdicts on AI performance claims.

    This engine is the judge. It takes evidence from correctness,
    adversarial, and contamination engines, and issues a final
    certification verdict with cryptographic evidence.
    """

    def __init__(self) -> None:
        super().__init__(
            name="certification",
            description="Final certification authority. Issues verdicts "
                        "on AI performance claims with cryptographic evidence.",
        )

    def execute(self, context: dict[str, Any]) -> EngineResult:
        """
        Issue a certification verdict.

        Context should contain:
        - claim: dict describing the performance claim
        - correctness_result: result from CorrectnessEngine
        - adversarial_result: result from AdversarialEngine (optional)
        - contamination_result: result from ContaminationEngine (optional)
        - candidate_name: name of the system being certified
        - operator: who requested certification
        """
        claim = context.get("claim", {})
        candidate = context.get("candidate_name", "unknown")
        operator = context.get("operator", "system")

        correctness = context.get("correctness_result", {})
        adversarial = context.get("adversarial_result", {})
        contamination = context.get("contamination_result", {})

        # Correctness is the absolute gate
        correctness_passed = correctness.get("verdict") == "certified"
        correctness_confidence = correctness.get("confidence", 0.0)

        # Adversarial resilience (if tested)
        adversarial_passed = True
        if adversarial:
            adversarial_passed = adversarial.get("verdict") == "resilient"

        # Contamination check (if tested)
        contamination_clean = True
        if contamination:
            contamination_clean = contamination.get("verdict") == "clean"

        # Final verdict logic
        certified = correctness_passed and adversarial_passed and contamination_clean

        # Build evidence pack
        evidence = {
            "candidate": candidate,
            "operator": operator,
            "claim": claim,
            "correctness_gate": {
                "passed": correctness_passed,
                "confidence": correctness_confidence,
            },
            "adversarial_gate": {
                "passed": adversarial_passed,
                "tested": bool(adversarial),
            },
            "contamination_gate": {
                "passed": contamination_clean,
                "tested": bool(contamination),
            },
            "certified": certified,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Cryptographic seal
        evidence_json = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        evidence_hash = hashlib.sha256(evidence_json.encode("utf-8")).hexdigest()
        evidence["evidence_hash"] = evidence_hash

        verdict = "CERTIFIED" if certified else "REJECTED"
        reasons = []
        if not correctness_passed:
            reasons.append("Correctness verification failed")
        if not adversarial_passed:
            reasons.append("Adversarial resilience check failed")
        if not contamination_clean:
            reasons.append("Contamination detected")

        return EngineResult(
            engine_name=self.name,
            status=EngineStatus.COMPLETE,
            verdict=verdict,
            confidence=correctness_confidence if certified else 0.0,
            findings=[{"reason": r} for r in reasons] if reasons else [],
            metadata={
                "evidence_pack": evidence,
                "evidence_hash": evidence_hash,
                "rejection_reasons": reasons,
                "gates_passed": {
                    "correctness": correctness_passed,
                    "adversarial": adversarial_passed,
                    "contamination": contamination_clean,
                },
            },
        )
