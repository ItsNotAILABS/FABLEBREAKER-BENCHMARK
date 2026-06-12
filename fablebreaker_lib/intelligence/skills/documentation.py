"""
Documentation Skill — analyzes and generates documentation.
"""

from __future__ import annotations

import re
from typing import Any

from .base import Skill, SkillLevel, SkillResult


class DocumentationSkill(Skill):
    """
    Analyzes documentation quality and completeness, identifies gaps,
    and produces structured documentation artifacts.
    """

    def __init__(self) -> None:
        super().__init__(
            name="documentation",
            description="Analyzes documentation quality and completeness. "
                        "Identifies gaps and produces documentation artifacts.",
            level=SkillLevel.PROFICIENT,
        )

    def invoke(self, context: dict[str, Any]) -> SkillResult:
        """
        Perform documentation analysis or generation.

        Context should contain:
        - doc_action: "analyze", "audit", "generate_api", "generate_readme"
        - code: source code to analyze
        - existing_docs: existing documentation content
        - module_name: name of the module
        """
        action = context.get("doc_action", "analyze")
        code = context.get("code", "")

        if action == "analyze":
            return self._analyze_docs(code, context)
        if action == "audit":
            return self._audit_docs(context)
        if action == "generate_api":
            return self._generate_api_docs(code, context)
        if action == "generate_readme":
            return self._generate_readme(context)
        return SkillResult(
            skill_name=self.name,
            success=False,
            reasoning=f"Unknown documentation action: {action}",
        )

    def _analyze_docs(self, code: str, context: dict[str, Any]) -> SkillResult:  # pylint: disable=unused-argument
        """Analyze documentation quality in code."""
        metrics = {
            "total_functions": 0,
            "documented_functions": 0,
            "total_classes": 0,
            "documented_classes": 0,
            "total_modules": 0,
            "documented_modules": 0,
            "issues": [],
        }

        # Module docstring
        metrics["total_modules"] = 1
        if code.lstrip().startswith('"""') or code.lstrip().startswith("'''"):
            metrics["documented_modules"] = 1
        else:
            metrics["issues"].append({
                "type": "missing_module_docstring",
                "severity": "medium",
            })

        # Class docstrings
        classes = re.finditer(r"class\s+(\w+)[^:]*:", code)
        for match in classes:
            metrics["total_classes"] += 1
            cls_name = match.group(1)
            # Check if followed by docstring
            after = code[match.end():]
            if re.match(r"\s*\n\s*\"\"\"", after) or re.match(r"\s*\n\s*'''", after):
                metrics["documented_classes"] += 1
            else:
                metrics["issues"].append({
                    "type": "missing_class_docstring",
                    "class": cls_name,
                    "severity": "medium",
                })

        # Function docstrings
        funcs = re.finditer(r"def\s+(\w+)\s*\([^)]*\)[^:]*:", code)
        for match in funcs:
            func_name = match.group(1)
            if func_name.startswith("_") and func_name != "__init__":
                continue
            metrics["total_functions"] += 1
            after = code[match.end():]
            if re.match(r"\s*\n\s*\"\"\"", after) or re.match(r"\s*\n\s*'''", after):
                metrics["documented_functions"] += 1
            else:
                metrics["issues"].append({
                    "type": "missing_function_docstring",
                    "function": func_name,
                    "severity": "low",
                })

        total = (metrics["total_functions"] + metrics["total_classes"] +
                 metrics["total_modules"])
        documented = (metrics["documented_functions"] + metrics["documented_classes"] +
                      metrics["documented_modules"])
        score = (documented / total * 100) if total else 0.0

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "documentation_score": round(score, 1),
                "metrics": metrics,
                "quality_grade": (
                    "A" if score >= 90 else "B" if score >= 75
                    else "C" if score >= 60 else "D" if score >= 40 else "F"
                ),
            },
            confidence=0.85,
            reasoning=f"Documentation score: {score:.1f}% (grade: {'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D'})",
        )

    def _audit_docs(self, context: dict[str, Any]) -> SkillResult:
        """Audit documentation completeness across a project."""
        files = context.get("files", [])
        existing_docs = context.get("existing_docs", {})

        audit = {
            "files_checked": len(files),
            "has_readme": "README.md" in existing_docs or "README" in existing_docs,
            "has_api_docs": any("api" in k.lower() for k in existing_docs),
            "has_changelog": any("change" in k.lower() for k in existing_docs),
            "has_contributing": any("contrib" in k.lower() for k in existing_docs),
            "has_license": any("license" in k.lower() for k in existing_docs),
            "missing": [],
        }

        if not audit["has_readme"]:
            audit["missing"].append({"doc": "README.md", "priority": "critical"})
        if not audit["has_api_docs"]:
            audit["missing"].append({"doc": "API documentation", "priority": "high"})
        if not audit["has_changelog"]:
            audit["missing"].append({"doc": "CHANGELOG", "priority": "medium"})
        if not audit["has_contributing"]:
            audit["missing"].append({"doc": "CONTRIBUTING.md", "priority": "low"})

        completeness = sum([
            audit["has_readme"],
            audit["has_api_docs"],
            audit["has_changelog"],
            audit["has_contributing"],
            audit["has_license"],
        ]) / 5.0 * 100

        audit["completeness_percentage"] = completeness

        return SkillResult(
            skill_name=self.name,
            success=True,
            output=audit,
            confidence=0.9,
            reasoning=f"Documentation audit: {completeness:.0f}% complete, {len(audit['missing'])} items missing",
        )

    def _generate_api_docs(self, code: str, context: dict[str, Any]) -> SkillResult:
        """Generate API documentation from code."""
        module_name = context.get("module_name", "module")
        api_items = []

        # Extract classes
        for match in re.finditer(r"class\s+(\w+)([^:]*?):\s*\n\s*\"\"\"(.*?)\"\"\"", code, re.DOTALL):
            cls_name = match.group(1)
            docstring = match.group(3).strip()
            api_items.append({
                "type": "class",
                "name": cls_name,
                "description": docstring.split("\n")[0],
                "full_doc": docstring,
            })

        # Extract public functions
        for match in re.finditer(
            r"def\s+([a-z]\w+)\s*\(([^)]*)\)[^:]*:\s*\n\s*\"\"\"(.*?)\"\"\"",
            code, re.DOTALL
        ):
            func_name = match.group(1)
            params = match.group(2)
            docstring = match.group(3).strip()
            api_items.append({
                "type": "function",
                "name": func_name,
                "parameters": params,
                "description": docstring.split("\n")[0],
                "full_doc": docstring,
            })

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={
                "module": module_name,
                "api_items": api_items,
                "total_documented_items": len(api_items),
            },
            confidence=0.9,
            reasoning=f"Generated API docs for {len(api_items)} items in {module_name}",
            artifacts=[{"type": "api_documentation", "module": module_name}],
        )

    def _generate_readme(self, context: dict[str, Any]) -> SkillResult:
        """Generate README structure."""
        project_name = context.get("project_name", "Project")
        features = context.get("features", [])
        install_cmd = context.get("install_command", "pip install .")

        sections = [
            {"heading": project_name, "level": 1},
            {"heading": "Overview", "level": 2, "content": context.get("description", "")},
            {"heading": "Installation", "level": 2, "content": f"```\n{install_cmd}\n```"},
            {"heading": "Features", "level": 2, "content": features},
            {"heading": "Quick Start", "level": 2, "content": context.get("quick_start", "")},
            {"heading": "API Reference", "level": 2, "content": "See API documentation."},
            {"heading": "Contributing", "level": 2, "content": "See CONTRIBUTING.md"},
            {"heading": "License", "level": 2, "content": context.get("license", "MIT")},
        ]

        return SkillResult(
            skill_name=self.name,
            success=True,
            output={"sections": sections, "total_sections": len(sections)},
            confidence=0.9,
            reasoning=f"Generated README structure with {len(sections)} sections",
            artifacts=[{"type": "readme_structure", "sections": len(sections)}],
        )
