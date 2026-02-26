"""AU.L2-3.3.2 — Audit traceability: all required evidence fields present."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput, KernelResult

REQUIRED_FIELDS = ["actor", "tool", "files", "repo_root"]


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when required evidence fields are missing."""
    evidence: list[str] = []
    rules: list[str] = ["AU.L2-3.3.2"]
    missing: list[str] = []

    if not kernel_input.actor:
        missing.append("actor")
    if not kernel_input.files:
        missing.append("files")
    if not kernel_input.repo_root:
        missing.append("repo_root")

    if missing:
        evidence.append(f"Missing required fields: {', '.join(missing)}")
        evidence.append("Cannot produce traceable audit record")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action=f"Provide missing fields: {', '.join(missing)}",
        )

    evidence.append(f"Actor: {kernel_input.actor}")
    evidence.append(f"Tool: {kernel_input.tool or 'none'}")
    evidence.append(f"Files: {len(kernel_input.files)}")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
