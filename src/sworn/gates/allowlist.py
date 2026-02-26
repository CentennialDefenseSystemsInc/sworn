"""Allowlist gate — enforce file access control."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch


@dataclass
class AllowlistResult:
    """Result of allowlist evaluation."""

    passed: bool
    blocked_files: list[str] = field(default_factory=list)
    reason: str = ""


def evaluate_allowlist(
    files: list[str],
    allowed_patterns: list[str],
) -> AllowlistResult:
    """Check files against allowlist. Empty allowlist = all allowed."""
    if not allowed_patterns:
        return AllowlistResult(passed=True)

    blocked: list[str] = []
    for f in files:
        if not any(fnmatch(f, pattern) for pattern in allowed_patterns):
            blocked.append(f)

    if blocked:
        return AllowlistResult(
            passed=False,
            blocked_files=blocked,
            reason=f"Outside allowlist: {', '.join(blocked)}",
        )

    return AllowlistResult(passed=True)
