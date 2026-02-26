"""Tests for AU.L2-3.3.2 traceability kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.au_traceability import evaluate
from sworn.kernels.sdk import KernelInput


class TestAUTraceability:
    def test_all_fields_present_passes(self):
        inp = KernelInput(files=["a.py"], actor="test", tool="claude", repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "PASS"

    def test_missing_actor_blocked(self):
        inp = KernelInput(files=["a.py"], actor="", tool=None, repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "BLOCKED"
        assert "actor" in result.evidence_summary[0].lower()

    def test_missing_files_blocked(self):
        inp = KernelInput(files=[], actor="test", tool=None, repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "BLOCKED"

    def test_missing_repo_root_blocked(self):
        inp = KernelInput(files=["a.py"], actor="test", tool=None, repo_root="")
        result = evaluate(inp)
        assert result.decision == "BLOCKED"

    def test_tool_none_still_passes(self):
        inp = KernelInput(files=["a.py"], actor="test", tool=None, repo_root="/tmp")
        result = evaluate(inp)
        assert result.decision == "PASS"
