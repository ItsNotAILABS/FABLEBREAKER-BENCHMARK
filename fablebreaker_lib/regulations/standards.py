"""
Pre-defined regulatory standards for AI evaluation systems.
"""

from __future__ import annotations

from .compliance import ComplianceStandard, ComplianceCheck


# --- EU AI Act ---

EU_AI_ACT = ComplianceStandard(
    id="EU-AI-ACT",
    name="EU Artificial Intelligence Act",
    version="2024",
    description="European Union regulation on artificial intelligence systems.",
    jurisdiction="EU",
    effective_date="2024-08-01",
)

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-001",
    standard_id="EU-AI-ACT",
    requirement="Risk Classification",
    description="AI system must be classified by risk level (unacceptable, high, limited, minimal).",
    article_ref="Article 6",
    check_fn=lambda ctx: "risk_level" in ctx,
    remediation="Classify your AI system according to EU AI Act risk categories.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-002",
    standard_id="EU-AI-ACT",
    requirement="Transparency Obligations",
    description="Users must be informed they are interacting with an AI system.",
    article_ref="Article 52",
    check_fn=lambda ctx: ctx.get("transparency_disclosed", False),
    remediation="Implement clear disclosure that users are interacting with AI.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-003",
    standard_id="EU-AI-ACT",
    requirement="Human Oversight",
    description="High-risk AI systems must allow human oversight and intervention.",
    article_ref="Article 14",
    check_fn=lambda ctx: ctx.get("human_oversight_enabled", False) or ctx.get("risk_level") != "high",
    remediation="Implement human-in-the-loop mechanisms for high-risk applications.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-004",
    standard_id="EU-AI-ACT",
    requirement="Technical Documentation",
    description="System must maintain technical documentation of capabilities and limitations.",
    article_ref="Article 11",
    check_fn=lambda ctx: ctx.get("technical_documentation", False),
    remediation="Create and maintain technical documentation per Annex IV requirements.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-005",
    standard_id="EU-AI-ACT",
    requirement="Data Governance",
    description="Training and evaluation data must meet quality criteria.",
    article_ref="Article 10",
    check_fn=lambda ctx: ctx.get("data_governance_implemented", False),
    remediation="Implement data governance practices for training and evaluation data.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-006",
    standard_id="EU-AI-ACT",
    requirement="Record Keeping",
    description="System must maintain logs of operation for traceability.",
    article_ref="Article 12",
    check_fn=lambda ctx: ctx.get("logging_enabled", False),
    remediation="Implement automatic logging of system operation.",
))

EU_AI_ACT.add_check(ComplianceCheck(
    id="EU-AI-007",
    standard_id="EU-AI-ACT",
    requirement="Accuracy and Robustness",
    description="System must achieve appropriate levels of accuracy and robustness.",
    article_ref="Article 15",
    check_fn=lambda ctx: ctx.get("accuracy_validated", False),
    remediation="Validate system accuracy and robustness through rigorous testing.",
))


# --- NIST AI Risk Management Framework ---

NIST_AI_RMF = ComplianceStandard(
    id="NIST-AI-RMF",
    name="NIST AI Risk Management Framework",
    version="1.0",
    description="NIST framework for managing risks in AI systems.",
    jurisdiction="US",
    effective_date="2023-01-26",
)

NIST_AI_RMF.add_check(ComplianceCheck(
    id="NIST-001",
    standard_id="NIST-AI-RMF",
    requirement="GOVERN: Policies and Processes",
    description="Organization has established AI governance policies.",
    check_fn=lambda ctx: ctx.get("governance_policies", False),
    remediation="Establish organizational AI governance policies and accountability structures.",
))

NIST_AI_RMF.add_check(ComplianceCheck(
    id="NIST-002",
    standard_id="NIST-AI-RMF",
    requirement="MAP: Context and Risk Identification",
    description="AI system context and potential risks are mapped and documented.",
    check_fn=lambda ctx: ctx.get("risk_mapped", False),
    remediation="Document AI system context, intended use, and potential risks.",
))

NIST_AI_RMF.add_check(ComplianceCheck(
    id="NIST-003",
    standard_id="NIST-AI-RMF",
    requirement="MEASURE: Risk Assessment",
    description="Risks are measured through appropriate metrics and testing.",
    check_fn=lambda ctx: ctx.get("risk_measured", False),
    remediation="Implement quantitative risk measurement through testing and monitoring.",
))

NIST_AI_RMF.add_check(ComplianceCheck(
    id="NIST-004",
    standard_id="NIST-AI-RMF",
    requirement="MANAGE: Risk Treatment",
    description="Identified risks are actively managed and mitigated.",
    check_fn=lambda ctx: ctx.get("risk_managed", False),
    remediation="Implement risk treatment plans for identified AI risks.",
))

NIST_AI_RMF.add_check(ComplianceCheck(
    id="NIST-005",
    standard_id="NIST-AI-RMF",
    requirement="Trustworthiness Characteristics",
    description="System addresses validity, reliability, safety, fairness, transparency, accountability, and privacy.",
    check_fn=lambda ctx: ctx.get("trustworthiness_assessed", False),
    remediation="Assess system against all NIST trustworthiness characteristics.",
))


# --- Responsible AI Principles ---

RESPONSIBLE_AI = ComplianceStandard(
    id="RESPONSIBLE-AI",
    name="Responsible AI Principles",
    version="1.0",
    description="Cross-industry responsible AI development principles.",
    jurisdiction="international",
)

RESPONSIBLE_AI.add_check(ComplianceCheck(
    id="RAI-001",
    standard_id="RESPONSIBLE-AI",
    requirement="Fairness",
    description="System does not produce biased or discriminatory outputs.",
    check_fn=lambda ctx: ctx.get("fairness_assessed", False),
    remediation="Conduct fairness assessment and bias testing.",
))

RESPONSIBLE_AI.add_check(ComplianceCheck(
    id="RAI-002",
    standard_id="RESPONSIBLE-AI",
    requirement="Explainability",
    description="System decisions can be explained to stakeholders.",
    check_fn=lambda ctx: ctx.get("explainability_implemented", False),
    remediation="Implement explanation mechanisms for system outputs.",
))

RESPONSIBLE_AI.add_check(ComplianceCheck(
    id="RAI-003",
    standard_id="RESPONSIBLE-AI",
    requirement="Privacy",
    description="System protects personal and sensitive data.",
    check_fn=lambda ctx: ctx.get("privacy_protected", False),
    remediation="Implement data protection and privacy-preserving techniques.",
))

RESPONSIBLE_AI.add_check(ComplianceCheck(
    id="RAI-004",
    standard_id="RESPONSIBLE-AI",
    requirement="Safety",
    description="System operates safely and does not cause harm.",
    check_fn=lambda ctx: ctx.get("safety_validated", False),
    remediation="Validate system safety through adversarial testing.",
))

RESPONSIBLE_AI.add_check(ComplianceCheck(
    id="RAI-005",
    standard_id="RESPONSIBLE-AI",
    requirement="Accountability",
    description="Clear accountability for system behavior and outcomes.",
    check_fn=lambda ctx: ctx.get("accountability_defined", False),
    remediation="Define clear accountability structures and escalation paths.",
))


# --- Transparency Standard ---

TRANSPARENCY_STANDARD = ComplianceStandard(
    id="TRANSPARENCY",
    name="AI Transparency Standard",
    version="1.0",
    description="Requirements for AI system transparency and disclosure.",
    jurisdiction="international",
)

TRANSPARENCY_STANDARD.add_check(ComplianceCheck(
    id="TRANS-001",
    standard_id="TRANSPARENCY",
    requirement="Method Disclosure",
    description="Evaluation methodology is publicly documented.",
    check_fn=lambda ctx: ctx.get("method_documented", False),
    remediation="Publish documentation of evaluation methodology.",
))

TRANSPARENCY_STANDARD.add_check(ComplianceCheck(
    id="TRANS-002",
    standard_id="TRANSPARENCY",
    requirement="Source Availability",
    description="Core evaluation code is open source and auditable.",
    check_fn=lambda ctx: ctx.get("source_available", False),
    remediation="Make evaluation source code publicly available.",
))

TRANSPARENCY_STANDARD.add_check(ComplianceCheck(
    id="TRANS-003",
    standard_id="TRANSPARENCY",
    requirement="Result Reproducibility",
    description="Results can be independently reproduced by third parties.",
    check_fn=lambda ctx: ctx.get("reproducible", False),
    remediation="Ensure deterministic evaluation with published seeds.",
))


# --- Safety Standard ---

SAFETY_STANDARD = ComplianceStandard(
    id="SAFETY",
    name="AI Safety Standard",
    version="1.0",
    description="Requirements for safe AI system operation.",
    jurisdiction="international",
)

SAFETY_STANDARD.add_check(ComplianceCheck(
    id="SAFE-001",
    standard_id="SAFETY",
    requirement="Bounded Computation",
    description="System has hard limits on computation to prevent runaway processes.",
    check_fn=lambda ctx: ctx.get("computation_bounded", False),
    remediation="Implement step budgets and timeout mechanisms.",
))

SAFETY_STANDARD.add_check(ComplianceCheck(
    id="SAFE-002",
    standard_id="SAFETY",
    requirement="Graceful Degradation",
    description="System handles adversarial inputs without crashing or hanging.",
    check_fn=lambda ctx: ctx.get("graceful_degradation", False),
    remediation="Implement error handling for all adversarial input families.",
))

SAFETY_STANDARD.add_check(ComplianceCheck(
    id="SAFE-003",
    standard_id="SAFETY",
    requirement="No Unauthorized Side Effects",
    description="Evaluation does not modify external state or leak data.",
    check_fn=lambda ctx: ctx.get("sandboxed", False),
    remediation="Run evaluations in sandboxed environments with no external access.",
))

SAFETY_STANDARD.add_check(ComplianceCheck(
    id="SAFE-004",
    standard_id="SAFETY",
    requirement="Failure Containment",
    description="Single candidate failure does not affect other evaluations.",
    check_fn=lambda ctx: ctx.get("failure_contained", False),
    remediation="Isolate candidate evaluations to prevent cross-contamination.",
))


ALL_STANDARDS = (
    EU_AI_ACT,
    NIST_AI_RMF,
    RESPONSIBLE_AI,
    TRANSPARENCY_STANDARD,
    SAFETY_STANDARD,
)
