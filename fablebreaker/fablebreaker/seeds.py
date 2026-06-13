from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SeedEntry:
    seed: int
    commitment: str
    created_utc: str
    status: str = "active"
    retired_utc: str | None = None


def commit_seed(seed: int) -> str:
    return hashlib.sha256(str(seed).encode("utf-8")).hexdigest()


class SeedRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.path = registry_path
        self.entries: list[SeedEntry] = []
        if self.path.exists() and self.path.stat().st_size > 0:
            self._load()

    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.entries = [
            SeedEntry(
                seed=e["seed"],
                commitment=e["commitment"],
                created_utc=e["created_utc"],
                status=e.get("status", "active"),
                retired_utc=e.get("retired_utc"),
            )
            for e in data.get("seeds", [])
        ]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",
            "seeds": [
                {
                    "seed": e.seed,
                    "commitment": e.commitment,
                    "created_utc": e.created_utc,
                    "status": e.status,
                    "retired_utc": e.retired_utc,
                }
                for e in self.entries
            ],
        }
        self.path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def active_seeds(self) -> list[SeedEntry]:
        return [e for e in self.entries if e.status == "active"]

    def register_seed(self, seed: int) -> SeedEntry:
        commitment = commit_seed(seed)
        for existing in self.entries:
            if existing.seed == seed:
                return existing
        entry = SeedEntry(
            seed=seed,
            commitment=commitment,
            created_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.entries.append(entry)
        self._save()
        return entry

    def retire_seed(self, seed: int) -> None:
        for entry in self.entries:
            if entry.seed == seed and entry.status == "active":
                entry.status = "retired"
                entry.retired_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._save()

    def rotate(self, new_seed: int | None = None) -> SeedEntry:
        if new_seed is None:
            new_seed = int.from_bytes(os.urandom(4), "big")
        for entry in self.entries:
            if entry.status == "active":
                entry.status = "retired"
                entry.retired_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new_entry = SeedEntry(
            seed=new_seed,
            commitment=commit_seed(new_seed),
            created_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.entries.append(new_entry)
        self._save()
        return new_entry

    def commitments(self) -> list[dict[str, str]]:
        return [
            {"commitment": e.commitment, "status": e.status, "created_utc": e.created_utc}
            for e in self.entries
        ]
