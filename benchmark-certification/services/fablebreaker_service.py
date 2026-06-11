from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "suites" / "fablebreaker"
MANIFEST = ROOT / "manifests" / "benchmark-manifest.json"


def run_json(command: list[str], cwd: Path = SUITE) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, proc.stdout if proc.returncode == 0 else proc.stderr


class FableBreakerHandler(BaseHTTPRequestHandler):
    server_version = "FableBreakerService/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.reply({"ok": True, "suite": "fablebreaker"})
            return
        if parsed.path == "/manifest":
            self.reply(json.loads(MANIFEST.read_text(encoding="utf-8")))
            return
        if parsed.path == "/score":
            query = parse_qs(parsed.query)
            dataset = query.get("dataset", ["dataset/public.jsonl"])[0]
            candidate = query.get("candidate", ["candidates.baseline_candidate"])[0]
            self.score(dataset, candidate)
            return
        self.reply({"error": "not_found", "paths": ["/health", "/manifest", "/score"]}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/generate":
            self.reply({"error": "not_found", "paths": ["/generate"]}, status=404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size) or b"{}")
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
                sys.executable,
                "-m",
                "fablebreaker.generator",
                "--out",
                out,
                "--count",
                str(count),
                "--seed",
                str(seed),
                "--split",
                split,
            ]
        )
        self.reply({"ok": code == 0, "out": out, "seed": seed, "count": count, "output": output}, status=200 if code == 0 else 500)

    def score(self, dataset: str, candidate: str) -> None:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FableBreakerHandler)
    print(f"FableBreaker service listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
