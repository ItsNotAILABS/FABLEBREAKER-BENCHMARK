from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fablebreaker.evidence import generate_evidence_pack, save_evidence_pack
from fablebreaker.generator import main as generate_main
from fablebreaker.scorer import score
from fablebreaker.seeds import SeedRegistry


ROOT = Path(__file__).resolve().parents[1]


def run_claim_audit(
    candidate: str,
    public_seed: int = 823,
    hidden_seed: int | None = None,
    count: int = 240,
    repeat: int = 1,
    signing_secret: str | None = None,
    output_dir: Path | None = None,
    candidate_source_ref: str = "",
    operator: str = "self-audit",
    notes: str = "",
) -> dict:
    if output_dir is None:
        output_dir = ROOT / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = SeedRegistry(ROOT / "data" / "seed_registry.json")

    if hidden_seed is None:
        active = registry.active_seeds()
        if active:
            hidden_seed = active[-1].seed
        else:
            import os
            hidden_seed = int.from_bytes(os.urandom(4), "big")
            registry.register_seed(hidden_seed)

    registry.register_seed(public_seed)
    registry.register_seed(hidden_seed)

    public_path = ROOT / "dataset" / "public.jsonl"
    hidden_path = ROOT / "dataset" / f"hidden_seed_{hidden_seed}.jsonl"

    print(f"[claim-audit] Generating public dataset (seed={public_seed}, count={count})...")
    _generate_dataset(public_path, count, public_seed, "public")

    print(f"[claim-audit] Generating hidden dataset (seed={hidden_seed}, count={count})...")
    _generate_dataset(hidden_path, count, hidden_seed, "hidden")

    print(f"[claim-audit] Scoring candidate '{candidate}' on public dataset...")
    public_score = score(public_path, candidate, repeat)

    print(f"[claim-audit] Scoring candidate '{candidate}' on hidden dataset...")
    hidden_score = score(hidden_path, candidate, repeat)

    print("[claim-audit] Generating evidence pack...")
    pack = generate_evidence_pack(
        candidate_name=candidate,
        candidate_source_ref=candidate_source_ref,
        public_score=public_score,
        hidden_score=hidden_score,
        public_seed=public_seed,
        hidden_seed=hidden_seed,
        operator=operator,
        signing_secret=signing_secret,
        notes=notes,
    )

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pack_path = output_dir / f"evidence-pack-{candidate.replace('.', '_')}-{timestamp}.json"
    save_evidence_pack(pack, pack_path)

    public_score_path = output_dir / f"score-public-{candidate.replace('.', '_')}-{timestamp}.json"
    hidden_score_path = output_dir / f"score-hidden-{candidate.replace('.', '_')}-{timestamp}.json"
    public_score_path.write_text(json.dumps(public_score, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hidden_score_path.write_text(json.dumps(hidden_score, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    certified = pack["overall_certified"]
    speedup = pack["overall_speedup"]

    print()
    print("=" * 60)
    print("  FABLEBREAKER CLAIM AUDIT RESULT")
    print("=" * 60)
    print(f"  Candidate:    {candidate}")
    print(f"  Certified:    {'YES' if certified else 'NO'}")
    if certified:
        print(f"  Speedup:      {speedup:.3f}x vs reference")
    else:
        print(f"  Failed cases: {pack['total_failed']}/{pack['total_cases']}")
    print(f"  Evidence:     {pack_path}")
    print("=" * 60)
    print()

    return {
        "certified": certified,
        "speedup": speedup,
        "evidence_pack_path": str(pack_path),
        "public_score_path": str(public_score_path),
        "hidden_score_path": str(hidden_score_path),
        "pack": pack,
    }


def _generate_dataset(path: Path, count: int, seed: int, split: str) -> None:
    import random
    from fablebreaker.generator import make_case

    path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    with path.open("w", encoding="utf-8") as handle:
        for idx in range(count):
            handle.write(json.dumps(make_case(rng, idx, split), sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FableBreaker Claim Audit: prove your speedup survives adversarial correctness."
    )
    parser.add_argument("--candidate", required=True, help="Python module path (e.g., candidates.baseline_candidate)")
    parser.add_argument("--public-seed", type=int, default=823)
    parser.add_argument("--hidden-seed", type=int, default=None, help="Hidden seed (auto-generated if omitted)")
    parser.add_argument("--count", type=int, default=240, help="Cases per split")
    parser.add_argument("--repeat", type=int, default=1, help="Timing repetitions per case")
    parser.add_argument("--signing-secret", default=None, help="HMAC secret for evidence signing")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--source-ref", default="", help="Git commit or reference for the candidate")
    parser.add_argument("--operator", default="self-audit")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    run_claim_audit(
        candidate=args.candidate,
        public_seed=args.public_seed,
        hidden_seed=args.hidden_seed,
        count=args.count,
        repeat=args.repeat,
        signing_secret=args.signing_secret,
        output_dir=args.output_dir,
        candidate_source_ref=args.source_ref,
        operator=args.operator,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
