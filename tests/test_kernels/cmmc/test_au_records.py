"""Tests for AU.L2-3.3.1 audit records kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.au_records import evaluate
from sworn.kernels.sdk import KernelInput


def _input(hash_chain: bool = True) -> KernelInput:
    return KernelInput(
        files=["a.py"], actor="test", tool=None, repo_root="/tmp",
        config={"evidence_hash_chain": hash_chain, "evidence_log_path": ".sworn/evidence.jsonl"},
    )


class TestAURecords:
    def test_hash_chain_enabled_passes(self):
        result = evaluate(_input(hash_chain=True))
        assert result.decision == "PASS"
        assert "AU.L2-3.3.1" in result.triggered_rules

    def test_hash_chain_disabled_blocked(self):
        result = evaluate(_input(hash_chain=False))
        assert result.decision == "BLOCKED"

    def test_evidence_summary_populated(self):
        result = evaluate(_input())
        assert any("hash chain" in e.lower() for e in result.evidence_summary)

    def test_default_config_passes(self):
        inp = KernelInput(files=["a.py"], actor="test", tool=None, repo_root="/tmp", config={})
        result = evaluate(inp)
        assert result.decision == "PASS"
