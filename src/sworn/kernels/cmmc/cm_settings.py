"""CM.L2-3.4.2 — Configuration settings: security gate + kernels + evidence enabled."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when security configuration is disabled."""
    evidence: list[str] = []
    rules: list[str] = ["CM.L2-3.4.2"]
    config = kernel_input.config

    security_patterns = config.get("security_patterns", [])
    kernels_enabled = config.get("kernels_enabled", {})
    hash_chain = config.get("evidence_hash_chain", True)

    issues: list[str] = []

    if not security_patterns:
        issues.append("security gate disabled (no patterns)")
    if not kernels_enabled.get("security", True):
        issues.append("security kernel disabled")
    if not hash_chain:
        issues.append("evidence hash chain disabled")

    if issues:
        evidence.append("Security configuration incomplete")
        for issue in issues[:3]:
            evidence.append(issue)
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Enable all security settings in .sworn/config.toml",
        )

    evidence.append("All security settings enabled")
    evidence.append(f"Security patterns: {len(security_patterns)}")
    active = [k for k, v in kernels_enabled.items() if v]
    evidence.append(f"Active kernels: {', '.join(active)}")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
