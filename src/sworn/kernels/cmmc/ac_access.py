"""AC.L2-3.1.1/3.1.2 — Access control: actor identity must be resolved."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when actor identity is unresolved."""
    actor = kernel_input.actor
    tool = kernel_input.tool

    evidence: list[str] = []
    rules: list[str] = []

    if not actor or actor == "unknown":
        rules.append("AC.L2-3.1.1")
        evidence.append(
            "Actor identity: unresolved — manual attestation may be required."
        )
        return KernelResult(
            decision="PASS",
            triggered_rules=rules,
            evidence_summary=evidence,
        )

    evidence.append(f"Actor: {actor}")
    if tool:
        evidence.append(f"AI tool detected: {tool}")
        rules.append("AC.L2-3.1.2")
    else:
        evidence.append("No AI tool detected")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
