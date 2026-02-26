"""Tests for CM.L2-3.4.5 access restrictions kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.cm_access import evaluate
from sworn.kernels.sdk import KernelInput


def _input(patterns: list | None = None, allowlist: list | None = None) -> KernelInput:
    return KernelInput(
        files=["a.py"], actor="test", tool=None, repo_root="/tmp",
        config={
            "security_patterns": patterns if patterns is not None else [],
            "allowlist": allowlist if allowlist is not None else [],
        },
    )


class TestCMAccess:
    def test_patterns_active_passes(self):
        result = evaluate(_input(patterns=["p1"]))
        assert result.decision == "PASS"

    def test_allowlist_active_passes(self):
        result = evaluate(_input(allowlist=["*.py"]))
        assert result.decision == "PASS"

    def test_both_active_passes(self):
        result = evaluate(_input(patterns=["p1"], allowlist=["*.py"]))
        assert result.decision == "PASS"

    def test_neither_active_blocked(self):
        result = evaluate(_input(patterns=[], allowlist=[]))
        assert result.decision == "BLOCKED"
        assert "CM.L2-3.4.5" in result.triggered_rules
