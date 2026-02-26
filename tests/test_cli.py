"""Tests for sworn CLI."""
from __future__ import annotations

import subprocess
from pathlib import Path

from sworn.cli import cmd_init, cmd_status, cmd_check, main


class TestCLI:
    def test_init_creates_sworn_dir(self, tmp_repo: Path):
        result = cmd_init(tmp_repo)
        assert result == 0
        assert (tmp_repo / ".sworn" / "config.toml").exists()

    def test_init_installs_hook(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        hook = tmp_repo / ".git" / "hooks" / "pre-commit"
        assert hook.exists()
        assert "sworn check" in hook.read_text()

    def test_init_idempotent(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        result = cmd_init(tmp_repo)
        assert result == 0
        # Config not overwritten
        assert (tmp_repo / ".sworn" / "config.toml").exists()

    def test_init_non_git_fails(self, tmp_path: Path):
        result = cmd_init(tmp_path)
        assert result == 1

    def test_check_clean_files(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        # Stage a clean file
        (tmp_repo / "app.py").write_text("print('hello')")
        subprocess.run(
            ["git", "add", "app.py"], cwd=tmp_repo, capture_output=True
        )
        result = cmd_check(tmp_repo)
        assert result == 0

    def test_check_no_staged_files(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        result = cmd_check(tmp_repo)
        assert result == 0  # Nothing to gate

    def test_status_not_initialized(self, tmp_repo: Path):
        result = cmd_status(tmp_repo)
        assert result == 0

    def test_version(self, capsys):
        import pytest
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        captured = capsys.readouterr()
        assert "0.3.0" in captured.out

    def test_no_command_shows_help(self, capsys):
        result = main([])
        assert result == 0
