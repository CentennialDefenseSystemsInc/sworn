"""AU.L2-3.3.1 — Audit records: evidence hash chain must be enabled."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when hash chain is disabled."""
    config = kernel_input.config
    hash_chain = config.get("evidence_hash_chain", True)
    log_path = config.get("evidence_log_path", ".sworn/evidence.jsonl")

    evidence: list[str] = []
    rules: list[str] = ["AU.L2-3.3.1"]

    if not hash_chain:
        evidence.append("Evidence hash chain is disabled")
        evidence.append("Audit records cannot guarantee integrity without hash chain")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Enable evidence.hash_chain in .sworn/config.toml",
        )

    evidence.append("Evidence hash chain enabled")
    evidence.append(f"Log path: {log_path}")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
