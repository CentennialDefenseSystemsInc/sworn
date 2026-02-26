"""Tests for allowlist kernel."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput
from sworn.kernels.allowlist_kernel import evaluate


def _input(files: list[str], allowlist: list[str] | None = None) -> KernelInput:
    config = {"allowlist": allowlist} if allowlist is not None else {}
    return KernelInput(
        files=files, actor="test", tool=None, repo_root="/tmp", config=config
    )


class TestAllowlistKernel:
    def test_no_allowlist_passes(self):
        result = evaluate(_input(["anything.py"]))
        assert result.decision == "PASS"

    def test_empty_allowlist_passes(self):
        result = evaluate(_input(["anything.py"], allowlist=[]))
        assert result.decision == "PASS"

    def test_allowed_file_passes(self):
        result = evaluate(_input(["src/main.py"], allowlist=["src/*"]))
        assert result.decision == "PASS"

    def test_disallowed_blocked(self):
        result = evaluate(_input(["deploy/prod.yml"], allowlist=["src/*"]))
        assert result.decision == "BLOCKED"
        assert "allowlist_violation" in result.triggered_rules

    def test_evidence_summary(self):
        result = evaluate(_input(["x.py"], allowlist=["src/*"]))
        assert len(result.evidence_summary) > 0

    def test_glob_matching(self):
        result = evaluate(
            _input(["src/app.py", "tests/test.py"], allowlist=["src/*", "tests/*"])
        )
        assert result.decision == "PASS"
