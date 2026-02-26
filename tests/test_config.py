"""Tests for config system."""
from __future__ import annotations

from pathlib import Path

import pytest

from sworn.config import SwornConfig, load_config, _compile_patterns


class TestConfig:
    def test_defaults_when_no_file(self, tmp_path: Path):
        config = load_config(tmp_path)
        assert len(config.security_patterns) > 0
        assert config.allowlist == []
        assert config.evidence_hash_chain is True

    def test_custom_patterns_load(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text(
            '[security]\npatterns = ["custom/"]'
        )
        config = load_config(tmp_path)
        assert len(config.security_patterns) == 1

    def test_invalid_toml_fails_closed(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text("{{{{invalid")
        with pytest.raises(ValueError, match="Failed to parse"):
            load_config(tmp_path)

    def test_missing_file_uses_defaults(self, tmp_path: Path):
        config = load_config(tmp_path)
        assert isinstance(config, SwornConfig)
        assert config.kernels_enabled["security"] is True

    def test_invalid_regex_fails_closed(self):
        with pytest.raises(ValueError, match="Invalid security pattern"):
            _compile_patterns(["[invalid"])

    def test_empty_allowlist_means_all_allowed(self, tmp_path: Path):
        sworn_dir = tmp_path / ".sworn"
        sworn_dir.mkdir()
        (sworn_dir / "config.toml").write_text(
            '[allowlist]\nfiles = []'
        )
        config = load_config(tmp_path)
        assert config.allowlist == []
