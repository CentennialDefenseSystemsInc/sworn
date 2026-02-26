"""Tests for SC.L2-3.13.1 boundary protection kernel."""
from __future__ import annotations

from sworn.kernels.cmmc.sc_boundary import evaluate
from sworn.kernels.sdk import KernelInput


def _input(files: list[str]) -> KernelInput:
    return KernelInput(files=files, actor="test", tool=None, repo_root="/tmp")


class TestSCBoundary:
    def test_clean_files_pass(self):
        result = evaluate(_input(["src/main.py", "tests/test_main.py"]))
        assert result.decision == "PASS"

    def test_env_file_blocked(self):
        result = evaluate(_input([".env"]))
        assert result.decision == "BLOCKED"
        assert "SC.L2-3.13.1" in result.triggered_rules

    def test_env_prefix_blocked(self):
        result = evaluate(_input([".env.production"]))
        assert result.decision == "BLOCKED"

    def test_webhook_blocked(self):
        result = evaluate(_input(["config/webhook_handler.py"]))
        assert result.decision == "BLOCKED"

    def test_api_key_blocked(self):
        result = evaluate(_input(["api_key.json"]))
        assert result.decision == "BLOCKED"

    def test_secrets_file_blocked(self):
        result = evaluate(_input(["secrets.yaml"]))
        assert result.decision == "BLOCKED"
