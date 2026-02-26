"""Security surface gate — block commits touching sensitive paths."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class SecurityResult:
    """Result of security surface evaluation."""

    passed: bool
    blocked_files: list[str] = field(default_factory=list)
    reason: str = ""


def evaluate_security(
    files: list[str],
    patterns: list[re.Pattern[str]],
) -> SecurityResult:
    """Check files against security surface patterns. Fail-closed."""
    if not patterns:
        return SecurityResult(passed=True)

    blocked: list[str] = []
    for f in files:
        for pattern in patterns:
            if pattern.search(f):
                blocked.append(f)
                break

    if blocked:
        return SecurityResult(
            passed=False,
            blocked_files=blocked,
            reason=f"Security surface: {', '.join(blocked)}",
        )

    return SecurityResult(passed=True)
