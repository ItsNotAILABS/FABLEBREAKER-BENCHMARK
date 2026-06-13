from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
import uuid
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "suites" / "fablebreaker"
MANIFEST = ROOT / "manifests" / "benchmark-manifest.json"

SERVICE_VERSION = "0.2.0"
API_PREFIX = "/api/v1"

logger = logging.getLogger("fablebreaker_service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Simple rate limiter state
_rate_lock = Lock()
_rate_window: dict[str, deque] = {}
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60


def check_rate_limit(client_ip: str) -> bool:
    """Return True if request is within rate limits."""
    now = time.time()
    with _rate_lock:
        if client_ip not in _rate_window:
            _rate_window[client_ip] = deque()
        window = _rate_window[client_ip]
        # Remove expired entries
        while window and window[0] < now - RATE_LIMIT_WINDOW_SECONDS:
            window.popleft()
        if len(window) >= RATE_LIMIT_REQUESTS:
            return False
        window.append(now)
        return True


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

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Rate limit check
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.reply({"error": "rate_limit_exceeded", "retry_after_seconds": RATE_LIMIT_WINDOW_SECONDS}, status=429)
            return

        # Legacy routes (backward compatible)
        if path == "/health":
            self._handle_health()
            return
        if path == "/manifest":
            self._handle_manifest()
            return
        if path == "/score":
            query = parse_qs(parsed.query)
            dataset = query.get("dataset", ["dataset/public.jsonl"])[0]
            candidate = query.get("candidate", ["candidates.baseline_candidate"])[0]
            self._handle_score(dataset, candidate)
            return

        # Versioned API routes
        if path == f"{API_PREFIX}/health":
            self._handle_health()
            return
        if path == f"{API_PREFIX}/manifest":
            self._handle_manifest()
            return
        if path == f"{API_PREFIX}/status":
            self._handle_status()
            return
        if path == f"{API_PREFIX}/candidates":
            self._handle_candidates()
            return
        if path == f"{API_PREFIX}/families":
            self._handle_families()
            return
        if path == f"{API_PREFIX}/score":
            query = parse_qs(parsed.query)
            dataset = query.get("dataset", ["dataset/public.jsonl"])[0]
            candidate = query.get("candidate", ["candidates.baseline_candidate"])[0]
            self._handle_score(dataset, candidate)
            return

        self.reply({
            "error": "not_found",
            "available_routes": {
                "legacy": ["/health", "/manifest", "/score"],
                "v1": [
                    f"{API_PREFIX}/health",
                    f"{API_PREFIX}/manifest",
                    f"{API_PREFIX}/status",
                    f"{API_PREFIX}/candidates",
                    f"{API_PREFIX}/families",
                    f"{API_PREFIX}/score",
                ],
            },
        }, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.reply({"error": "rate_limit_exceeded", "retry_after_seconds": RATE_LIMIT_WINDOW_SECONDS}, status=429)
            return

        if path in ("/generate", f"{API_PREFIX}/generate"):
            self._handle_generate()
            return
        if path == f"{API_PREFIX}/score":
            self._handle_post_score()
            return

        self.reply({"error": "not_found", "paths": ["/generate", f"{API_PREFIX}/generate", f"{API_PREFIX}/score"]}, status=404)

    def _handle_health(self) -> None:
        self.reply({
            "ok": True,
            "suite": "fablebreaker",
            "version": SERVICE_VERSION,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

    def _handle_manifest(self) -> None:
        try:
            self.reply(json.loads(MANIFEST.read_text(encoding="utf-8")))
        except FileNotFoundError:
            self.reply({"error": "manifest_not_found"}, status=500)

    def _handle_status(self) -> None:
        dataset_dir = SUITE / "dataset"
        datasets = sorted(str(p.name) for p in dataset_dir.glob("*.jsonl")) if dataset_dir.exists() else []
        reports_dir = SUITE / "reports"
        reports = sorted(str(p.name) for p in reports_dir.glob("*.json")) if reports_dir.exists() else []
        self.reply({
            "service_version": SERVICE_VERSION,
            "suite_root": str(SUITE),
            "datasets_available": datasets,
            "reports_available": reports,
            "rate_limit": {
                "requests_per_window": RATE_LIMIT_REQUESTS,
                "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
            },
        })

    def _handle_candidates(self) -> None:
        candidates_dir = SUITE / "candidates"
        candidates = []
        if candidates_dir.exists():
            for p in sorted(candidates_dir.glob("*.py")):
                if p.name.startswith("_"):
                    continue
                candidates.append({
                    "module": f"candidates.{p.stem}",
                    "filename": p.name,
                })
        self.reply({"candidates": candidates})

    def _handle_families(self) -> None:
        families = [
            {"name": "dynamic_match_storm", "description": "Chains of pattern matches with multiple tag paths"},
            {"name": "del_erasure_trap", "description": "Erase nodes hiding bomb expressions that must not evaluate"},
            {"name": "duplication_aliasing", "description": "Shared values through dup with deep pair projections"},
            {"name": "branch_balance", "description": "Alternating KEEP/DEL tags with erasure in dead branches"},
            {"name": "deep_pair_projection", "description": "Deeply nested pair construction and path projection"},
            {"name": "modular_arithmetic_net", "description": "Large repeat loops with modular arithmetic"},
            {"name": "overflow_corridor", "description": "Overflow-prone expressions with large integer arithmetic"},
            {"name": "nested_conditional_cascade", "description": "Deeply nested if_zero/match cascades with erasure traps"},
        ]
        self.reply({"families": families, "count": len(families)})

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
        request_id = str(uuid.uuid4())[:8]
        logger.info("Score request %s: candidate=%s dataset=%s", request_id, candidate, dataset)
        start = time.time()
        code, output = run_json([sys.executable, "-m", "fablebreaker.scorer", "--dataset", dataset, "--candidate", candidate])
        elapsed = time.time() - start
        if code == 0:
            result = json.loads(output)
            result["request_id"] = request_id
            result["scoring_elapsed_seconds"] = round(elapsed, 3)
            self.reply(result)
        else:
            logger.error("Score request %s failed: %s", request_id, output)
            self.reply({"ok": False, "error": "scoring failed", "request_id": request_id}, status=500)

    def _handle_post_score(self) -> None:
        size = int(self.headers.get("Content-Length", "0"))
        if size == 0:
            self.reply({"error": "request body required"}, status=400)
            return
        payload = json.loads(self.rfile.read(size))
        dataset = payload.get("dataset", "dataset/public.jsonl")
        candidate = payload.get("candidate", "candidates.baseline_candidate")
        self._handle_score(dataset, candidate)

    def _handle_generate(self) -> None:
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

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        logger.debug(format, *args)

    def reply(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Service-Version", SERVICE_VERSION)
        self.send_header("X-Request-Time", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")


def main() -> None:
    parser = argparse.ArgumentParser(description="FableBreaker Benchmark Certification Service")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=8787, help="Listen port")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))
    server = ThreadingHTTPServer((args.host, args.port), FableBreakerHandler)
    logger.info("FableBreaker service v%s listening on http://%s:%d", SERVICE_VERSION, args.host, args.port)
    logger.info("API prefix: %s", API_PREFIX)
    server.serve_forever()


if __name__ == "__main__":
    main()
