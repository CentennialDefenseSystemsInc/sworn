"""Tests for kernel SDK."""
from __future__ import annotations

from pathlib import Path

from sworn.kernels.sdk import (
    KernelInput,
    KernelResult,
    load_builtin_kernels,
    load_custom_kernels,
)


class TestKernelSDK:
    def test_kernel_input_construction(self):
        ki = KernelInput(
            files=["a.py"], actor="test", tool="codex", repo_root="/tmp"
        )
        assert ki.files == ["a.py"]
        assert ki.config == {}

    def test_kernel_result_construction(self):
        kr = KernelResult(decision="PASS")
        assert kr.triggered_rules == []
        assert kr.evidence_summary == []

    def test_load_builtins(self):
        kernels = load_builtin_kernels(
            {"security": True, "allowlist": True, "audit": True}
        )
        names = [name for name, _ in kernels]
        assert "security" in names
        assert "allowlist" in names
        assert "audit" in names

    def test_load_builtins_disabled(self):
        kernels = load_builtin_kernels(
            {"security": False, "allowlist": False, "audit": False}
        )
        assert len(kernels) == 0

    def test_custom_kernel_missing_dir(self, tmp_path: Path):
        kernels = load_custom_kernels(tmp_path / "nonexistent")
        assert len(kernels) == 0

    def test_custom_kernel_import_failure_blocked(self, tmp_path: Path):
        bad_kernel = tmp_path / "bad.py"
        bad_kernel.write_text("raise RuntimeError('broken')")
        kernels = load_custom_kernels(tmp_path)
        assert len(kernels) == 1
        name, fn = kernels[0]
        assert name == "bad"
        ki = KernelInput(files=[], actor="t", tool=None, repo_root="/tmp")
        result = fn(ki)
        assert result.decision == "BLOCKED"
