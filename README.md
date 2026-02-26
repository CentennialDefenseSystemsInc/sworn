# Sworn

**Deterministic, fail-closed AI code governance. Every commit is sworn.**

Sworn is a Python CLI that installs git pre-commit hooks, runs a configurable
gate pipeline on every commit, and produces tamper-evident evidence logs.

Cross-tool enforcement for any AI coding tool that commits through git.

## Install

```bash
pip install sworncode
```

## Quick Start

```bash
# Initialize in any git repo
cd your-repo
sworn init

# That's it. Every commit is now gated.
# Try committing a file in a sensitive path:
mkdir -p crypto
echo "secret = 'key'" > crypto/vault.py
git add crypto/vault.py
git commit -m "test"
# → SWORN BLOCKED — Security surface: crypto/vault.py
```

## What It Does

Sworn runs a 5-stage gate pipeline on every `git commit`:

1. **Identity** — Detects the actor and AI tool from environment
2. **Security** — Blocks commits touching sensitive paths (configurable)
3. **Allowlist** — Enforces file access control (opt-in)
4. **Kernels** — Runs constraint kernels (built-in + custom)
5. **Evidence** — Logs everything to `.sworn/evidence.jsonl`

Every stage is deterministic. No AI in the governance loop. No network calls.
No probabilistic analysis. A gate either passes or blocks.

## Commands

```bash
sworn init              # Initialize sworn in a git repo
sworn check             # Run gate pipeline (called by pre-commit hook)
sworn report            # Show evidence summary
sworn report --json     # Machine-readable output
sworn status            # Show initialization and config state
sworn verify            # Verify evidence chain integrity
sworn --version         # Print version
```

## Configuration

After `sworn init`, edit `.sworn/config.toml`:

```toml
[security]
# Regex patterns for sensitive paths (case-insensitive)
patterns = [
    '(^|/)(crypto|auth|gates|licensing|keys)/',
    '(^|/)secrets?/',
    '\.env$',
]

[allowlist]
# Only these glob patterns allowed (empty = all allowed)
files = []

[kernels]
# Built-in kernels
security = true
allowlist = true
audit = true

# Custom kernels
custom_dir = ".sworn/kernels"
```

## Custom Kernels

Write a Python file in `.sworn/kernels/` with an `evaluate()` function:

```python
from sworn.kernels.sdk import KernelInput, KernelResult

def evaluate(kernel_input: KernelInput) -> KernelResult:
    # Your logic here
    if some_condition:
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=["my_rule"],
            evidence_summary=["Blocked because..."],
        )
    return KernelResult(decision="PASS")
```

## Evidence

Every gate run produces a JSONL entry with SHA256 hash chain:

```bash
sworn report
# SWORN EVIDENCE REPORT
# ========================================
# Total commits gated: 47
#   Passed: 43
#   Blocked: 4
#   Pass rate: 91.5%
# Chain integrity: VALID

sworn verify
# Chain: VALID
#   Chain valid: 47 entries
```

## Requirements

- Python 3.10+
- Git
- Zero runtime dependencies (tomli included in stdlib from 3.11)

## License

Apache 2.0 — Centennial Defense Systems
