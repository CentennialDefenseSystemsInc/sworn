"""SC.L2-3.13.1 — Boundary protection: no boundary-crossing patterns in commit."""
from __future__ import annotations

import re

from sworn.kernels.sdk import KernelInput, KernelResult

BOUNDARY_PATTERNS = [
    re.compile(r"\.env$", re.IGNORECASE),
    re.compile(r"(^|/)\.env\.", re.IGNORECASE),
    re.compile(r"webhook", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"(^|/)secrets?\.", re.IGNORECASE),
]


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when boundary-crossing patterns detected in committed files."""
    evidence: list[str] = []
    rules: list[str] = ["SC.L2-3.13.1"]

    violations: list[str] = []
    for f in kernel_input.files:
        for pattern in BOUNDARY_PATTERNS:
            if pattern.search(f):
                violations.append(f)
                break

    if violations:
        evidence.append(f"Boundary pattern detected in {len(violations)} file(s)")
        for v in violations[:3]:
            evidence.append(f"  {v}")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Remove boundary-crossing files from commit",
        )

    evidence.append(f"No boundary patterns in {len(kernel_input.files)} file(s)")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
