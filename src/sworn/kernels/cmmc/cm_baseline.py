"""CM.L2-3.4.1 — Configuration baseline: config must exist."""
from __future__ import annotations

from pathlib import Path

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when no baseline configuration exists."""
    evidence: list[str] = []
    rules: list[str] = ["CM.L2-3.4.1"]

    repo_root = Path(kernel_input.repo_root)
    config_path = repo_root / ".sworn" / "config.toml"
    config = kernel_input.config

    if not config_path.exists():
        evidence.append("No .sworn/config.toml found")
        evidence.append("Cannot establish configuration baseline")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Run 'sworn init' to establish baseline config",
        )

    security_patterns = config.get("security_patterns", [])
    if not security_patterns:
        evidence.append("No security patterns configured")
        evidence.append("Baseline config exists but has no security controls")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Add security patterns to .sworn/config.toml",
        )

    evidence.append("Configuration baseline established")
    evidence.append(f"Security patterns: {len(security_patterns)}")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
