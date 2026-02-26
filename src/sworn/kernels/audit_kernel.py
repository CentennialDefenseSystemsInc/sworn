"""Audit kernel — record commit metadata. Never blocks."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """Record audit trail data. This kernel always passes."""
    summary = [
        f"Actor: {kernel_input.actor}",
        f"Tool: {kernel_input.tool or 'none detected'}",
        f"Files: {len(kernel_input.files)}",
    ]

    if kernel_input.files:
        summary.append(f"First: {kernel_input.files[0]}")
        if len(kernel_input.files) > 1:
            summary.append(f"Last: {kernel_input.files[-1]}")

    return KernelResult(
        decision="PASS",
        triggered_rules=[],
        evidence_summary=summary[:5],
    )
