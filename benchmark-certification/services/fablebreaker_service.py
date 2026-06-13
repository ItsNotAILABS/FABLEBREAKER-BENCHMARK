from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "suites" / "fablebreaker"
MANIFEST = ROOT / "manifests" / "benchmark-manifest.json"

SERVICE_VERSION = "0.2.0"

logger = logging.getLogger("fablebreaker_service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Optional API token for authentication (set via environment variable)
API_TOKEN = os.environ.get("FABLEBREAKER_API_TOKEN", "")


def _check_auth(handler: "FableBreakerHandler") -> bool:
    """Validate API token if configured. Returns True if authorized."""
    if not API_TOKEN:
        return True  # No token configured — local-only mode
    auth = handler.headers.get("Authorization", "")
    if auth == f"******":
        return True
    handler.reply({"error": "unauthorized"}, status=401)
    return False


def run_json(command: list[str], cwd: Path = SUITE) -> tuple[int, str]:
    """Execute a subprocess and return (returncode, output).

    Security note: command is always a list (no shell=True), and all user-provided
    values are validated/sanitized before being included in the command list.
    """
    proc = subprocess.run(  # noqa: S603 - command list is sanitized by callers
        command, cwd=cwd, text=True, capture_output=True, shell=False,
    )
    return proc.returncode, proc.stdout if proc.returncode == 0 else proc.stderr


class FableBreakerHandler(BaseHTTPRequestHandler):
    server_version = f"FableBreakerService/{SERVICE_VERSION}"

    def do_GET(self) -> None:
        if not _check_auth(self):
            return
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.reply({"ok": True, "suite": "fablebreaker", "version": SERVICE_VERSION})
            return
        if parsed.path == "/manifest":
            try:
                self.reply(json.loads(MANIFEST.read_text(encoding="utf-8")))
            except FileNotFoundError:
                self.reply({"error": "manifest_not_found"}, status=500)
            return
        if parsed.path == "/score":
            query = parse_qs(parsed.query)
            dataset = query.get("dataset", ["dataset/public.jsonl"])[0]
            candidate = query.get("candidate", ["candidates.baseline_candidate"])[0]
            self._handle_score(dataset, candidate)
            return
        self.reply({"error": "not_found", "paths": ["/health", "/manifest", "/score"]}, status=404)

    def do_POST(self) -> None:
        if not _check_auth(self):
            return
        parsed = urlparse(self.path)
        if parsed.path != "/generate":
            self.reply({"error": "not_found", "paths": ["/generate"]}, status=404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size) or b"{}")
        try:
            seed = int(payload.get("seed", 1701))
            count = int(payload.get("count", 240))
        except (TypeError, ValueError):
            self.reply({"error": "seed and count must be integers"}, status=400)
            return
        if not 0 <= seed <= 2**31 or not 1 <= count <= 10000:
            self.reply({"error": "seed must be 0..2^31, count must be 1..10000"}, status=400)
            return
        split = payload.get("split", "hidden")
        out = payload.get("out", f"dataset/{split}_seed_{seed}.jsonl")
        if split not in {"public", "hidden"}:
            self.reply({"error": "split must be public or hidden"}, status=400)
            return
        if not out.startswith("dataset/") or ".." in out:
            self.reply({"error": "out must stay under dataset/ with no path traversal"}, status=400)
            return
        logger.info("Generate request: seed=%d count=%d split=%s out=%s", seed, count, split, out)
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

    def _handle_score(self, dataset: str, candidate: str) -> None:
        if not dataset.startswith("dataset/") or ".." in dataset:
            self.reply({"error": "dataset must stay under dataset/ with no path traversal"}, status=400)
            return
        if "/" in candidate or "\\" in candidate or ".." in candidate:
            self.reply({"error": "candidate must be a Python module path, not a filesystem path"}, status=400)
            return
        # Validate candidate is a safe module path (alphanumeric, dots, underscores only)
        if not all(c.isalnum() or c in "._" for c in candidate):
            self.reply({"error": "candidate contains invalid characters"}, status=400)
            return
        logger.info("Score request: candidate=%s dataset=%s", candidate, dataset)
        code, output = run_json([sys.executable, "-m", "fablebreaker.scorer", "--dataset", dataset, "--candidate", candidate])
        if code == 0:
            self.reply(json.loads(output))
        else:
            self.reply({"ok": False, "error": "scoring failed"}, status=500)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        logger.debug(format, *args)

    def reply(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Service-Version", SERVICE_VERSION)
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="FableBreaker Benchmark Certification Service")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=8787, help="Listen port")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))
    server = ThreadingHTTPServer((args.host, args.port), FableBreakerHandler)
    logger.info("FableBreaker service v%s listening on http://%s:%d", SERVICE_VERSION, args.host, args.port)
    if API_TOKEN:
        logger.info("API token authentication enabled")
    else:
        logger.info("No API token configured — running in local-only mode")
    server.serve_forever()


if __name__ == "__main__":
    main()
