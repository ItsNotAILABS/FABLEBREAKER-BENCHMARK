"""FableBreaker Batch Audit: Test 30-100+ agents/candidates in parallel.

Usage:
    # Test all candidates in candidates/ directory:
    python -m tools.batch_audit --discover candidates

    # Test specific candidate modules:
    python -m tools.batch_audit --candidates candidates.agent_1 candidates.agent_2 candidates.agent_3

    # Test candidates from external repos/directories:
    python -m tools.batch_audit --scan-dirs /path/to/repo1 /path/to/repo2

    # Full swarm test (100 agents, 1000 cases, 4 workers):
    python -m tools.batch_audit --discover candidates --count 1000 --workers 4

    # Custom hidden seeds for adversarial testing:
    python -m tools.batch_audit --discover candidates --hidden-seeds 1701 9999 31337
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fablebreaker.scorer import score
from tools.repo_scanner import discover_candidates, scan_external_dirs


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class AgentResult:
    candidate: str
    certified: bool = False
    speedup: float = 0.0
    total_cases: int = 0
    correct: int = 0
    failed: int = 0
    error: str | None = None
    elapsed_seconds: float = 0.0
    public_score: dict[str, Any] = field(default_factory=dict)
    hidden_scores: list[dict[str, Any]] = field(default_factory=list)
    failure_families: list[str] = field(default_factory=list)


def _generate_dataset(path: Path, count: int, seed: int, split: str) -> None:
    import random
    from fablebreaker.generator import make_case

    path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    with path.open("w", encoding="utf-8") as handle:
        for idx in range(count):
            handle.write(json.dumps(make_case(rng, idx, split), sort_keys=True) + "\n")


def _audit_single_candidate(
    candidate_module: str,
    public_path: str,
    hidden_paths: list[str],
    repeat: int,
) -> dict[str, Any]:
    """Run in a subprocess: score one candidate against public + hidden datasets."""
    result: dict[str, Any] = {
        "candidate": candidate_module,
        "certified": False,
        "speedup": 0.0,
        "total_cases": 0,
        "correct": 0,
        "failed": 0,
        "error": None,
        "elapsed_seconds": 0.0,
        "public_score": {},
        "hidden_scores": [],
        "failure_families": [],
    }
    start = time.perf_counter()
    try:
        pub_score = score(Path(public_path), candidate_module, repeat)
        result["public_score"] = pub_score
        result["total_cases"] += pub_score["cases"]
        result["correct"] += pub_score["correct"]
        result["failed"] += pub_score["failed"]

        all_certified = pub_score["certified"]

        for hp in hidden_paths:
            h_score = score(Path(hp), candidate_module, repeat)
            result["hidden_scores"].append(h_score)
            result["total_cases"] += h_score["cases"]
            result["correct"] += h_score["correct"]
            result["failed"] += h_score["failed"]
            if not h_score["certified"]:
                all_certified = False
                # Track which families broke
                for family, diag in h_score.get("family_diagnostics", {}).items():
                    if diag.get("failed", 0) > 0:
                        result["failure_families"].append(family)

        result["certified"] = all_certified
        if all_certified:
            # Speedup = minimum across all datasets (conservative)
            speedups = [pub_score.get("speedup_vs_reference", 0.0)]
            for hs in result["hidden_scores"]:
                speedups.append(hs.get("speedup_vs_reference", 0.0))
            result["speedup"] = min(speedups) if speedups else 0.0

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

    result["elapsed_seconds"] = time.perf_counter() - start
    return result


def run_batch_audit(
    candidates: list[str],
    public_seed: int = 823,
    hidden_seeds: list[int] | None = None,
    count: int = 240,
    repeat: int = 1,
    workers: int = 4,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run FableBreaker audit on multiple candidates (30-100+) in parallel."""
    if hidden_seeds is None:
        hidden_seeds = [1701]
    if output_dir is None:
        output_dir = ROOT / "reports" / "batch"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate datasets
    public_path = ROOT / "dataset" / "batch_public.jsonl"
    _generate_dataset(public_path, count, public_seed, "public")

    hidden_paths: list[Path] = []
    for seed in hidden_seeds:
        hp = ROOT / "dataset" / f"batch_hidden_{seed}.jsonl"
        _generate_dataset(hp, count, seed, "hidden")
        hidden_paths.append(hp)

    print(f"\n{'='*70}")
    print(f"  FABLEBREAKER BATCH AUDIT: {len(candidates)} AGENTS")
    print(f"{'='*70}")
    print(f"  Public seed:    {public_seed} ({count} cases)")
    print(f"  Hidden seeds:   {hidden_seeds} ({count} cases each)")
    print(f"  Total cases:    {count * (1 + len(hidden_seeds))} per agent")
    print(f"  Workers:        {workers}")
    print(f"  Candidates:     {len(candidates)}")
    print(f"{'='*70}\n")

    results: list[dict[str, Any]] = []

    if workers <= 1:
        # Sequential mode (easier to debug)
        for i, cand in enumerate(candidates):
            print(f"  [{i+1}/{len(candidates)}] Testing {cand}...")
            r = _audit_single_candidate(
                cand, str(public_path), [str(p) for p in hidden_paths], repeat
            )
            results.append(r)
            status = "CERTIFIED" if r["certified"] else "FAILED"
            if r["error"]:
                status = "ERROR"
            print(f"           -> {status} ({r['correct']}/{r['total_cases']} correct, {r['elapsed_seconds']:.2f}s)")
    else:
        # Parallel mode for large agent counts
        futures = {}
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for cand in candidates:
                fut = executor.submit(
                    _audit_single_candidate,
                    cand,
                    str(public_path),
                    [str(p) for p in hidden_paths],
                    repeat,
                )
                futures[fut] = cand

            done_count = 0
            for fut in as_completed(futures):
                done_count += 1
                cand = futures[fut]
                try:
                    r = fut.result()
                except Exception as exc:  # noqa: BLE001
                    r = {"candidate": cand, "certified": False, "error": str(exc),
                         "total_cases": 0, "correct": 0, "failed": 0,
                         "speedup": 0.0, "elapsed_seconds": 0.0,
                         "public_score": {}, "hidden_scores": [],
                         "failure_families": []}
                results.append(r)
                status = "CERTIFIED" if r["certified"] else "FAILED"
                if r.get("error"):
                    status = "ERROR"
                print(f"  [{done_count}/{len(candidates)}] {cand} -> {status}")

    # Build consolidated report
    report = _build_report(results, candidates, public_seed, hidden_seeds, count, repeat)

    # Save report
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_path = output_dir / f"batch-report-{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Print summary
    _print_summary(report, report_path)

    return report


def _build_report(
    results: list[dict[str, Any]],
    candidates: list[str],
    public_seed: int,
    hidden_seeds: list[int],
    count: int,
    repeat: int,
) -> dict[str, Any]:
    certified_count = sum(1 for r in results if r["certified"])
    failed_count = sum(1 for r in results if not r["certified"] and not r.get("error"))
    error_count = sum(1 for r in results if r.get("error"))

    # Rank by speedup (certified first)
    ranked = sorted(results, key=lambda r: (r["certified"], r["speedup"]), reverse=True)

    # Failure analysis: which families break agents most?
    family_failures: dict[str, int] = {}
    for r in results:
        for fam in r.get("failure_families", []):
            family_failures[fam] = family_failures.get(fam, 0) + 1

    return {
        "batch_audit_version": "1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "configuration": {
            "total_agents": len(candidates),
            "public_seed": public_seed,
            "hidden_seeds": hidden_seeds,
            "cases_per_dataset": count,
            "repeat": repeat,
        },
        "summary": {
            "total_agents_tested": len(results),
            "certified": certified_count,
            "failed_correctness": failed_count,
            "errored": error_count,
            "certification_rate": certified_count / len(results) if results else 0,
            "best_speedup": max((r["speedup"] for r in results), default=0),
            "median_speedup": sorted(r["speedup"] for r in results if r["certified"])[
                len([r for r in results if r["certified"]]) // 2
            ] if certified_count else 0,
        },
        "failure_analysis": {
            "most_broken_families": dict(sorted(family_failures.items(), key=lambda x: x[1], reverse=True)),
            "agents_with_errors": [r["candidate"] for r in results if r.get("error")],
            "agents_with_failures": [
                {"candidate": r["candidate"], "failed": r["failed"], "families": r.get("failure_families", [])}
                for r in results if r["failed"] > 0 and not r.get("error")
            ],
        },
        "ranked_results": [
            {
                "rank": i + 1,
                "candidate": r["candidate"],
                "certified": r["certified"],
                "speedup": r["speedup"],
                "correct": r["correct"],
                "total_cases": r["total_cases"],
                "failed": r["failed"],
                "elapsed_seconds": r["elapsed_seconds"],
                "error": r.get("error"),
            }
            for i, r in enumerate(ranked)
        ],
        "detailed_results": results,
    }


def _print_summary(report: dict[str, Any], report_path: Path) -> None:
    summary = report["summary"]
    config = report["configuration"]
    ranked = report["ranked_results"]

    print(f"\n{'='*70}")
    print(f"  BATCH AUDIT COMPLETE")
    print(f"{'='*70}")
    print(f"  Agents tested:      {summary['total_agents_tested']}")
    print(f"  Certified:          {summary['certified']} ({summary['certification_rate']*100:.1f}%)")
    print(f"  Failed correctness: {summary['failed_correctness']}")
    print(f"  Errored:            {summary['errored']}")
    print(f"  Best speedup:       {summary['best_speedup']:.3f}x")
    print()

    # Top 10 leaderboard
    print("  TOP AGENTS (by speedup, certified only):")
    print(f"  {'Rank':<5} {'Candidate':<40} {'Speedup':<10} {'Correct':<12}")
    print(f"  {'-'*5} {'-'*40} {'-'*10} {'-'*12}")
    shown = 0
    for r in ranked:
        if r["certified"] and shown < 10:
            shown += 1
            print(f"  {r['rank']:<5} {r['candidate']:<40} {r['speedup']:<10.3f} {r['correct']}/{r['total_cases']}")
    if shown == 0:
        print("  (no certified agents)")

    # Failure summary
    failures = report["failure_analysis"]
    if failures["most_broken_families"]:
        print()
        print("  MOST COMMON FAILURE FAMILIES:")
        for fam, count in list(failures["most_broken_families"].items())[:5]:
            print(f"    {fam}: broke {count} agent(s)")

    if failures["agents_with_errors"]:
        print()
        print(f"  AGENTS WITH ERRORS ({len(failures['agents_with_errors'])}):")
        for agent in failures["agents_with_errors"][:10]:
            print(f"    - {agent}")

    print()
    print(f"  Full report: {report_path}")
    print(f"{'='*70}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FableBreaker Batch Audit: test 30-100+ agents in parallel."
    )
    parser.add_argument("--candidates", nargs="*", help="Explicit list of candidate module paths")
    parser.add_argument("--discover", help="Auto-discover candidates from a package directory (e.g., 'candidates')")
    parser.add_argument("--scan-dirs", nargs="*", help="Scan external directories/repos for evaluate() functions")
    parser.add_argument("--public-seed", type=int, default=823)
    parser.add_argument("--hidden-seeds", nargs="*", type=int, default=[1701])
    parser.add_argument("--count", type=int, default=240, help="Cases per dataset")
    parser.add_argument("--repeat", type=int, default=1, help="Timing repetitions per case")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker processes (1=sequential)")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    # Collect all candidates
    all_candidates: list[str] = []

    if args.candidates:
        all_candidates.extend(args.candidates)

    if args.discover:
        discovered = discover_candidates(ROOT / args.discover)
        all_candidates.extend(discovered)
        print(f"Discovered {len(discovered)} candidates in {args.discover}/")

    if args.scan_dirs:
        scanned = scan_external_dirs(args.scan_dirs)
        all_candidates.extend(scanned)
        print(f"Scanned {len(scanned)} candidates from external directories")

    if not all_candidates:
        print("ERROR: No candidates found. Use --candidates, --discover, or --scan-dirs")
        sys.exit(1)

    # Deduplicate
    all_candidates = list(dict.fromkeys(all_candidates))

    print(f"\nTotal candidates to test: {len(all_candidates)}")
    if len(all_candidates) > 100:
        print(f"WARNING: Testing {len(all_candidates)} agents. This may take a while.")

    run_batch_audit(
        candidates=all_candidates,
        public_seed=args.public_seed,
        hidden_seeds=args.hidden_seeds,
        count=args.count,
        repeat=args.repeat,
        workers=args.workers,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
