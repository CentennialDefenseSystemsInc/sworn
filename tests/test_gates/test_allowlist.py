"""Tests for allowlist gate."""
from __future__ import annotations

from sworn.gates.allowlist import evaluate_allowlist


class TestAllowlistGate:
    def test_empty_allowlist_passes_all(self):
        result = evaluate_allowlist(["anything.py"], [])
        assert result.passed

    def test_allowed_file_passes(self):
        result = evaluate_allowlist(["src/main.py"], ["src/*"])
        assert result.passed

    def test_disallowed_file_blocked(self):
        result = evaluate_allowlist(["config/secret.py"], ["src/*"])
        assert not result.passed
        assert "config/secret.py" in result.blocked_files

    def test_glob_pattern_matching(self):
        result = evaluate_allowlist(
            ["src/app.py", "tests/test_app.py"],
            ["src/*.py", "tests/*.py"],
        )
        assert result.passed

    def test_mixed_files(self):
        result = evaluate_allowlist(
            ["src/app.py", "deploy/prod.yml"],
            ["src/*"],
        )
        assert not result.passed
        assert "deploy/prod.yml" in result.blocked_files
        assert "src/app.py" not in result.blocked_files
