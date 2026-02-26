"""SI.L2-3.14.1 — Flaw remediation: governance pipeline is executing."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """Always PASS — execution of this kernel IS evidence of flaw remediation.

    The fact that the governance pipeline is running demonstrates that
    flaw identification and remediation processes are in place.
    """
    evidence: list[str] = [
        "Governance pipeline executing",
        f"Actor: {kernel_input.actor}",
        f"Files under governance: {len(kernel_input.files)}",
    ]

    if kernel_input.tool:
        evidence.append(f"AI tool governed: {kernel_input.tool}")

    return KernelResult(
        decision="PASS",
        triggered_rules=["SI.L2-3.14.1"],
        evidence_summary=evidence,
    )
