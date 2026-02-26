"""Tests for audit kernel."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput
from sworn.kernels.audit_kernel import evaluate


def _input(files: list[str], actor: str = "test", tool: str | None = None) -> KernelInput:
    return KernelInput(
        files=files, actor=actor, tool=tool, repo_root="/tmp", config={}
    )


class TestAuditKernel:
    def test_always_passes(self):
        result = evaluate(_input(["src/main.py"]))
        assert result.decision == "PASS"

    def test_records_actor(self):
        result = evaluate(_input(["x.py"], actor="cj"))
        assert any("cj" in s for s in result.evidence_summary)

    def test_records_tool(self):
        result = evaluate(_input(["x.py"], tool="claude-code"))
        assert any("claude-code" in s for s in result.evidence_summary)

    def test_records_no_tool(self):
        result = evaluate(_input(["x.py"]))
        assert any("none" in s for s in result.evidence_summary)

    def test_records_file_count(self):
        result = evaluate(_input(["a.py", "b.py", "c.py"]))
        assert any("3" in s for s in result.evidence_summary)

    def test_evidence_max_five(self):
        result = evaluate(_input(["a.py", "b.py"]))
        assert len(result.evidence_summary) <= 5
