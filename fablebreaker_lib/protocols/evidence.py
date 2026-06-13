"""
Evidence generation and verification protocols.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class EvidenceGenerator:
    """Generates cryptographically-bound evidence packs."""

    def __init__(self, signing_secret: str | None = None) -> None:
        self._secret = signing_secret

    def generate(
        self,
        candidate_name: str,
        candidate_source_ref: str,
        public_score: dict[str, Any],
        hidden_score: dict[str, Any],
        public_seed: int,
        hidden_seed: int,
        operator: str = "self-audit",
        notes: str = "",
    ) -> dict[str, Any]:
        """Generate a complete evidence pack with integrity metadata."""
        certified = public_score.get("certified", False) and hidden_score.get("certified", False)
        speedup = min(
            public_score.get("speedup_vs_reference", 0.0),
            hidden_score.get("speedup_vs_reference", 0.0),
        ) if certified else 0.0

        pack: dict[str, Any] = {
            "evidence_version": "1.0.0",
            "suite_id": "fablebreaker",
            "candidate_name": candidate_name,
            "candidate_source_ref": candidate_source_ref,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "operator": operator,
            "public_seed": public_seed,
            "hidden_seed_commitment": hashlib.sha256(str(hidden_seed).encode()).hexdigest(),
            "public_score": public_score,
            "hidden_score": hidden_score,
            "overall_certified": certified,
            "overall_speedup": speedup,
            "total_cases": public_score.get("cases", 0) + hidden_score.get("cases", 0),
            "total_correct": public_score.get("correct", 0) + hidden_score.get("correct", 0),
            "total_failed": public_score.get("failed", 0) + hidden_score.get("failed", 0),
            "notes": notes,
        }

        # Content hash
        pack["content_hash"] = self._hash_json(pack)

        # HMAC signature
        if self._secret:
            payload = json.dumps(pack, sort_keys=True, separators=(",", ":"))
            pack["signature"] = hmac.HMAC(
                self._secret.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            pack["signature_method"] = "hmac-sha256"

        return pack

    @staticmethod
    def _hash_json(obj: Any) -> str:
        payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EvidenceVerifier:
    """Verifies integrity and authenticity of evidence packs."""

    def __init__(self, signing_secret: str | None = None) -> None:
        self._secret = signing_secret

    def verify_content_hash(self, pack: dict[str, Any]) -> bool:
        """Verify the content hash of an evidence pack."""
        stored_hash = pack.get("content_hash", "")
        pack_copy = {k: v for k, v in pack.items() if k not in ("content_hash", "signature", "signature_method")}
        expected = hashlib.sha256(
            json.dumps(pack_copy, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return hmac.compare_digest(stored_hash, expected)

    def verify_signature(self, pack: dict[str, Any]) -> bool:
        """Verify the HMAC signature of an evidence pack."""
        if not self._secret:
            return True  # No secret = skip signature check
        signature = pack.get("signature", "")
        if not signature:
            return False
        pack_without_sig = {k: v for k, v in pack.items() if k not in ("signature", "signature_method")}
        payload = json.dumps(pack_without_sig, sort_keys=True, separators=(",", ":"))
        expected = hmac.HMAC(
            self._secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def verify(self, pack: dict[str, Any]) -> tuple[bool, list[str]]:
        """Full verification of an evidence pack. Returns (valid, issues)."""
        issues: list[str] = []
        if not self.verify_content_hash(pack):
            issues.append("Content hash mismatch - pack may be tampered")
        if self._secret and not self.verify_signature(pack):
            issues.append("Signature verification failed")
        if not pack.get("overall_certified", False):
            issues.append("Pack indicates certification failure")
        return len(issues) == 0, issues


@dataclass
class EvidenceChain:
    """Chain of evidence packs for tracking certification history."""
    entries: list[dict[str, Any]] = field(default_factory=list)

    def append(self, pack: dict[str, Any]) -> None:
        self.entries.append(pack)

    @property
    def latest(self) -> dict[str, Any] | None:
        return self.entries[-1] if self.entries else None

    @property
    def certified_count(self) -> int:
        return sum(1 for e in self.entries if e.get("overall_certified", False))

    def history(self, candidate_name: str) -> list[dict[str, Any]]:
        return [e for e in self.entries if e.get("candidate_name") == candidate_name]
