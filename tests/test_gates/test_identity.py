"""Tests for identity gate."""
from __future__ import annotations

import os
from unittest.mock import patch

from sworn.gates.identity import evaluate_identity


class TestIdentityGate:
    def test_env_var_detection(self):
        with patch.dict(os.environ, {"CLAUDE_CODE": "1"}, clear=False):
            result = evaluate_identity({"CLAUDE_CODE": "claude-code"})
            assert result.tool == "claude-code"
            assert result.confidence == "detected"

    def test_no_env_vars_unknown(self):
        with patch.dict(os.environ, {}, clear=True):
            result = evaluate_identity({"NONEXISTENT_VAR": "tool"})
            assert result.tool is None
            assert result.confidence == "unknown"

    def test_multiple_tools_first_match(self):
        with patch.dict(
            os.environ,
            {"CLAUDE_CODE": "1", "CODEX_CLI": "1"},
            clear=False,
        ):
            result = evaluate_identity(
                {"CLAUDE_CODE": "claude-code", "CODEX_CLI": "codex"}
            )
            assert result.tool == "claude-code"

    def test_actor_from_git(self):
        result = evaluate_identity({})
        assert isinstance(result.actor, str)
        assert len(result.actor) > 0
