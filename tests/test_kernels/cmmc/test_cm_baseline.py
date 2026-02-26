"""Tests for CM.L2-3.4.1 configuration baseline kernel."""
from __future__ import annotations

from pathlib import Path

from sworn.kernels.cmmc.cm_baseline import evaluate
from sworn.kernels.sdk import KernelInput


class TestCMBaseline:
    def test_config_exists_with_patterns_passes(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text("[sworn]\nversion = '0.1'\n")
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"security_patterns": ["pattern1"]},
        )
        result = evaluate(inp)
        assert result.decision == "PASS"

    def test_no_config_blocked(self, tmp_path: Path):
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"security_patterns": []},
        )
        result = evaluate(inp)
        assert result.decision == "BLOCKED"

    def test_config_no_patterns_blocked(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text("[sworn]\n")
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"security_patterns": []},
        )
        result = evaluate(inp)
        assert result.decision == "BLOCKED"

    def test_evidence_summary_populated(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text("[sworn]\n")
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"security_patterns": ["p1", "p2"]},
        )
        result = evaluate(inp)
        assert any("2" in e for e in result.evidence_summary)
