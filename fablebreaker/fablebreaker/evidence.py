from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVIDENCE_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _content_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sign_evidence(pack: dict[str, Any], secret: str) -> str:
    payload = json.dumps(pack, sort_keys=True, separators=(",", ":"))
    return hmac.HMAC(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def verify_signature(pack: dict[str, Any], signature: str, secret: str) -> bool:
    expected = sign_evidence(pack, secret)
    return hmac.compare_digest(expected, signature)


def generate_evidence_pack(
    candidate_name: str,
    candidate_source_ref: str,
    public_score: dict[str, Any],
    hidden_score: dict[str, Any],
    public_seed: int,
    hidden_seed: int,
    operator: str = "self-audit",
    signing_secret: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    certified = public_score.get("certified", False) and hidden_score.get("certified", False)
    speedup = min(
        public_score.get("speedup_vs_reference", 0.0),
        hidden_score.get("speedup_vs_reference", 0.0),
    ) if certified else 0.0

    pack: dict[str, Any] = {
        "evidence_version": EVIDENCE_VERSION,
        "suite_id": "fablebreaker",
        "suite_version": "0.1.0",
        "candidate_name": candidate_name,
        "candidate_source_ref": candidate_source_ref,
        "timestamp_utc": _utc_now(),
        "operator": operator,
        "public_seed": public_seed,
        "hidden_seed_commitment": hashlib.sha256(str(hidden_seed).encode()).hexdigest(),
        "public_score": {
            "cases": public_score["cases"],
            "correct": public_score["correct"],
            "failed": public_score["failed"],
            "certified": public_score["certified"],
            "speedup_vs_reference": public_score.get("speedup_vs_reference", 0.0),
            "candidate_median_ms": public_score.get("candidate_median_ms", 0),
            "candidate_p95_ms": public_score.get("candidate_p95_ms", 0),
            "family_diagnostics": public_score.get("family_diagnostics", {}),
        },
        "hidden_score": {
            "cases": hidden_score["cases"],
            "correct": hidden_score["correct"],
            "failed": hidden_score["failed"],
            "certified": hidden_score["certified"],
            "speedup_vs_reference": hidden_score.get("speedup_vs_reference", 0.0),
            "candidate_median_ms": hidden_score.get("candidate_median_ms", 0),
            "candidate_p95_ms": hidden_score.get("candidate_p95_ms", 0),
            "family_diagnostics": hidden_score.get("family_diagnostics", {}),
        },
        "overall_certified": certified,
        "overall_speedup": speedup,
        "total_cases": public_score["cases"] + hidden_score["cases"],
        "total_correct": public_score["correct"] + hidden_score["correct"],
        "total_failed": public_score["failed"] + hidden_score["failed"],
        "notes": notes,
    }

    pack["content_hash"] = _content_hash(
        json.dumps(pack, sort_keys=True, separators=(",", ":"))
    )

    if signing_secret:
        pack["signature"] = sign_evidence(pack, signing_secret)
        pack["signature_method"] = "hmac-sha256"

    return pack


def save_evidence_pack(pack: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output_path
