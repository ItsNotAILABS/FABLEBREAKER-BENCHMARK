from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
SUITE = ROOT / "fablebreaker"
MANIFEST = ROOT / "benchmark-manifest.json"
DATA_DIR = SUITE / "data"
LEADERBOARD_PATH = DATA_DIR / "leaderboard.json"
REGRESSION_PATH = DATA_DIR / "regression_history.json"
SEED_REGISTRY_PATH = DATA_DIR / "seed_registry.json"

sys.path.insert(0, str(SUITE))


def run_json(command: list[str], cwd: Path = SUITE) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, proc.stdout if proc.returncode == 0 else proc.stderr


class FableBreakerHandler(BaseHTTPRequestHandler):
    server_version = "FableBreakerService/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.reply({"ok": True, "suite": "fablebreaker", "version": "1.0.0"})
            return
        if parsed.path == "/manifest":
            self.reply(json.loads(MANIFEST.read_text(encoding="utf-8")))
            return
        if parsed.path == "/score":
            query = parse_qs(parsed.query)
            dataset = query.get("dataset", ["dataset/public.jsonl"])[0]
            candidate = query.get("candidate", ["candidates.baseline_candidate"])[0]
            self._score(dataset, candidate)
            return
        if parsed.path == "/leaderboard":
            self._get_leaderboard(parsed)
            return
        if parsed.path == "/seed-commitments":
            self._get_seed_commitments()
            return
        if parsed.path == "/regression":
            query = parse_qs(parsed.query)
            candidate = query.get("candidate", [None])[0]
            self._get_regression(candidate)
            return
        self.reply({
            "error": "not_found",
            "endpoints": {
                "GET": ["/health", "/manifest", "/score", "/leaderboard", "/seed-commitments", "/regression"],
                "POST": ["/generate", "/claim-audit", "/certify", "/batch-audit"],
            },
        }, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size) if size else b"{}"

        if parsed.path == "/generate":
            self._generate(body)
            return
        if parsed.path == "/claim-audit":
            self._claim_audit(body)
            return
        if parsed.path == "/certify":
            self._certify(body)
            return
        if parsed.path == "/batch-audit":
            self._batch_audit(body)
            return
        self.reply({"error": "not_found"}, status=404)

    def _generate(self, body: bytes) -> None:
        payload = json.loads(body or b"{}")
        seed = int(payload.get("seed", 1701))
        count = int(payload.get("count", 240))
        split = payload.get("split", "hidden")
        out = payload.get("out", f"dataset/{split}_seed_{seed}.jsonl")
        if split not in {"public", "hidden"}:
            self.reply({"error": "split must be public or hidden"}, status=400)
            return
        if not out.startswith("dataset/"):
            self.reply({"error": "out must stay under dataset/"}, status=400)
            return
        code, output = run_json(
            [
                sys.executable, "-m", "fablebreaker.generator",
                "--out", out, "--count", str(count),
                "--seed", str(seed), "--split", split,
            ]
        )
        self.reply({"ok": code == 0, "out": out, "seed": seed, "count": count, "output": output}, status=200 if code == 0 else 500)

    def _claim_audit(self, body: bytes) -> None:
        payload = json.loads(body or b"{}")
        candidate = payload.get("candidate")
        if not candidate:
            self.reply({"error": "candidate is required"}, status=400)
            return
        if "/" in candidate or "\\" in candidate:
            self.reply({"error": "candidate must be a Python module path"}, status=400)
            return

        public_seed = int(payload.get("public_seed", 823))
        count = int(payload.get("count", 240))
        repeat = int(payload.get("repeat", 1))
        source_ref = payload.get("source_ref", "")
        operator = payload.get("operator", "api-submission")
        notes = payload.get("notes", "")

        cmd = [
            sys.executable, "-m", "tools.claim_audit",
            "--candidate", candidate,
            "--public-seed", str(public_seed),
            "--count", str(count),
            "--repeat", str(repeat),
            "--source-ref", source_ref,
            "--operator", operator,
            "--notes", notes,
        ]
        code, output = run_json(cmd)
        if code == 0:
            reports_dir = SUITE / "reports"
            packs = sorted(reports_dir.glob(f"evidence-pack-{candidate.replace('.', '_')}*.json"))
            if packs:
                pack = json.loads(packs[-1].read_text(encoding="utf-8"))
                self._record_to_leaderboard(pack)
                self._record_regression(pack)
                self.reply(pack)
            else:
                self.reply({"ok": True, "output": output})
        else:
            self.reply({"ok": False, "error": output}, status=500)

    def _certify(self, body: bytes) -> None:
        payload = json.loads(body or b"{}")
        candidate = payload.get("candidate")
        if not candidate:
            self.reply({"error": "candidate is required"}, status=400)
            return
        if "/" in candidate or "\\" in candidate:
            self.reply({"error": "candidate must be a Python module path"}, status=400)
            return

        count = int(payload.get("count", 240))
        repeat = int(payload.get("repeat", 1))

        from fablebreaker.seeds import SeedRegistry
        registry = SeedRegistry(SEED_REGISTRY_PATH)
        active = registry.active_seeds()
        if not active:
            new_entry = registry.rotate()
            hidden_seed = new_entry.seed
        else:
            hidden_seed = active[-1].seed

        cmd = [
            sys.executable, "-m", "tools.claim_audit",
            "--candidate", candidate,
            "--hidden-seed", str(hidden_seed),
            "--count", str(count),
            "--repeat", str(repeat),
            "--operator", "certification-service",
        ]
        code, output = run_json(cmd)
        if code == 0:
            reports_dir = SUITE / "reports"
            packs = sorted(reports_dir.glob(f"evidence-pack-{candidate.replace('.', '_')}*.json"))
            if packs:
                pack = json.loads(packs[-1].read_text(encoding="utf-8"))
                self._record_to_leaderboard(pack)
                self._record_regression(pack)
                self.reply({
                    "certified": pack["overall_certified"],
                    "speedup": pack["overall_speedup"],
                    "evidence_pack": pack,
                })
            else:
                self.reply({"ok": True, "output": output})
        else:
            self.reply({"ok": False, "error": output}, status=500)

    def _batch_audit(self, body: bytes) -> None:
        """Test 30-100+ agents in a single API call.

        POST /batch-audit
        {
            "candidates": ["candidates.agent_1", "candidates.agent_2", ...],
            "discover": "candidates",           // optional: auto-discover from directory
            "scan_dirs": ["/path/to/repo"],      // optional: scan external repos
            "public_seed": 823,
            "hidden_seeds": [1701, 9999],
            "count": 240,
            "workers": 4
        }
        """
        payload = json.loads(body or b"{}")
        candidates_list = payload.get("candidates", [])
        discover_dir = payload.get("discover")
        scan_dirs = payload.get("scan_dirs", [])
        public_seed = int(payload.get("public_seed", 823))
        hidden_seeds = [int(s) for s in payload.get("hidden_seeds", [1701])]
        count = int(payload.get("count", 240))
        workers = int(payload.get("workers", 4))

        # Validate candidates don't contain path traversal
        for cand in candidates_list:
            if "/" in cand or "\\" in cand:
                self.reply({"error": f"candidate must be a Python module path: {cand}"}, status=400)
                return

        # Discover from package directory
        if discover_dir:
            if "/" in discover_dir or "\\" in discover_dir:
                self.reply({"error": "discover must be a package name, not a path"}, status=400)
                return
            from tools.repo_scanner import discover_candidates
            discovered = discover_candidates(SUITE / discover_dir)
            candidates_list.extend(discovered)

        # Scan external dirs
        if scan_dirs:
            from tools.repo_scanner import scan_external_dirs
            scanned = scan_external_dirs(scan_dirs)
            candidates_list.extend(scanned)

        if not candidates_list:
            self.reply({"error": "No candidates specified or discovered"}, status=400)
            return

        # Deduplicate
        candidates_list = list(dict.fromkeys(candidates_list))

        # Run batch audit
        from tools.batch_audit import run_batch_audit
        try:
            report = run_batch_audit(
                candidates=candidates_list,
                public_seed=public_seed,
                hidden_seeds=hidden_seeds,
                count=count,
                workers=workers,
            )
            self.reply(report)
        except Exception as exc:  # noqa: BLE001 - service must not crash
            self.reply({"ok": False, "error": str(exc)}, status=500)

    def _score(self, dataset: str, candidate: str) -> None:
        if not dataset.startswith("dataset/"):
            self.reply({"error": "dataset must stay under dataset/"}, status=400)
            return
        if "/" in candidate or "\\" in candidate:
            self.reply({"error": "candidate must be a Python module path, not a filesystem path"}, status=400)
            return
        code, output = run_json([sys.executable, "-m", "fablebreaker.scorer", "--dataset", dataset, "--candidate", candidate])
        if code == 0:
            self.reply(json.loads(output))
        else:
            self.reply({"ok": False, "error": output}, status=500)

    def _get_leaderboard(self, parsed) -> None:
        query = parse_qs(parsed.query)
        certified_only = query.get("certified_only", ["true"])[0].lower() == "true"
        limit = int(query.get("limit", ["50"])[0])
        if LEADERBOARD_PATH.exists():
            from fablebreaker.leaderboard import Leaderboard
            lb = Leaderboard(LEADERBOARD_PATH)
            self.reply(lb.to_dict(certified_only=certified_only, limit=limit))
        else:
            self.reply({"leaderboard": [], "total_submissions": 0, "certified_submissions": 0})

    def _get_seed_commitments(self) -> None:
        if SEED_REGISTRY_PATH.exists():
            from fablebreaker.seeds import SeedRegistry
            registry = SeedRegistry(SEED_REGISTRY_PATH)
            self.reply({"commitments": registry.commitments()})
        else:
            self.reply({"commitments": []})

    def _get_regression(self, candidate: str | None) -> None:
        if REGRESSION_PATH.exists():
            from fablebreaker.regression import RegressionMonitor
            monitor = RegressionMonitor(REGRESSION_PATH)
            if candidate:
                history = monitor.history(candidate)
                self.reply({
                    "candidate": candidate,
                    "runs": len(history),
                    "history": [
                        {
                            "timestamp": r.timestamp_utc,
                            "certified": r.certified,
                            "speedup": r.speedup,
                            "failed": r.total_failed,
                        }
                        for r in history
                    ],
                })
            else:
                self.reply(monitor.summary())
        else:
            self.reply({"total_records": 0, "candidates_tracked": 0, "candidates": {}})

    def _record_to_leaderboard(self, pack: dict) -> None:
        from fablebreaker.leaderboard import Leaderboard
        LEADERBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        lb = Leaderboard(LEADERBOARD_PATH)
        lb.submit(pack)

    def _record_regression(self, pack: dict) -> None:
        from fablebreaker.regression import RegressionMonitor
        REGRESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        monitor = RegressionMonitor(REGRESSION_PATH)
        monitor.record_from_pack(pack)

    def log_message(self, format: str, *args: object) -> None:
        return

    def reply(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="FableBreaker Certification Service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FableBreakerHandler)
    print(f"FableBreaker Certification Service listening on http://{args.host}:{args.port}")
    print("Endpoints:")
    print("  GET  /health            - Service health check")
    print("  GET  /manifest          - Benchmark manifest")
    print("  GET  /score             - Score a candidate on a dataset")
    print("  GET  /leaderboard       - View certified leaderboard")
    print("  GET  /seed-commitments  - View hidden seed commitments")
    print("  GET  /regression        - Regression monitoring history")
    print("  POST /generate          - Generate a dataset")
    print("  POST /claim-audit       - Submit a claim for full audit")
    print("  POST /certify           - Certify a candidate (hidden seeds)")
    print("  POST /batch-audit       - Test 30-100+ agents in parallel")
    server.serve_forever()


if __name__ == "__main__":
    main()
