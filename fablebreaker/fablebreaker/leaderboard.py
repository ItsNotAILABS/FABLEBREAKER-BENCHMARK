from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LeaderboardEntry:
    candidate_name: str
    certified: bool
    speedup: float
    total_cases: int
    total_correct: int
    total_failed: int
    timestamp_utc: str
    operator: str
    evidence_hash: str
    source_ref: str = ""


class Leaderboard:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: list[LeaderboardEntry] = []
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.entries = [
            LeaderboardEntry(
                candidate_name=e["candidate_name"],
                certified=e["certified"],
                speedup=e["speedup"],
                total_cases=e["total_cases"],
                total_correct=e["total_correct"],
                total_failed=e["total_failed"],
                timestamp_utc=e["timestamp_utc"],
                operator=e["operator"],
                evidence_hash=e["evidence_hash"],
                source_ref=e.get("source_ref", ""),
            )
            for e in data.get("entries", [])
        ]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",
            "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entries": [
                {
                    "candidate_name": e.candidate_name,
                    "certified": e.certified,
                    "speedup": e.speedup,
                    "total_cases": e.total_cases,
                    "total_correct": e.total_correct,
                    "total_failed": e.total_failed,
                    "timestamp_utc": e.timestamp_utc,
                    "operator": e.operator,
                    "evidence_hash": e.evidence_hash,
                    "source_ref": e.source_ref,
                }
                for e in self.entries
            ],
        }
        self.path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def submit(self, pack: dict[str, Any]) -> LeaderboardEntry:
        entry = LeaderboardEntry(
            candidate_name=pack["candidate_name"],
            certified=pack["overall_certified"],
            speedup=pack["overall_speedup"],
            total_cases=pack["total_cases"],
            total_correct=pack["total_correct"],
            total_failed=pack["total_failed"],
            timestamp_utc=pack["timestamp_utc"],
            operator=pack["operator"],
            evidence_hash=pack.get("content_hash", ""),
            source_ref=pack.get("candidate_source_ref", ""),
        )
        self.entries.append(entry)
        self._save()
        return entry

    def ranked(self, certified_only: bool = True) -> list[LeaderboardEntry]:
        filtered = self.entries
        if certified_only:
            filtered = [e for e in filtered if e.certified]
        return sorted(filtered, key=lambda e: e.speedup, reverse=True)

    def to_dict(self, certified_only: bool = True, limit: int = 50) -> dict[str, Any]:
        ranked = self.ranked(certified_only)[:limit]
        return {
            "leaderboard": [
                {
                    "rank": i + 1,
                    "candidate": e.candidate_name,
                    "certified": e.certified,
                    "speedup": e.speedup,
                    "cases": e.total_cases,
                    "correct": e.total_correct,
                    "timestamp": e.timestamp_utc,
                    "operator": e.operator,
                }
                for i, e in enumerate(ranked)
            ],
            "total_submissions": len(self.entries),
            "certified_submissions": sum(1 for e in self.entries if e.certified),
        }
