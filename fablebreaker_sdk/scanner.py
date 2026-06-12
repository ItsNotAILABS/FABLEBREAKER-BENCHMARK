"""
FableBreaker Code Scanner — scans files and directories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import FableBreaker


class CodeScanner:
    """
    Scans files and directories using FableBreaker's full skill set.

    Example:
        scanner = CodeScanner()
        report = scanner.scan_file("myapp/views.py")
        report = scanner.scan_directory("src/")
    """

    def __init__(self) -> None:
        self._fb = FableBreaker()

    def scan_file(self, filepath: str | Path, language: str = "python") -> dict[str, Any]:
        """
        Scan a single file with all FableBreaker skills.

        Args:
            filepath: Path to the file to scan.
            language: Programming language.

        Returns:
            Full scan report for the file.
        """
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}", "success": False}

        code = path.read_text(encoding="utf-8")
        return self._fb.full_scan(code, language=language, filename=str(path.name))

    def scan_directory(
        self,
        dirpath: str | Path,
        pattern: str = "*.py",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """
        Scan all matching files in a directory.

        Args:
            dirpath: Directory to scan.
            pattern: Glob pattern for files (default: "*.py").
            recursive: Whether to scan subdirectories.

        Returns:
            Aggregated scan report for all files.
        """
        path = Path(dirpath)
        if not path.exists():
            return {"error": f"Directory not found: {dirpath}", "success": False}

        files = list(path.rglob(pattern)) if recursive else list(path.glob(pattern))

        results = {
            "directory": str(path),
            "files_scanned": 0,
            "total_issues": 0,
            "file_reports": [],
            "aggregate_security": {"total_vulnerabilities": 0, "critical": 0},
            "aggregate_coverage": {"undocumented_items": 0},
        }

        for file in sorted(files):
            if "__pycache__" in str(file) or ".git" in str(file):
                continue

            try:
                code = file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            report = self._fb.full_scan(
                code, language="python", filename=str(file.relative_to(path))
            )
            results["files_scanned"] += 1
            results["file_reports"].append({
                "file": str(file.relative_to(path)),
                "summary": report.get("summary", {}),
            })

            # Aggregate
            sec = report.get("security", {}).get("output", {})
            results["aggregate_security"]["total_vulnerabilities"] += sec.get("total_findings", 0)
            results["aggregate_security"]["critical"] += sec.get("critical_count", 0)

            doc = report.get("documentation", {}).get("output", {})
            metrics = doc.get("metrics", {})
            results["aggregate_coverage"]["undocumented_items"] += len(metrics.get("issues", []))

            results["total_issues"] += report.get("summary", {}).get(
                "total_issues_across_all_skills", 0
            )

        return results

    def scan_own_codebase(self) -> dict[str, Any]:
        """
        Dogfood: scan FableBreaker's own codebase.

        This is the ultimate proof that FableBreaker works — it evaluates itself.

        Returns:
            Self-analysis report of the FableBreaker codebase.
        """
        # Find the fablebreaker_lib directory
        sdk_root = Path(__file__).resolve().parent.parent
        lib_dir = sdk_root / "fablebreaker_lib"

        if not lib_dir.exists():
            return {"error": "fablebreaker_lib not found", "success": False}

        return self.scan_directory(lib_dir, pattern="*.py", recursive=True)
