from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="candidates.baseline_candidate")
    parser.add_argument("--public-seed", type=int, default=823)
    parser.add_argument("--hidden-seed", type=int, default=1701)
    parser.add_argument("--count", type=int, default=240)
    args = parser.parse_args()

    public_path = ROOT / "dataset" / "public.jsonl"
    hidden_path = ROOT / "dataset" / f"hidden_seed_{args.hidden_seed}.jsonl"
    public_score = ROOT / "reports" / "audit_public_score.json"
    hidden_score = ROOT / "reports" / f"audit_hidden_seed_{args.hidden_seed}_score.json"

    run([sys.executable, "-m", "compileall", "fablebreaker", "candidates", "tests"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
    run([sys.executable, "-m", "fablebreaker.generator", "--out", str(public_path), "--count", str(args.count), "--seed", str(args.public_seed), "--split", "public"])
    run([sys.executable, "-m", "fablebreaker.generator", "--out", str(hidden_path), "--count", str(args.count), "--seed", str(args.hidden_seed), "--split", "hidden"])
    run([sys.executable, "-m", "fablebreaker.scorer", "--dataset", str(public_path), "--candidate", args.candidate, "--json-out", str(public_score)])
    run([sys.executable, "-m", "fablebreaker.scorer", "--dataset", str(hidden_path), "--candidate", args.candidate, "--json-out", str(hidden_score)])

    summary = {
        "candidate": args.candidate,
        "public_score": str(public_score.relative_to(ROOT)),
        "hidden_score": str(hidden_score.relative_to(ROOT)),
        "count_per_split": args.count,
        "public_seed": args.public_seed,
        "hidden_seed": args.hidden_seed,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
