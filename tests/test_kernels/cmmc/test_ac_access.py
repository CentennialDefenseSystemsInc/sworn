"""Tests for AC.L2-3.1.1/3.1.2 access control kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.ac_access import evaluate
from sworn.kernels.sdk import KernelInput


def _input(actor: str = "test", tool: str | None = None) -> KernelInput:
    return KernelInput(files=["a.py"], actor=actor, tool=tool, repo_root="/tmp")


class TestACAccess:
    def test_known_actor_passes(self):
        result = evaluate(_input(actor="cj"))
        assert result.decision == "PASS"

    def test_unknown_actor_passes(self):
        result = evaluate(_input(actor="unknown"))
        assert result.decision == "PASS"
        assert "AC.L2-3.1.1" in result.triggered_rules

    def test_empty_actor_passes_with_manual_attestation_note(self):
        result = evaluate(_input(actor=""))
        assert result.decision == "PASS"
        assert any("manual attestation may be required" in e.lower() for e in result.evidence_summary)

    def test_ai_tool_detected(self):
        result = evaluate(_input(actor="cj", tool="claude-code"))
        assert result.decision == "PASS"
        assert "AC.L2-3.1.2" in result.triggered_rules
        assert any("claude-code" in e for e in result.evidence_summary)

    def test_no_tool_passes(self):
        result = evaluate(_input(actor="cj", tool=None))
        assert result.decision == "PASS"

    def test_threat_unknown_actor_does_not_block(self):
        result = evaluate(_input(actor=""))
        assert result.decision == "PASS"
