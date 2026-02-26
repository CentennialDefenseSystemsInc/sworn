"""Tests for evidence log."""
from __future__ import annotations

import json
from pathlib import Path

from sworn.evidence.log import (
    EvidenceEntry,
    append_entry,
    read_entries,
    read_last_hash,
    verify_chain,
)


class TestEvidenceLog:
    def test_append_and_read(self, tmp_path: Path):
        log = tmp_path / "evidence.jsonl"
        entry = EvidenceEntry(
            timestamp="2026-01-01T00:00:00Z",
            actor="test",
            tool=None,
            files=["a.py"],
            gates={"identity": "PASS"},
            kernels=[],
            decision="PASS",
        )
        append_entry(log, entry, hash_chain=False)
        entries = read_entries(log)
        assert len(entries) == 1
        assert entries[0]["actor"] == "test"

    def test_hash_chain_genesis(self, tmp_path: Path):
        log = tmp_path / "evidence.jsonl"
        assert read_last_hash(log) == "genesis"

    def test_hash_chain_integrity(self, tmp_path: Path):
        log = tmp_path / "evidence.jsonl"
        for i in range(3):
            entry = EvidenceEntry(
                timestamp=f"2026-01-0{i+1}T00:00:00Z",
                actor="test",
                tool=None,
                files=[f"file{i}.py"],
                gates={"identity": "PASS"},
                kernels=[],
                decision="PASS",
            )
            append_entry(log, entry, hash_chain=True)

        valid, msg = verify_chain(log)
        assert valid, msg

    def test_tampered_chain_detected(self, tmp_path: Path):
        log = tmp_path / "evidence.jsonl"
        for i in range(3):
            entry = EvidenceEntry(
                timestamp=f"2026-01-0{i+1}T00:00:00Z",
                actor="test",
                tool=None,
                files=[f"file{i}.py"],
                gates={"identity": "PASS"},
                kernels=[],
                decision="PASS",
            )
            append_entry(log, entry, hash_chain=True)

        # Tamper with line 2
        lines = log.read_text().splitlines()
        entry2 = json.loads(lines[1])
        entry2["actor"] = "tampered"
        lines[1] = json.dumps(entry2, separators=(",", ":"), sort_keys=True)
        log.write_text("\n".join(lines) + "\n")

        valid, msg = verify_chain(log)
        assert not valid
        assert "broken" in msg.lower()

    def test_write_failure_no_crash(self, tmp_path: Path):
        log = tmp_path / "readonly" / "deep" / "evidence.jsonl"
        # Create parent as a file to make mkdir fail
        (tmp_path / "readonly").mkdir()
        (tmp_path / "readonly" / "deep").write_text("blocker")
        entry = EvidenceEntry(
            timestamp="2026-01-01T00:00:00Z",
            actor="test",
            tool=None,
            files=[],
            gates={},
            kernels=[],
            decision="PASS",
        )
        try:
            append_entry(log, entry)
            assert False, "Should have raised"
        except (NotADirectoryError, OSError):
            pass  # Expected — fail-closed behavior tested via pipeline
