"""Allowlist kernel — block commits with files outside the allowed set."""
from __future__ import annotations

from fnmatch import fnmatch

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """Evaluate files against allowlist. Empty allowlist = all allowed."""
    allowed = kernel_input.config.get("allowlist", [])
    if not allowed:
        return KernelResult(
            decision="PASS",
            triggered_rules=[],
            evidence_summary=["No allowlist configured — all files allowed"],
        )

    blocked_files: list[str] = []
    for f in kernel_input.files:
        if not any(fnmatch(f, pattern) for pattern in allowed):
            blocked_files.append(f)

    if blocked_files:
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=["allowlist_violation"],
            evidence_summary=[
                f"{len(blocked_files)} file(s) outside allowlist",
                *[f"  {f}" for f in blocked_files[:5]],
            ],
            required_next_action="Add files to allowlist or remove from commit",
        )

    return KernelResult(
        decision="PASS",
        triggered_rules=[],
        evidence_summary=[
            f"All {len(kernel_input.files)} file(s) within allowlist"
        ],
    )
