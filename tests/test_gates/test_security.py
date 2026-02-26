"""Tests for security surface gate."""
from __future__ import annotations

import re

from sworn.gates.security import evaluate_security


def _patterns(raw: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in raw]


DEFAULT = _patterns([r"(^|/)(crypto|auth|gates|licensing|keys)/"])


class TestSecurityGate:
    def test_clean_files_pass(self):
        result = evaluate_security(["src/main.py", "tests/test_main.py"], DEFAULT)
        assert result.passed
        assert result.blocked_files == []

    def test_security_surface_blocked(self):
        result = evaluate_security(["crypto/vault.py"], DEFAULT)
        assert not result.passed
        assert "crypto/vault.py" in result.blocked_files

    def test_case_insensitive_blocked(self):
        result = evaluate_security(["Crypto/Key.py"], DEFAULT)
        assert not result.passed
        assert "Crypto/Key.py" in result.blocked_files

    def test_nested_path_blocked(self):
        result = evaluate_security(["src/auth/login.py"], DEFAULT)
        assert not result.passed

    def test_no_patterns_passes_all(self):
        result = evaluate_security(["crypto/vault.py"], [])
        assert result.passed

    def test_custom_patterns(self):
        custom = _patterns([r"\.secret$"])
        result = evaluate_security(["config.secret", "config.toml"], custom)
        assert not result.passed
        assert "config.secret" in result.blocked_files
        assert "config.toml" not in result.blocked_files
