"""Tests for sworn keygen CLI command."""
from __future__ import annotations

from pathlib import Path

from sworn.cli import cmd_keygen, cmd_init


class TestKeygen:
    def test_keygen_creates_keypair(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        result = cmd_keygen(tmp_repo)
        assert result == 0
        assert (tmp_repo / ".sworn" / "signing.key").exists()
        assert (tmp_repo / ".sworn" / "signing.pub").exists()

    def test_keygen_refuses_overwrite(self, tmp_repo: Path):
        cmd_init(tmp_repo)
        cmd_keygen(tmp_repo)
        result = cmd_keygen(tmp_repo)
        assert result == 1

    def test_keygen_requires_init(self, tmp_repo: Path):
        result = cmd_keygen(tmp_repo)
        assert result == 1

    def test_keygen_warns_gitignore(self, tmp_repo: Path, capsys):
        cmd_init(tmp_repo)
        # No .gitignore in tmp_repo
        cmd_keygen(tmp_repo)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "gitignore" in captured.out.lower()
