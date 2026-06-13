# 🛡️ FableBreaker AutoAgent

**Automated adversarial code review for GitHub PRs — like CodeRabbit, but correctness-first.**

FableBreaker AutoAgent runs on every pull request, scans changed files with the FableBreaker SDK, and posts a structured review report as a PR comment. Anyone can install it on their repos.

---

## Quick Start (Add to Any Repo)

Create `.github/workflows/fablebreaker.yml` in your repository:

```yaml
name: FableBreaker AutoAgent
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    uses: ItsNotAILABS/FABLEBREAKER-BENCHMARK/.github/workflows/fablebreaker-autoagent.yml@main
    with:
      scan-pattern: "*.py"
      severity-threshold: "medium"
```

That's it. Every PR will now get automated FableBreaker analysis.

---

## What It Does

On every PR, FableBreaker AutoAgent:

1. **Detects changed files** matching your configured pattern
2. **Runs full analysis** using the FableBreaker SDK (code review, security, refactoring, documentation)
3. **Posts a structured report** as a PR comment with:
   - Overall verdict (PASS / WARN / FAIL)
   - Issue counts by severity
   - Security risk score
   - Per-file findings in collapsible sections
4. **Optionally fails the check** if critical issues are detected

---

## Example Output

```
## 🛡️ FableBreaker AutoAgent Report

> Automated adversarial code review — correctness before speed.

**Verdict:** ⚠️ WARN — High-severity issues found

| Metric | Value |
|--------|-------|
| Files Scanned | 4 |
| Total Issues | 7 |
| Critical | 0 |
| High | 2 |
| Medium | 3 |
| Low | 2 |
| Security Score | 3.2 / 10 |
```

---

## Configuration Options

| Input | Default | Description |
|-------|---------|-------------|
| `scan-pattern` | `*.py` | Glob pattern for files to analyze |
| `severity-threshold` | `low` | Minimum severity to report: `low`, `medium`, `high`, `critical` |
| `scan-mode` | `changed-files` | What to scan: `changed-files`, `full-repo`, `directory` |
| `target-directory` | `.` | Directory to scan (when `scan-mode` is `directory`) |
| `fail-on-critical` | `true` | Fail the CI check if critical issues are found |
| `max-issues-per-file` | `10` | Maximum issues to report per file |

---

## Outputs

| Output | Description |
|--------|-------------|
| `total-issues` | Total number of issues found |
| `critical-issues` | Number of critical issues found |
| `security-score` | Security risk score (0-10) |
| `verdict` | Overall verdict: `PASS`, `WARN`, `FAIL` |
| `report-path` | Path to the full JSON report |

---

## Scan Modes

### `changed-files` (default)
Only scans files modified in the PR. Fast, focused, and ideal for PR reviews.

### `full-repo`
Scans the entire repository. Use for scheduled audits or initial setup.

### `directory`
Scans a specific directory. Use with `target-directory` for monorepos.

---

## Using as a Composite Action

You can also use FableBreaker AutoAgent as a direct action step:

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0

  - uses: ItsNotAILABS/FABLEBREAKER-BENCHMARK/fablebreaker-autoagent@main
    with:
      github-token: ${{ secrets.GITHUB_TOKEN }}
      scan-pattern: "*.py"
      severity-threshold: "medium"
      fail-on-critical: "true"
```

---

## Running Locally

You can also run the agent locally to preview what it would report:

```bash
# From the FABLEBREAKER-BENCHMARK repo root
python fablebreaker-autoagent/agent.py

# Or with custom settings
INPUT_SCAN_MODE=full-repo INPUT_SCAN_PATTERN="*.py" python fablebreaker-autoagent/agent.py
```

---

## How It Compares

| Feature | FableBreaker AutoAgent | CodeRabbit | GitHub CodeQL |
|---------|----------------------|------------|---------------|
| **Focus** | Correctness + adversarial analysis | General code review | Security vulnerabilities |
| **Self-hostable** | ✅ Yes | ❌ No | ✅ Yes |
| **Open source** | ✅ Fully | ❌ No | Partially |
| **PR comments** | ✅ | ✅ | ❌ (annotations) |
| **Security scanning** | ✅ | Limited | ✅ |
| **Refactoring suggestions** | ✅ | ✅ | ❌ |
| **Custom rules** | ✅ (SDK skills) | Limited | ✅ (QL queries) |
| **Free** | ✅ Always | Freemium | ✅ for public repos |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              FableBreaker AutoAgent               │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐  │
│  │  Trigger  │──▶│  Scanner  │──▶│  Reporter   │  │
│  │ (PR event)│   │ (SDK)    │   │ (comment)  │  │
│  └──────────┘   └──────────┘   └────────────┘  │
│        │                               │         │
│        ▼                               ▼         │
│  ┌──────────┐                   ┌────────────┐  │
│  │  Git Diff │                   │  PR Comment │  │
│  │  (files)  │                   │  (GitHub)   │  │
│  └──────────┘                   └────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Skills Used

FableBreaker AutoAgent invokes these SDK skills per file:

| Skill | Purpose |
|-------|---------|
| `code_review` | Bug detection, logic errors, missed edge cases |
| `security` | Vulnerability scanning, injection risks, auth issues |
| `refactoring` | Structural improvement opportunities |
| `documentation` | Missing docstrings and coverage gaps |
| `self_analysis` | Meta-evaluation and blind spot detection |

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on improving the AutoAgent.

---

<p align="center">
  <strong>ItsNotAI LABS</strong><br>
  <em>Proof before speed. Correctness before claims. Reproducibility before trust.</em>
</p>
