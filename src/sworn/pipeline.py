"""Gate pipeline — deterministic, fail-closed commit gating."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sworn.config import SwornConfig
from sworn.evidence.log import EvidenceEntry, _now, append_entry
from sworn.gates.allowlist import evaluate_allowlist
from sworn.gates.identity import evaluate_identity
from sworn.gates.security import evaluate_security
from sworn.kernels.sdk import (
    KernelInput,
    KernelResult,
    load_builtin_kernels,
    load_custom_kernels,
)


@dataclass
class PipelineResult:
    """Result of the full gate pipeline."""

    decision: str  # "PASS" or "BLOCKED"
    reason: str = ""
    gate_results: dict[str, str] = field(default_factory=dict)
    kernel_results: list[dict[str, Any]] = field(default_factory=list)
    actor: str = ""
    tool: str | None = None


def run_pipeline(
    repo_root: Path,
    files: list[str],
    config: SwornConfig,
) -> PipelineResult:
    """Run the full gate pipeline. Deterministic, fail-closed."""
    gate_results: dict[str, str] = {}
    kernel_details: list[dict[str, Any]] = []
    decision = "PASS"
    reason = ""

    # 1. Identity (never blocks)
    identity = evaluate_identity(config.identity_env_vars)
    gate_results["identity"] = "PASS"

    # 2. Security
    security = evaluate_security(files, config.security_patterns)
    gate_results["security"] = "PASS" if security.passed else "BLOCKED"
    if not security.passed:
        decision = "BLOCKED"
        reason = security.reason

    # 3. Allowlist (only if not already blocked and allowlist is configured)
    if decision == "PASS" and config.allowlist:
        allowlist = evaluate_allowlist(files, config.allowlist)
        gate_results["allowlist"] = "PASS" if allowlist.passed else "BLOCKED"
        if not allowlist.passed:
            decision = "BLOCKED"
            reason = allowlist.reason
    else:
        gate_results["allowlist"] = "SKIP" if not config.allowlist else "SKIP"

    # 4. Kernels (only if not already blocked)
    if decision == "PASS":
        kernel_input = KernelInput(
            files=files,
            actor=identity.actor,
            tool=identity.tool,
            repo_root=str(repo_root),
            config={
                "security_patterns": config.security_patterns,
                "allowlist": config.allowlist,
            },
        )

        all_kernels = load_builtin_kernels(config.kernels_enabled)
        custom_dir = repo_root / config.custom_kernel_dir
        all_kernels.extend(load_custom_kernels(custom_dir))

        for name, evaluate_fn in all_kernels:
            try:
                result = evaluate_fn(kernel_input)
            except Exception as exc:
                result = KernelResult(
                    decision="BLOCKED",
                    triggered_rules=["kernel_exception"],
                    evidence_summary=[f"Kernel {name} raised: {exc}"],
                    required_next_action=f"Fix kernel {name}",
                )

            kernel_details.append(
                {
                    "name": name,
                    "decision": result.decision,
                    "triggered_rules": result.triggered_rules,
                    "evidence_summary": result.evidence_summary,
                }
            )

            if result.decision == "BLOCKED":
                decision = "BLOCKED"
                reason = (
                    f"Kernel '{name}': "
                    + "; ".join(result.evidence_summary[:2])
                )

        gate_results["kernels"] = (
            "BLOCKED" if decision == "BLOCKED" else "PASS"
        )

    # 5. Evidence (always log, even on block)
    evidence_entry = EvidenceEntry(
        timestamp=_now(),
        actor=identity.actor,
        tool=identity.tool,
        files=files,
        gates=gate_results,
        kernels=kernel_details,
        decision=decision,
        reason=reason,
    )

    log_path = repo_root / config.evidence_log_path
    try:
        append_entry(log_path, evidence_entry, config.evidence_hash_chain)
        gate_results["evidence"] = "PASS"
    except Exception:
        gate_results["evidence"] = "ERROR"

    return PipelineResult(
        decision=decision,
        reason=reason,
        gate_results=gate_results,
        kernel_results=kernel_details,
        actor=identity.actor,
        tool=identity.tool,
    )
