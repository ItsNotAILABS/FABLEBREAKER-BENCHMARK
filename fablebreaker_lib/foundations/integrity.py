"""
Cryptographic integrity primitives used across the library.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Any


class ContentHasher:
    """SHA-256 content hasher for canonical serialization."""

    @staticmethod
    def hash_str(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_json(obj: Any) -> str:
        payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hmac_sign(content: str, secret: str) -> str:
        return hmac.HMAC(
            secret.encode("utf-8"),
            content.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def hmac_verify(content: str, signature: str, secret: str) -> bool:
        expected = ContentHasher.hmac_sign(content, secret)
        return hmac.compare_digest(expected, signature)


@dataclass
class HashChain:
    """An append-only hash chain for tamper-evident logging."""

    entries: list[dict[str, Any]] = field(default_factory=list)
    _chain: list[str] = field(default_factory=list)

    def append(self, data: dict[str, Any]) -> str:
        prev_hash = self._chain[-1] if self._chain else "0" * 64
        entry_payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
        combined = f"{prev_hash}:{entry_payload}"
        new_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        self.entries.append(data)
        self._chain.append(new_hash)
        return new_hash

    @property
    def head(self) -> str:
        return self._chain[-1] if self._chain else "0" * 64

    @property
    def length(self) -> int:
        return len(self._chain)

    def verify(self) -> bool:
        if len(self.entries) != len(self._chain):
            return False
        prev = "0" * 64
        for entry, stored_hash in zip(self.entries, self._chain):
            payload = json.dumps(entry, sort_keys=True, separators=(",", ":"))
            combined = f"{prev}:{payload}"
            expected = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            if expected != stored_hash:
                return False
            prev = stored_hash
        return True


@dataclass
class IntegrityEnvelope:
    """Wraps any payload with integrity metadata."""

    payload: dict[str, Any]
    content_hash: str = ""
    signature: str = ""
    signature_method: str = ""

    def seal(self, secret: str | None = None) -> IntegrityEnvelope:
        self.content_hash = ContentHasher.hash_json(self.payload)
        if secret:
            self.signature = ContentHasher.hmac_sign(self.content_hash, secret)
            self.signature_method = "hmac-sha256"
        return self

    def verify(self, secret: str | None = None) -> bool:
        expected_hash = ContentHasher.hash_json(self.payload)
        if expected_hash != self.content_hash:
            return False
        if secret and self.signature:
            return ContentHasher.hmac_verify(self.content_hash, self.signature, secret)
        return True

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "payload": self.payload,
            "content_hash": self.content_hash,
        }
        if self.signature:
            result["signature"] = self.signature
            result["signature_method"] = self.signature_method
        return result
