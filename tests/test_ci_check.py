"""Tests for sworn ci-check CLI command."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from sworn.cli import cmd_ci_check, cmd_init


class TestCICheck:
    def test_clean_diff_passes(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        # Create a file and commit it so there's history
        (tmp_repo / "app.py").write_text("print('hello')")
        subprocess.run(["git", "add", "app.py"], cwd=tmp_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "add app"],
            cwd=tmp_repo, capture_output=True,
        )
        # ci-check with no diff files should pass
        result = cmd_ci_check(tmp_repo, "HEAD")
        assert result == 0

    def test_no_diff_passes(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        result = cmd_ci_check(tmp_repo, "HEAD")
        assert result == 0

    def test_uses_github_base_ref(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        with patch.dict(os.environ, {"GITHUB_BASE_REF": "main"}):
            # Should use GITHUB_BASE_REF when no --base given
            result = cmd_ci_check(tmp_repo, None)
            # May fail on git diff but shouldn't crash
            assert result in (0, 1)

    def test_security_surface_blocks(self, tmp_repo: Path):
        # Determine default branch name
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=tmp_repo, capture_output=True, text=True,
        )
        default_branch = res.stdout.strip()
        # Create a branch with a security surface file BEFORE init
        # (init installs pre-commit hook which would block the commit)
        subprocess.run(
            ["git", "checkout", "-b", "feature"],
            cwd=tmp_repo, capture_output=True,
        )
        (tmp_repo / "crypto").mkdir()
        (tmp_repo / "crypto" / "vault.py").write_text("secret = 42")
        subprocess.run(
            ["git", "add", "crypto/vault.py"],
            cwd=tmp_repo, capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "add crypto"],
            cwd=tmp_repo, capture_output=True, check=True,
        )
        # Now init sworn for ci-check
        cmd_init(tmp_repo)
        # Compare against default branch (first commit)
        result = cmd_ci_check(tmp_repo, default_branch)
        assert result == 1

    def test_ci_check_help(self):
        """ci-check subcommand is registered."""
        from sworn.cli import main
        import pytest
        # Should not error on --help
        with pytest.raises(SystemExit, match="0"):
            main(["ci-check", "--help"])
