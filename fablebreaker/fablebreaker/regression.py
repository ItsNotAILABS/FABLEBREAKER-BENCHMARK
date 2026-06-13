from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RegressionRecord:
    candidate_name: str
    timestamp_utc: str
    certified: bool
    speedup: float
    total_cases: int
    total_failed: int
    public_seed: int
    hidden_seed_commitment: str


class RegressionMonitor:
    def __init__(self, history_path: Path) -> None:
        self.path = history_path
        self.records: list[RegressionRecord] = []
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.records = [
            RegressionRecord(
                candidate_name=r["candidate_name"],
                timestamp_utc=r["timestamp_utc"],
                certified=r["certified"],
                speedup=r["speedup"],
                total_cases=r["total_cases"],
                total_failed=r["total_failed"],
                public_seed=r["public_seed"],
                hidden_seed_commitment=r["hidden_seed_commitment"],
            )
            for r in data.get("records", [])
        ]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",
            "records": [
                {
                    "candidate_name": r.candidate_name,
                    "timestamp_utc": r.timestamp_utc,
                    "certified": r.certified,
                    "speedup": r.speedup,
                    "total_cases": r.total_cases,
                    "total_failed": r.total_failed,
                    "public_seed": r.public_seed,
                    "hidden_seed_commitment": r.hidden_seed_commitment,
                }
                for r in self.records
            ],
        }
        self.path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def record_from_pack(self, pack: dict[str, Any]) -> RegressionRecord:
        record = RegressionRecord(
            candidate_name=pack["candidate_name"],
            timestamp_utc=pack["timestamp_utc"],
            certified=pack["overall_certified"],
            speedup=pack["overall_speedup"],
            total_cases=pack["total_cases"],
            total_failed=pack["total_failed"],
            public_seed=pack["public_seed"],
            hidden_seed_commitment=pack["hidden_seed_commitment"],
        )
        self.records.append(record)
        self._save()
        return record

    def history(self, candidate_name: str) -> list[RegressionRecord]:
        return [r for r in self.records if r.candidate_name == candidate_name]

    def detect_regression(self, candidate_name: str, current_pack: dict[str, Any]) -> dict[str, Any]:
        history = self.history(candidate_name)
        if not history:
            return {"regression": False, "reason": "no_history"}

        last = history[-1]
        current_certified = current_pack["overall_certified"]
        current_speedup = current_pack["overall_speedup"]

        regressions: list[str] = []

        if last.certified and not current_certified:
            regressions.append("certification_lost")

        if last.certified and current_certified and current_speedup < last.speedup * 0.9:
            regressions.append(f"speedup_dropped: {last.speedup:.3f}x -> {current_speedup:.3f}x")

        if current_pack["total_failed"] > last.total_failed:
            regressions.append(f"failures_increased: {last.total_failed} -> {current_pack['total_failed']}")

        return {
            "regression": bool(regressions),
            "issues": regressions,
            "previous_speedup": last.speedup,
            "current_speedup": current_speedup,
            "previous_certified": last.certified,
            "current_certified": current_certified,
        }

    def summary(self) -> dict[str, Any]:
        candidates: dict[str, list[RegressionRecord]] = {}
        for r in self.records:
            candidates.setdefault(r.candidate_name, []).append(r)
        return {
            "total_records": len(self.records),
            "candidates_tracked": len(candidates),
            "candidates": {
                name: {
                    "runs": len(records),
                    "latest_certified": records[-1].certified,
                    "latest_speedup": records[-1].speedup,
                    "best_speedup": max(r.speedup for r in records if r.certified) if any(r.certified for r in records) else 0.0,
                }
                for name, records in candidates.items()
            },
        }
