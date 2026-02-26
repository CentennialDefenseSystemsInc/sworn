"""Tests for CM.L2-3.4.2 configuration settings kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.cm_settings import evaluate
from sworn.kernels.sdk import KernelInput


def _input(patterns: list | None = None, security: bool = True, hash_chain: bool = True) -> KernelInput:
    return KernelInput(
        files=["a.py"], actor="test", tool=None, repo_root="/tmp",
        config={
            "security_patterns": patterns if patterns is not None else ["p1"],
            "kernels_enabled": {"security": security},
            "evidence_hash_chain": hash_chain,
        },
    )


class TestCMSettings:
    def test_all_enabled_passes(self):
        result = evaluate(_input())
        assert result.decision == "PASS"

    def test_no_patterns_blocked(self):
        result = evaluate(_input(patterns=[]))
        assert result.decision == "BLOCKED"

    def test_security_kernel_disabled_blocked(self):
        result = evaluate(_input(security=False))
        assert result.decision == "BLOCKED"

    def test_hash_chain_disabled_blocked(self):
        result = evaluate(_input(hash_chain=False))
        assert result.decision == "BLOCKED"

    def test_multiple_issues_reported(self):
        result = evaluate(_input(patterns=[], security=False, hash_chain=False))
        assert result.decision == "BLOCKED"
        # Multiple issues in evidence
        assert len(result.evidence_summary) >= 3
