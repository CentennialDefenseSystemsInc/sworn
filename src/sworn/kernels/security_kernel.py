"""Security kernel — block commits touching security surfaces."""
from __future__ import annotations

import re

from sworn.kernels.sdk import KernelInput, KernelResult

DEFAULT_PATTERNS = [
    re.compile(r"(^|/)(crypto|auth|gates|licensing|keys)/", re.IGNORECASE),
    re.compile(r"(^|/)secrets?/", re.IGNORECASE),
    re.compile(r"\.env$", re.IGNORECASE),
    re.compile(r"(^|/)private/", re.IGNORECASE),
]


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """Evaluate files against security surface patterns."""
    patterns = DEFAULT_PATTERNS

    # Use config patterns if provided
    config_patterns = kernel_input.config.get("security_patterns")
    if config_patterns and isinstance(config_patterns, list):
        patterns = config_patterns

    blocked_files: list[str] = []
    for f in kernel_input.files:
        for pattern in patterns:
            if pattern.search(f):
                blocked_files.append(f)
                break

    if blocked_files:
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=["security_surface"],
            evidence_summary=[
                f"Blocked {len(blocked_files)} file(s) on security surface",
                *[f"  {f}" for f in blocked_files[:5]],
            ],
            required_next_action="Remove security-surface files or adjust config",
        )

    return KernelResult(
        decision="PASS",
        triggered_rules=[],
        evidence_summary=[f"All {len(kernel_input.files)} file(s) clear"],
    )
