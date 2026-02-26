"""Disposition resolver — deterministic kernel conflict resolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class KernelDisposition:
    """A single kernel's verdict."""

    name: str
    decision: Literal["PASS", "BLOCKED"]
    triggered_rules: list[str] = field(default_factory=list)
    evidence_summary: list[str] = field(default_factory=list)


@dataclass
class ResolutionTrace:
    """Auditable resolution of all kernel dispositions."""

    dispositions: list[KernelDisposition]
    applied_overrides: list[str]
    final_decision: Literal["PASS", "BLOCKED"]
    final_reason: str
    blocked_by: list[str]


def resolve(
    dispositions: list[KernelDisposition],
    precedence_rules: list[dict[str, str]] | None = None,
) -> ResolutionTrace:
    """Resolve kernel dispositions into a single decision.

    Precedence rules can only REMOVE blocks, never ADD them.
    Fail-closed by construction: any unresolved block -> BLOCKED.

    Each precedence rule is a dict with:
        - when_pass: kernel name that must have passed
        - overrides_block: kernel name whose block is overridden

    Returns a ResolutionTrace with full audit trail.
    """
    if not dispositions:
        return ResolutionTrace(
            dispositions=[],
            applied_overrides=[],
            final_decision="PASS",
            final_reason="No kernels evaluated",
            blocked_by=[],
        )

    blocked_set = {
        d.name for d in dispositions if d.decision == "BLOCKED"
    }
    passed_set = {
        d.name for d in dispositions if d.decision == "PASS"
    }
    applied_overrides: list[str] = []

    for rule in precedence_rules or []:
        when_pass = rule.get("when_pass", "")
        overrides_block = rule.get("overrides_block", "")

        if not when_pass or not overrides_block:
            continue

        if when_pass in passed_set and overrides_block in blocked_set:
            blocked_set.discard(overrides_block)
            applied_overrides.append(
                f"{when_pass} PASS overrides {overrides_block} BLOCKED"
            )

    blocked_by = sorted(blocked_set)

    if blocked_by:
        blocked_dispositions = [
            d for d in dispositions if d.name in blocked_set
        ]
        reasons = []
        for d in blocked_dispositions:
            summary = "; ".join(d.evidence_summary[:2]) if d.evidence_summary else "no details"
            reasons.append(f"Kernel '{d.name}': {summary}")
        final_reason = " | ".join(reasons)
        final_decision: Literal["PASS", "BLOCKED"] = "BLOCKED"
    else:
        final_reason = "All kernels passed" if not applied_overrides else (
            "All blocks resolved via precedence overrides"
        )
        final_decision = "PASS"

    return ResolutionTrace(
        dispositions=list(dispositions),
        applied_overrides=applied_overrides,
        final_decision=final_decision,
        final_reason=final_reason,
        blocked_by=blocked_by,
    )
