"""Governance-Aware Certification Protocol SDK.

Implements the methodology from:
    "Governance-Aware Certification: Embedding Trust Hierarchies
     in Benchmark Evidence Chains"
    Journal of Certification Systems · Volume 1 · 2026

This module provides a programmatic interface for constructing, validating,
and verifying governance-aware evidence chains as described in the paper.

Foundation: https://doi.org/10.5281/zenodo.20589250
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GovernanceRole(Enum):
    """Roles in the governance authority model (Section 3)."""

    SEED_GENERATOR = "seed_generator"
    DATASET_PRODUCER = "dataset_producer"
    SCORING_OPERATOR = "scoring_operator"
    RESULT_PUBLISHER = "result_publisher"
    GOVERNANCE_AUTHORITY = "governance_authority"


@dataclass(frozen=True)
class GovernanceVersion:
    """A specific version of governance rules.

    All certification evidence is pinned to a governance version,
    preventing retroactive rule changes (Threat #2).
    """

    version: str
    effective_date: str
    rules_hash: str
    authority: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for evidence chain embedding."""
        return {
            "version": self.version,
            "effective_date": self.effective_date,
            "rules_hash": self.rules_hash,
            "authority": self.authority,
        }


@dataclass(frozen=True)
class RoleAttestation:
    """Attestation that an operator holds a specific role.

    Prevents self-certification (Threat #1) and authority escalation (Threat #3).
    """

    operator: str
    role: GovernanceRole
    granted_by: str
    granted_at: str
    expires_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for evidence chain embedding."""
        return {
            "operator": self.operator,
            "role": self.role.value,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
        }


@dataclass
class GovernanceAttestation:
    """Complete governance attestation for an evidence pack.

    Binds evidence to governance version, operator role, and temporal ordering.
    """

    governance_version: GovernanceVersion
    operator_role: RoleAttestation
    timestamp_utc: str
    attestation_hash: str = ""

    def __post_init__(self) -> None:
        if not self.attestation_hash:
            self.attestation_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute cryptographic binding for the attestation."""
        payload = json.dumps({
            "governance_version": self.governance_version.to_dict(),
            "operator_role": self.operator_role.to_dict(),
            "timestamp_utc": self.timestamp_utc,
        }, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for evidence pack inclusion."""
        return {
            "governance_version": self.governance_version.to_dict(),
            "operator_role": self.operator_role.to_dict(),
            "timestamp_utc": self.timestamp_utc,
            "attestation_hash": self.attestation_hash,
        }


@dataclass
class GovernanceAwareEvidencePack:
    """Evidence pack with embedded governance attestation.

    Extends the base evidence pack template with governance bindings
    as specified in Section 4 of the paper.
    """

    suite_id: str
    suite_version: str
    candidate_name: str
    candidate_source_ref: str
    certified: bool
    speedup_vs_reference: float | None
    governance_attestation: GovernanceAttestation
    scoring_hash: str = ""
    timestamp_utc: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp_utc:
            self.timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> dict[str, Any]:
        """Serialize to complete evidence pack dictionary."""
        return {
            "suite_id": self.suite_id,
            "suite_version": self.suite_version,
            "candidate_name": self.candidate_name,
            "candidate_source_ref": self.candidate_source_ref,
            "certified": self.certified,
            "speedup_vs_reference": self.speedup_vs_reference,
            "governance_attestation": self.governance_attestation.to_dict(),
            "scoring_hash": self.scoring_hash,
            "timestamp_utc": self.timestamp_utc,
        }

    def verify_integrity(self) -> bool:
        """Verify that the attestation hash matches recomputation."""
        return (
            self.governance_attestation.attestation_hash
            == self.governance_attestation._compute_hash()
        )


class GovernanceCertificationProtocol:
    """SDK for the Governance-Aware Certification protocol.

    Provides methods for constructing governance-aware evidence chains,
    validating role separation, and verifying attestation integrity.

    Usage:
        protocol = GovernanceCertificationProtocol()

        # Define governance version
        gov = protocol.create_governance_version(
            version="1.0.0",
            effective_date="2026-01-01",
            rules_hash="abc123...",
            authority="ItsNotAI LABS"
        )

        # Grant operator role
        role = protocol.grant_role(
            operator="operator@example.com",
            role=GovernanceRole.SCORING_OPERATOR,
            granted_by="admin@itsnotai.com"
        )

        # Create governance-aware evidence pack
        pack = protocol.create_evidence_pack(
            suite_id="fablebreaker",
            candidate_name="fast_evaluator",
            candidate_source_ref="abc123",
            certified=True,
            speedup=2.3,
            governance_version=gov,
            operator_role=role,
        )

        # Verify integrity
        assert pack.verify_integrity()
    """

    PAPER_TITLE = "Governance-Aware Certification: Embedding Trust Hierarchies in Benchmark Evidence Chains"
    JOURNAL = "Journal of Certification Systems"
    DOI_FOUNDATION = "10.5281/zenodo.20589250"

    # Seven certification integrity attacks (Section 2)
    THREAT_MODEL = [
        "self_certification",
        "retroactive_rule_change",
        "authority_escalation",
        "seed_leakage",
        "evidence_substitution",
        "temporal_reordering",
        "governance_fork",
    ]

    def create_governance_version(
        self,
        version: str,
        effective_date: str,
        rules_hash: str,
        authority: str,
    ) -> GovernanceVersion:
        """Create a governance version specification."""
        return GovernanceVersion(
            version=version,
            effective_date=effective_date,
            rules_hash=rules_hash,
            authority=authority,
        )

    def grant_role(
        self,
        operator: str,
        role: GovernanceRole,
        granted_by: str,
        granted_at: str | None = None,
        expires_at: str | None = None,
    ) -> RoleAttestation:
        """Grant a governance role to an operator.

        Args:
            operator: Identity of the operator receiving the role.
            role: The governance role being granted.
            granted_by: Identity of the authority granting the role.
            granted_at: ISO timestamp (defaults to now).
            expires_at: Optional expiration timestamp.
        """
        if not granted_at:
            granted_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return RoleAttestation(
            operator=operator,
            role=role,
            granted_by=granted_by,
            granted_at=granted_at,
            expires_at=expires_at,
        )

    def create_evidence_pack(
        self,
        suite_id: str,
        candidate_name: str,
        candidate_source_ref: str,
        certified: bool,
        speedup: float | None,
        governance_version: GovernanceVersion,
        operator_role: RoleAttestation,
        suite_version: str = "0.1.0",
        scoring_hash: str = "",
    ) -> GovernanceAwareEvidencePack:
        """Create a governance-aware evidence pack.

        Binds certification result to governance context for
        non-repudiation and temporal ordering.
        """
        attestation = GovernanceAttestation(
            governance_version=governance_version,
            operator_role=operator_role,
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        return GovernanceAwareEvidencePack(
            suite_id=suite_id,
            suite_version=suite_version,
            candidate_name=candidate_name,
            candidate_source_ref=candidate_source_ref,
            certified=certified,
            speedup_vs_reference=speedup,
            governance_attestation=attestation,
            scoring_hash=scoring_hash,
        )

    def validate_role_separation(
        self,
        candidate_author: str,
        operator_role: RoleAttestation,
    ) -> bool:
        """Validate that the scoring operator is not the candidate author.

        Prevents self-certification (Threat #1).
        """
        return operator_role.operator != candidate_author

    def validate_temporal_ordering(
        self,
        governance_version: GovernanceVersion,
        certification_timestamp: str,
    ) -> bool:
        """Validate that certification occurred after governance rules were effective.

        Prevents retroactive rule changes (Threat #2) and temporal reordering (Threat #6).
        """
        return certification_timestamp >= governance_version.effective_date

    def verify_attestation(self, pack: GovernanceAwareEvidencePack) -> bool:
        """Verify the cryptographic integrity of a governance attestation."""
        return pack.verify_integrity()
