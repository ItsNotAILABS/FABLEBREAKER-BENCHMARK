"""Repo Scanner: discover and load evaluate() candidates from local and external sources.

Supports:
- Discovering candidates in a local package directory (e.g., candidates/)
- Scanning external repos/directories for Python files exposing evaluate(expr: dict)
- Dynamically loading external candidates as importable modules
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def discover_candidates(package_dir: Path) -> list[str]:
    """Find all Python modules in a directory that expose an evaluate() function.

    Args:
        package_dir: Path to the package directory (e.g., ROOT / 'candidates')

    Returns:
        List of importable module paths (e.g., ['candidates.baseline_candidate', ...])
    """
    candidates: list[str] = []
    if not package_dir.is_dir():
        return candidates

    package_name = package_dir.name

    for py_file in sorted(package_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        module_name = py_file.stem
        module_path = f"{package_name}.{module_name}"

        # Verify it has evaluate()
        try:
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "evaluate") and callable(module.evaluate):
                    candidates.append(module_path)
        except Exception:  # noqa: BLE001 - discovery must not crash on bad candidates
            # Skip files that fail to import
            continue

    return candidates


def scan_external_dirs(directories: list[str]) -> list[str]:
    """Scan external directories/repos for files with evaluate() functions.

    For each directory:
    1. Looks recursively for .py files containing 'def evaluate'
    2. Validates they expose evaluate(expr: dict) -> object
    3. Registers them as dynamically importable modules

    Args:
        directories: List of directory paths to scan

    Returns:
        List of importable module names (registered dynamically)
    """
    candidates: list[str] = []

    for dir_path_str in directories:
        dir_path = Path(dir_path_str).resolve()
        if not dir_path.is_dir():
            print(f"  WARNING: {dir_path} is not a directory, skipping")
            continue

        # Add to sys.path so candidates can import their dependencies
        if str(dir_path) not in sys.path:
            sys.path.insert(0, str(dir_path))
        if str(dir_path.parent) not in sys.path:
            sys.path.insert(0, str(dir_path.parent))

        # Scan for Python files with evaluate()
        for py_file in sorted(dir_path.rglob("*.py")):
            if py_file.name.startswith("_"):
                continue
            # Quick text check before expensive import
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "def evaluate" not in content:
                continue

            # Build a unique module name
            relative = py_file.relative_to(dir_path)
            module_name = f"_ext_{dir_path.name}.{'.'.join(relative.with_suffix('').parts)}"

            try:
                loaded = _load_external_module(module_name, py_file)
                if loaded and hasattr(loaded, "evaluate") and callable(loaded.evaluate):
                    candidates.append(module_name)
            except Exception:  # noqa: BLE001
                continue

    return candidates


def _load_external_module(module_name: str, file_path: Path) -> Any:
    """Dynamically load a Python file as a named module."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def scan_repo_for_agents(repo_path: str | Path, pattern: str = "**/*.py") -> list[dict[str, Any]]:
    """High-level scan: find all agent-like files in a repo.

    Returns metadata about each discovered agent, not just module paths.
    Useful for the batch audit report.
    """
    repo = Path(repo_path).resolve()
    agents: list[dict[str, Any]] = []

    for py_file in sorted(repo.rglob(pattern)):
        if py_file.name.startswith("_") or ".git" in py_file.parts:
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "def evaluate" not in content:
            continue

        agents.append({
            "file": str(py_file.relative_to(repo)),
            "abs_path": str(py_file),
            "size_bytes": py_file.stat().st_size,
            "has_evaluate": True,
            "functions": _extract_function_names(content),
        })

    return agents


def _extract_function_names(content: str) -> list[str]:
    """Quick extraction of top-level function names from source."""
    names = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("def ") and "(" in stripped:
            name = stripped[4:stripped.index("(")].strip()
            names.append(name)
    return names
