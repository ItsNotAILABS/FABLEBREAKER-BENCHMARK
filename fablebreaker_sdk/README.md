# FableBreaker AI SDK

**The downloadable adversarial evaluation toolkit for AI systems.**

---

## Installation

```bash
# From the repository
pip install ./fablebreaker_sdk

# Or install in development mode
pip install -e ./fablebreaker_sdk
```

---

## Quick Start

```python
from fablebreaker_sdk import FableBreaker

fb = FableBreaker()

# Review code for issues
result = fb.review_code(open("your_file.py").read())
print(f"Issues found: {result['output']['total_issues']}")

# Full scan with all skills
result = fb.full_scan(open("your_file.py").read(), filename="your_file.py")

# Security scan
result = fb.scan_security(open("your_file.py").read())

# Self-analyze your codebase (dogfood mode)
files = [{"name": "app.py", "content": open("app.py").read()}]
result = fb.self_analyze(files)
```

---

## CLI Usage

```bash
# Full scan
fablebreaker scan src/

# Code review
fablebreaker review myfile.py

# Security scan
fablebreaker security myfile.py

# Run on FableBreaker's own code
fablebreaker dogfood

# Show info
fablebreaker info
```

---

## Available Skills (11)

| Skill | Description |
|-------|-------------|
| **analysis** | Deep analysis of AI systems, claims, and evaluation methodologies |
| **generation** | Generates adversarial test cases and evaluation datasets |
| **detection** | Detects gaming, contamination, manipulation, and fraud |
| **reasoning** | Multi-step reasoning about evidence chains and certification |
| **synthesis** | Combines information into actionable intelligence reports |
| **code_review** | Reviews code for correctness, security, and missed edge cases |
| **coverage** | Identifies gaps in testing, docs, and error handling |
| **security** | Identifies vulnerabilities, attack surfaces, and misconfigs |
| **refactoring** | Finds code smells, duplication, and complexity hotspots |
| **documentation** | Audits documentation quality and completeness |
| **self_analysis** | Dogfood: FableBreaker analyzes its own codebase |

---

## SDK API Reference

### `FableBreaker` (main class)

```python
fb = FableBreaker()

fb.review_code(code, language="python", focus=None)
fb.scan_security(code, scan_type="code")
fb.check_coverage(source_files, test_files=None, coverage_type="test")
fb.suggest_refactoring(code, language="python")
fb.audit_documentation(code, doc_action="analyze")
fb.generate_adversarial(domain="code", count=10, difficulty=5)
fb.detect_gaming(scores=None, evidence=None, detection_type="gaming")
fb.self_analyze(source_files, depth="standard")
fb.full_scan(code, language="python", filename="unknown.py")
fb.summary()
```

### `CodeScanner` (file/directory scanner)

```python
from fablebreaker_sdk import CodeScanner

scanner = CodeScanner()
scanner.scan_file("path/to/file.py")
scanner.scan_directory("src/", pattern="*.py")
scanner.scan_own_codebase()  # dogfood mode
```

### `ReportGenerator` (output formatting)

```python
from fablebreaker_sdk import ReportGenerator

ReportGenerator.to_json(results)
ReportGenerator.to_markdown(results, title="My Report")
ReportGenerator.to_summary(results)
```

---

## Use Case: Don't Miss Stuff

FableBreaker SDK is designed to help you **not miss things**:

1. **Run `full_scan` on every file** before committing — catches security, correctness, and completeness issues
2. **Use `check_coverage`** to find untested functions and undocumented APIs
3. **Use `self_analyze`** to dogfood your own tools
4. **Use `detect_gaming`** to verify your benchmark results are legitimate
5. **Use `generate_adversarial`** to create test cases that stress your edge cases

---

## License

MIT — ItsNotAI LABS
