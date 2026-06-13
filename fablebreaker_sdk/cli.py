"""
FableBreaker SDK CLI — command-line interface.

Usage:
    fablebreaker scan <file_or_directory>
    fablebreaker review <file>
    fablebreaker security <file>
    fablebreaker dogfood
    fablebreaker info
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    """FableBreaker SDK CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="fablebreaker",
        description="FableBreaker AI SDK — adversarial evaluation toolkit",
    )
    subparsers = parser.add_subparsers(dest="command")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Full scan of file or directory")
    scan_parser.add_argument("target", help="File or directory to scan")
    scan_parser.add_argument("--format", choices=["json", "markdown", "summary"], default="markdown")

    # review command
    review_parser = subparsers.add_parser("review", help="Code review a file")
    review_parser.add_argument("file", help="File to review")
    review_parser.add_argument("--focus", nargs="*", default=None)

    # security command
    sec_parser = subparsers.add_parser("security", help="Security scan a file")
    sec_parser.add_argument("file", help="File to scan")

    # dogfood command
    subparsers.add_parser("dogfood", help="Run FableBreaker on its own code")

    # info command
    subparsers.add_parser("info", help="Show SDK info and available skills")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "info":
        _cmd_info()
    elif args.command == "scan":
        _cmd_scan(args)
    elif args.command == "review":
        _cmd_review(args)
    elif args.command == "security":
        _cmd_security(args)
    elif args.command == "dogfood":
        _cmd_dogfood()


def _cmd_info() -> None:
    """Show SDK info."""
    from . import FableBreaker
    fb = FableBreaker()
    print("FableBreaker AI SDK v1.0.0")
    print("=" * 40)
    print(f"Total Skills: {fb.skill_count}")
    print(f"Available Skills: {', '.join(fb.skills)}")
    print()
    print("Usage:")
    print("  fablebreaker scan <file_or_dir>  — full scan")
    print("  fablebreaker review <file>       — code review")
    print("  fablebreaker security <file>     — security scan")
    print("  fablebreaker dogfood             — self-analysis")


def _cmd_scan(args: argparse.Namespace) -> None:
    """Run full scan."""
    from .scanner import CodeScanner
    from .reporter import ReportGenerator

    scanner = CodeScanner()
    target = Path(args.target)

    if target.is_file():
        results = scanner.scan_file(target)
    elif target.is_dir():
        results = scanner.scan_directory(target)
    else:
        print(f"Error: {args.target} not found")
        sys.exit(1)

    if args.format == "json":
        print(ReportGenerator.to_json(results))
    elif args.format == "markdown":
        print(ReportGenerator.to_markdown(results))
    else:
        print(ReportGenerator.to_summary(results))


def _cmd_review(args: argparse.Namespace) -> None:
    """Run code review."""
    from . import FableBreaker
    from .reporter import ReportGenerator

    path = Path(args.file)
    if not path.exists():
        print(f"Error: {args.file} not found")
        sys.exit(1)

    fb = FableBreaker()
    code = path.read_text(encoding="utf-8")
    result = fb.review_code(code, focus=args.focus)
    print(ReportGenerator.to_json(result))


def _cmd_security(args: argparse.Namespace) -> None:
    """Run security scan."""
    from . import FableBreaker
    from .reporter import ReportGenerator

    path = Path(args.file)
    if not path.exists():
        print(f"Error: {args.file} not found")
        sys.exit(1)

    fb = FableBreaker()
    code = path.read_text(encoding="utf-8")
    result = fb.scan_security(code)
    print(ReportGenerator.to_json(result))


def _cmd_dogfood() -> None:
    """Run FableBreaker on its own code."""
    from .scanner import CodeScanner
    from .reporter import ReportGenerator

    print("🔄 Running FableBreaker on its own codebase (dogfooding)...")
    print()

    scanner = CodeScanner()
    results = scanner.scan_own_codebase()

    print(ReportGenerator.to_markdown(results, title="FableBreaker Self-Analysis Report"))


if __name__ == "__main__":
    main()
