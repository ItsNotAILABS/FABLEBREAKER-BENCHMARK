"""
FableBreaker AutoAgent — automated PR analysis engine.

This is the core logic that runs when the GitHub Action is triggered.
It scans changed files in a PR, runs FableBreaker analysis, and posts
results as PR comments or inline review annotations.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure SDK is importable
AGENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AGENT_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "fablebreaker_sdk"))

from fablebreaker_sdk import FableBreaker  # noqa: E402
from fablebreaker_sdk.scanner import CodeScanner  # noqa: E402
from fablebreaker_sdk.reporter import ReportGenerator  # noqa: E402


SEVERITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "critical": 3}

COMMENT_HEADER = (
    "## 🛡️ FableBreaker AutoAgent Report\n\n"
    "> *Automated adversarial code review — correctness before speed.*\n\n"
)


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def get_changed_files() -> list[str]:
    """Get list of changed files in the PR using git diff."""
    try:
        base_ref = os.environ.get("GITHUB_BASE_REF", "main")
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
            capture_output=True, text=True, check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        # Fallback: diff against HEAD~1
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"],
                capture_output=True, text=True, check=True,
            )
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except subprocess.CalledProcessError:
            return []


def filter_files(files: list[str], pattern: str) -> list[str]:
    """Filter file list by glob pattern."""
    from fnmatch import fnmatch
    return [f for f in files if fnmatch(f, pattern) or fnmatch(Path(f).name, pattern)]


def severity_meets_threshold(severity: str, threshold: str) -> bool:
    """Check if a severity level meets the configured threshold."""
    return SEVERITY_LEVELS.get(severity.lower(), 0) >= SEVERITY_LEVELS.get(threshold.lower(), 0)


def scan_files(files: list[str], max_issues_per_file: int) -> dict[str, Any]:
    """Run FableBreaker scan on the given files."""
    scanner = CodeScanner()
    results: dict[str, Any] = {
        "files_scanned": 0,
        "total_issues": 0,
        "critical_issues": 0,
        "high_issues": 0,
        "medium_issues": 0,
        "low_issues": 0,
        "security_score": 0.0,
        "file_results": {},
        "verdict": "PASS",
    }

    for filepath in files:
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            continue

        try:
            scan_result = scanner.scan_file(str(path))
        except Exception as exc:
            results["file_results"][filepath] = {"error": str(exc)}
            continue

        results["files_scanned"] += 1

        # Extract issues from scan result
        file_issues = extract_issues(scan_result, max_issues_per_file)
        results["file_results"][filepath] = {
            "issues": file_issues,
            "summary": scan_result.get("summary", {}),
        }

        for issue in file_issues:
            sev = issue.get("severity", "low").lower()
            results["total_issues"] += 1
            if sev == "critical":
                results["critical_issues"] += 1
            elif sev == "high":
                results["high_issues"] += 1
            elif sev == "medium":
                results["medium_issues"] += 1
            else:
                results["low_issues"] += 1

    # Calculate aggregate security score
    if results["files_scanned"] > 0:
        total_weighted = (
            results["critical_issues"] * 10
            + results["high_issues"] * 7
            + results["medium_issues"] * 4
            + results["low_issues"] * 1
        )
        results["security_score"] = min(10.0, total_weighted / max(results["files_scanned"], 1))

    # Determine verdict
    if results["critical_issues"] > 0:
        results["verdict"] = "FAIL"
    elif results["high_issues"] > 0:
        results["verdict"] = "WARN"
    else:
        results["verdict"] = "PASS"

    return results


def extract_issues(scan_result: dict[str, Any], max_issues: int) -> list[dict[str, Any]]:
    """Extract structured issues from a scan result."""
    issues: list[dict[str, Any]] = []

    # From code_review skill
    code_review = scan_result.get("code_review", {})
    if code_review:
        output = code_review.get("output", {})
        for finding in output.get("findings", [])[:max_issues]:
            issues.append({
                "category": finding.get("category", "code_review"),
                "severity": finding.get("severity", "low"),
                "description": finding.get("description", ""),
                "line": finding.get("line"),
                "source": "code_review",
            })

    # From security skill
    security = scan_result.get("security", {})
    if security:
        output = security.get("output", {})
        for vuln in output.get("vulnerabilities", [])[:max_issues]:
            issues.append({
                "category": vuln.get("type", "security"),
                "severity": vuln.get("severity", "medium"),
                "description": vuln.get("description", ""),
                "line": vuln.get("line"),
                "source": "security",
            })

    # From refactoring skill
    refactoring = scan_result.get("refactoring", {})
    if refactoring:
        output = refactoring.get("output", {})
        for opportunity in output.get("opportunities", [])[:max_issues]:
            issues.append({
                "category": "refactoring",
                "severity": opportunity.get("impact", "low"),
                "description": opportunity.get("description", ""),
                "line": opportunity.get("line"),
                "source": "refactoring",
            })

    return issues[:max_issues]


def format_comment(results: dict[str, Any], severity_threshold: str) -> str:
    """Format scan results as a GitHub PR comment."""
    lines = [COMMENT_HEADER]

    # Verdict badge
    verdict = results["verdict"]
    if verdict == "PASS":
        lines.append("**Verdict:** ✅ PASS — No critical issues detected\n\n")
    elif verdict == "WARN":
        lines.append("**Verdict:** ⚠️ WARN — High-severity issues found\n\n")
    else:
        lines.append("**Verdict:** ❌ FAIL — Critical issues require attention\n\n")

    # Summary table
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Files Scanned | {results['files_scanned']} |")
    lines.append(f"| Total Issues | {results['total_issues']} |")
    lines.append(f"| Critical | {results['critical_issues']} |")
    lines.append(f"| High | {results['high_issues']} |")
    lines.append(f"| Medium | {results['medium_issues']} |")
    lines.append(f"| Low | {results['low_issues']} |")
    lines.append(f"| Security Score | {results['security_score']:.1f} / 10 |")
    lines.append("")

    # Per-file findings
    has_findings = False
    for filepath, file_data in results.get("file_results", {}).items():
        if "error" in file_data:
            continue
        issues = file_data.get("issues", [])
        filtered = [i for i in issues if severity_meets_threshold(i.get("severity", "low"), severity_threshold)]
        if not filtered:
            continue

        if not has_findings:
            lines.append("\n### Findings\n")
            has_findings = True

        lines.append(f"\n<details><summary><code>{filepath}</code> — {len(filtered)} issue(s)</summary>\n")
        lines.append("| Severity | Category | Finding |")
        lines.append("|----------|----------|---------|")
        for issue in filtered:
            sev = issue.get("severity", "low").capitalize()
            cat = issue.get("category", "—")
            desc = issue.get("description", "—")
            line_ref = f" (L{issue['line']})" if issue.get("line") else ""
            lines.append(f"| {sev} | {cat} | {desc}{line_ref} |")
        lines.append("\n</details>")

    if not has_findings:
        lines.append("\n✨ No issues above the configured threshold.\n")

    lines.append("\n---\n")
    lines.append("*Powered by [FableBreaker SDK](https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK) — "
                 "proof before speed.*")

    return "\n".join(lines)


def post_comment(comment_body: str) -> None:
    """Post a comment on the PR using GitHub API."""
    token = get_env("GITHUB_TOKEN")
    repo = get_env("GITHUB_REPOSITORY")
    pr_number = get_env("GITHUB_PR_NUMBER")

    if not all([token, repo, pr_number]):
        print("⚠️  Missing GitHub context — printing report to stdout instead.")
        print(comment_body)
        return

    import urllib.request
    import urllib.error

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    data = json.dumps({"body": comment_body}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status in (200, 201):
                print(f"✅ Posted FableBreaker report to PR #{pr_number}")
            else:
                print(f"⚠️  Unexpected status {response.status}")
    except urllib.error.HTTPError as exc:
        print(f"❌ Failed to post comment: {exc.code} {exc.reason}")
        print(comment_body)


def set_output(name: str, value: str) -> None:
    """Set a GitHub Actions output."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")


def main() -> None:
    """Main entry point for the FableBreaker AutoAgent."""
    print("🛡️  FableBreaker AutoAgent starting...")

    # Read configuration from environment
    scan_pattern = get_env("INPUT_SCAN_PATTERN", "*.py")
    severity_threshold = get_env("INPUT_SEVERITY_THRESHOLD", "low")
    scan_mode = get_env("INPUT_SCAN_MODE", "changed-files")
    target_directory = get_env("INPUT_TARGET_DIRECTORY", ".")
    fail_on_critical = get_env("INPUT_FAIL_ON_CRITICAL", "true").lower() == "true"
    max_issues_per_file = int(get_env("INPUT_MAX_ISSUES_PER_FILE", "10"))

    # Determine which files to scan
    if scan_mode == "changed-files":
        all_files = get_changed_files()
        files = filter_files(all_files, scan_pattern)
        print(f"📂 Found {len(files)} changed files matching '{scan_pattern}'")
    elif scan_mode == "full-repo":
        files = [str(p) for p in Path(".").rglob(scan_pattern) if p.is_file()]
        print(f"📂 Found {len(files)} files in repo matching '{scan_pattern}'")
    elif scan_mode == "directory":
        files = [str(p) for p in Path(target_directory).rglob(scan_pattern) if p.is_file()]
        print(f"📂 Found {len(files)} files in '{target_directory}' matching '{scan_pattern}'")
    else:
        print(f"❌ Unknown scan-mode: {scan_mode}")
        sys.exit(1)

    if not files:
        print("ℹ️  No files to scan. Exiting cleanly.")
        set_output("total-issues", "0")
        set_output("critical-issues", "0")
        set_output("security-score", "0")
        set_output("verdict", "PASS")
        return

    # Run the scan
    print(f"🔍 Scanning {len(files)} file(s)...")
    results = scan_files(files, max_issues_per_file)

    # Write full report
    report_path = Path("/tmp/fablebreaker-report.json")
    report_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"📝 Full report written to {report_path}")

    # Set outputs
    set_output("total-issues", str(results["total_issues"]))
    set_output("critical-issues", str(results["critical_issues"]))
    set_output("security-score", f"{results['security_score']:.1f}")
    set_output("verdict", results["verdict"])
    set_output("report-path", str(report_path))

    # Post comment
    comment_mode = get_env("INPUT_COMMENT_MODE", "pr-comment")
    if comment_mode in ("pr-comment", "both"):
        comment = format_comment(results, severity_threshold)
        post_comment(comment)

    # Print summary
    print(f"\n{'='*50}")
    print(f"🛡️  FableBreaker AutoAgent Results")
    print(f"{'='*50}")
    print(f"  Files scanned: {results['files_scanned']}")
    print(f"  Total issues:  {results['total_issues']}")
    print(f"  Critical:      {results['critical_issues']}")
    print(f"  Verdict:       {results['verdict']}")
    print(f"{'='*50}\n")

    # Fail if critical issues found and configured to do so
    if fail_on_critical and results["critical_issues"] > 0:
        print("❌ Failing check due to critical issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
