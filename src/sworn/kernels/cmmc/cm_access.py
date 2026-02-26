"""CM.L2-3.4.5 — Access restrictions: allowlist or security patterns active."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when no access restrictions are active."""
    evidence: list[str] = []
    rules: list[str] = ["CM.L2-3.4.5"]
    config = kernel_input.config

    security_patterns = config.get("security_patterns", [])
    allowlist = config.get("allowlist", [])

    if not security_patterns and not allowlist:
        evidence.append("No access restrictions configured")
        evidence.append("Neither security patterns nor allowlist is active")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Configure security patterns or allowlist in .sworn/config.toml",
        )

    evidence.append("Access restrictions active")
    if security_patterns:
        evidence.append(f"Security patterns: {len(security_patterns)}")
    if allowlist:
        evidence.append(f"Allowlist patterns: {len(allowlist)}")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
