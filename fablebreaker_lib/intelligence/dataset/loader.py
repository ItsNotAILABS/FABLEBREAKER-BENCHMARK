"""
Dataset loader and knowledge base interface for Fablebreaker Intelligence.

Provides structured access to the AI benchmarks mega-dataset so that
Fablebreaker's engines and skills can reason over benchmark knowledge.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BenchmarkEntry:
    """A single benchmark entry in the knowledge base."""
    name: str
    domain: str
    category: str
    description: str
    metrics: list[str]
    year: int
    organization: str
    task_types: list[str]
    scale: str
    url: str = ""
    limitations: list[str] = field(default_factory=list)
    gaming_vectors: list[str] = field(default_factory=list)
    correctness_requirements: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenchmarkEntry":
        return cls(
            name=data["name"],
            domain=data["domain"],
            category=data["category"],
            description=data["description"],
            metrics=data["metrics"],
            year=data["year"],
            organization=data["organization"],
            task_types=data["task_types"],
            scale=data["scale"],
            url=data.get("url", ""),
            limitations=data.get("limitations", []),
            gaming_vectors=data.get("gaming_vectors", []),
            correctness_requirements=data.get("correctness_requirements", []),
            tags=data.get("tags", []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "category": self.category,
            "description": self.description,
            "metrics": self.metrics,
            "year": self.year,
            "organization": self.organization,
            "task_types": self.task_types,
            "scale": self.scale,
            "url": self.url,
            "limitations": self.limitations,
            "gaming_vectors": self.gaming_vectors,
            "correctness_requirements": self.correctness_requirements,
            "tags": self.tags,
        }


class BenchmarkKnowledgeBase:
    """
    The central knowledge base for Fablebreaker Intelligence.

    Benchmarks are data. Fablebreaker is the intelligence that ingests,
    evaluates, and transcends them. This class provides the interface
    for engines and skills to query benchmark knowledge.
    """

    def __init__(self) -> None:
        self._entries: list[BenchmarkEntry] = []
        self._by_name: dict[str, BenchmarkEntry] = {}
        self._by_domain: dict[str, list[BenchmarkEntry]] = {}
        self._by_category: dict[str, list[BenchmarkEntry]] = {}
        self._by_tag: dict[str, list[BenchmarkEntry]] = {}

    def load_catalog(self, catalog: list[dict[str, Any]]) -> None:
        """Load the full benchmark catalog into the knowledge base."""
        for item in catalog:
            entry = BenchmarkEntry.from_dict(item)
            self._entries.append(entry)
            self._by_name[entry.name] = entry

            if entry.domain not in self._by_domain:
                self._by_domain[entry.domain] = []
            self._by_domain[entry.domain].append(entry)

            if entry.category not in self._by_category:
                self._by_category[entry.category] = []
            self._by_category[entry.category].append(entry)

            for tag in entry.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = []
                self._by_tag[tag].append(entry)

    def load_from_file(self, path: Path) -> None:
        """Load benchmark data from a JSONL file."""
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    self.load_catalog([json.loads(line)])

    @property
    def total_benchmarks(self) -> int:
        return len(self._entries)

    @property
    def domains(self) -> list[str]:
        return list(self._by_domain.keys())

    @property
    def categories(self) -> list[str]:
        return list(self._by_category.keys())

    @property
    def tags(self) -> list[str]:
        return list(self._by_tag.keys())

    def get(self, name: str) -> BenchmarkEntry | None:
        """Get a specific benchmark by name."""
        return self._by_name.get(name)

    def by_domain(self, domain: str) -> list[BenchmarkEntry]:
        """Get all benchmarks in a domain."""
        return self._by_domain.get(domain, [])

    def by_category(self, category: str) -> list[BenchmarkEntry]:
        """Get all benchmarks in a category."""
        return self._by_category.get(category, [])

    def by_tag(self, tag: str) -> list[BenchmarkEntry]:
        """Get all benchmarks with a specific tag."""
        return self._by_tag.get(tag, [])

    def by_year_range(self, start: int, end: int) -> list[BenchmarkEntry]:
        """Get benchmarks published in a year range."""
        return [e for e in self._entries if start <= e.year <= end]

    def with_gaming_vectors(self) -> list[BenchmarkEntry]:
        """Get benchmarks that have known gaming/contamination vectors."""
        return [e for e in self._entries if e.gaming_vectors]

    def with_correctness_requirements(self) -> list[BenchmarkEntry]:
        """Get benchmarks that enforce correctness verification."""
        return [e for e in self._entries if e.correctness_requirements]

    def search(self, query: str) -> list[BenchmarkEntry]:
        """Simple text search across benchmark names, descriptions, and tags."""
        query_lower = query.lower()
        results = []
        for entry in self._entries:
            searchable = (
                entry.name.lower()
                + " " + entry.description.lower()
                + " " + " ".join(entry.tags)
                + " " + " ".join(entry.task_types)
            )
            if query_lower in searchable:
                results.append(entry)
        return results

    def gaming_analysis(self) -> dict[str, Any]:
        """Analyze gaming vectors across the entire benchmark landscape."""
        all_vectors: dict[str, int] = {}
        for entry in self._entries:
            for vector in entry.gaming_vectors:
                all_vectors[vector] = all_vectors.get(vector, 0) + 1

        return {
            "total_benchmarks_analyzed": len(self._entries),
            "benchmarks_with_gaming_vectors": len(self.with_gaming_vectors()),
            "unique_gaming_vectors": len(all_vectors),
            "most_common_vectors": sorted(
                all_vectors.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "most_vulnerable_domains": {
                domain: sum(1 for e in entries if e.gaming_vectors)
                for domain, entries in self._by_domain.items()
            },
        }

    def correctness_landscape(self) -> dict[str, Any]:
        """Analyze correctness enforcement across the benchmark ecosystem."""
        enforcement_types: dict[str, int] = {}
        for entry in self._entries:
            for req in entry.correctness_requirements:
                enforcement_types[req] = enforcement_types.get(req, 0) + 1

        return {
            "total_with_correctness": len(self.with_correctness_requirements()),
            "total_without_correctness": len(self._entries) - len(self.with_correctness_requirements()),
            "enforcement_types": enforcement_types,
            "domains_without_correctness": [
                domain for domain, entries in self._by_domain.items()
                if not any(e.correctness_requirements for e in entries)
            ],
        }

    def export_jsonl(self, path: Path) -> None:
        """Export the knowledge base to JSONL format."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for entry in self._entries:
                handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")

    def summary(self) -> dict[str, Any]:
        """Get a high-level summary of the knowledge base."""
        return {
            "total_benchmarks": self.total_benchmarks,
            "domains": self.domains,
            "domain_counts": {d: len(e) for d, e in self._by_domain.items()},
            "categories": len(self.categories),
            "year_range": (
                min(e.year for e in self._entries) if self._entries else 0,
                max(e.year for e in self._entries) if self._entries else 0,
            ),
            "total_gaming_vectors": sum(len(e.gaming_vectors) for e in self._entries),
            "total_tags": len(self.tags),
        }
