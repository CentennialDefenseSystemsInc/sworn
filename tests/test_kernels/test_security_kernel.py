"""Tests for security kernel."""
from __future__ import annotations

from sworn.kernels.sdk import KernelInput
from sworn.kernels.security_kernel import evaluate


def _input(files: list[str], **kwargs) -> KernelInput:
    return KernelInput(
        files=files, actor="test", tool=None, repo_root="/tmp", config=kwargs
    )


class TestSecurityKernel:
    def test_clean_files_pass(self):
        result = evaluate(_input(["src/main.py"]))
        assert result.decision == "PASS"

    def test_crypto_blocked(self):
        result = evaluate(_input(["crypto/vault.py"]))
        assert result.decision == "BLOCKED"
        assert "security_surface" in result.triggered_rules

    def test_auth_blocked(self):
        result = evaluate(_input(["auth/login.py"]))
        assert result.decision == "BLOCKED"

    def test_env_file_blocked(self):
        result = evaluate(_input([".env"]))
        assert result.decision == "BLOCKED"

    def test_evidence_summary_populated(self):
        result = evaluate(_input(["keys/api.key"]))
        assert len(result.evidence_summary) > 0

    def test_multiple_files_partial_block(self):
        result = evaluate(_input(["src/main.py", "crypto/key.py"]))
        assert result.decision == "BLOCKED"
        assert any("1 file" in s for s in result.evidence_summary)
