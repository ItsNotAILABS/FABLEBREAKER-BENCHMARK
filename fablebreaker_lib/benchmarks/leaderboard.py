"""
Leaderboard generation and ranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class LeaderboardEntry:
    """A single entry on the leaderboard."""
    rank: int
    candidate_name: str
    certified: bool
    speedup: float
    total_cases: int
    total_correct: int
    total_failed: int
    pass_rate: float
    timestamp_utc: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "candidate_name": self.candidate_name,
            "certified": self.certified,
            "speedup": self.speedup,
            "total_cases": self.total_cases,
            "total_correct": self.total_correct,
            "total_failed": self.total_failed,
            "pass_rate": self.pass_rate,
            "timestamp_utc": self.timestamp_utc,
            "metadata": self.metadata,
        }


class Leaderboard:
    """Manages ranked leaderboard of candidates."""

    def __init__(self) -> None:
        self._entries: list[LeaderboardEntry] = []

    def add_result(
        self,
        candidate_name: str,
        certified: bool,
        speedup: float,
        total_cases: int,
        total_correct: int,
        total_failed: int,
    ) -> LeaderboardEntry:
        entry = LeaderboardEntry(
            rank=0,
            candidate_name=candidate_name,
            certified=certified,
            speedup=speedup if certified else 0.0,
            total_cases=total_cases,
            total_correct=total_correct,
            total_failed=total_failed,
            pass_rate=total_correct / total_cases if total_cases > 0 else 0.0,
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self._entries.append(entry)
        self._rerank()
        return entry

    def _rerank(self) -> None:
        # Certified first (sorted by speedup desc), then uncertified (sorted by pass_rate desc)
        certified = [e for e in self._entries if e.certified]
        uncertified = [e for e in self._entries if not e.certified]
        certified.sort(key=lambda e: e.speedup, reverse=True)
        uncertified.sort(key=lambda e: e.pass_rate, reverse=True)
        combined = certified + uncertified
        for i, entry in enumerate(combined, 1):
            entry.rank = i
        self._entries = combined

    @property
    def entries(self) -> list[LeaderboardEntry]:
        return list(self._entries)

    @property
    def certified_count(self) -> int:
        return sum(1 for e in self._entries if e.certified)

    @property
    def total_candidates(self) -> int:
        return len(self._entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_candidates": self.total_candidates,
            "certified_count": self.certified_count,
            "certification_rate": self.certified_count / self.total_candidates if self.total_candidates > 0 else 0.0,
            "entries": [e.to_dict() for e in self._entries],
        }
