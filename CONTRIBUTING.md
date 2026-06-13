# Contributing to FableBreaker

Thank you for your interest in contributing to FableBreaker.

---

## Ways to Contribute

| Type | Description |
|------|-------------|
| **New Candidates** | Implement `def evaluate(expr: dict) -> object` in `fablebreaker/candidates/` |
| **Adversarial Families** | Add new expression families that stress-test evaluator correctness |
| **Scoring Improvements** | Enhance measurement precision or add new metrics |
| **Documentation** | Improve docstrings, guides, or examples |
| **Bug Reports** | File issues with reproduction steps |

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ItsNotAILABS/FABLEBREAKER-BENCHMARK.git
cd FABLEBREAKER-BENCHMARK

# Install the SDK in development mode
pip install -e ./fablebreaker_sdk

# Run the test suite
cd fablebreaker
python -m pytest tests/
```

---

## Pull Request Guidelines

1. **All submissions must pass the full audit pipeline** — run `python tools/run_full_audit.py` before submitting
2. **Maintain hash integrity** — do not modify expected outputs in existing datasets
3. **One concern per PR** — keep changes focused and reviewable
4. **Include tests** for new candidates or families
5. **Follow existing code style** — the project uses pylint for enforcement

---

## Candidate Contract

Any candidate must expose exactly one function:

```python
def evaluate(expr: dict) -> object:
    """Evaluate a FableBreaker AST expression and return the computed value."""
    ...
```

The returned value must be semantically identical to the reference evaluator's output. Verification is performed via SHA-256 hash of the canonical serialization.

---

## Code of Conduct

Be respectful, constructive, and focused on technical merit. FableBreaker values rigor over rhetoric.

---

<p align="center">
  <strong>ItsNotAI LABS</strong><br>
  <em>Proof before speed. Correctness before claims. Reproducibility before trust.</em>
</p>
