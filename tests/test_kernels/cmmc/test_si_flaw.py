"""Tests for SI.L2-3.14.1 flaw remediation kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.si_flaw import evaluate
from sworn.kernels.sdk import KernelInput


class TestSIFlaw:
    def test_always_passes(self):
        inp = KernelInput(files=["a.py"], actor="test", tool=None, repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "PASS"

    def test_records_execution(self):
        inp = KernelInput(files=["a.py", "b.py"], actor="cj", tool="claude-code", repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "PASS"
        assert "SI.L2-3.14.1" in result.triggered_rules
        assert any("governance" in e.lower() for e in result.evidence_summary)

    def test_tool_in_evidence(self):
        inp = KernelInput(files=["a.py"], actor="test", tool="cursor", repo_root="/tmp")
        result = evaluate(inp)
        assert any("cursor" in e for e in result.evidence_summary)

    def test_no_tool_still_passes(self):
        inp = KernelInput(files=["a.py"], actor="test", tool=None, repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "PASS"
