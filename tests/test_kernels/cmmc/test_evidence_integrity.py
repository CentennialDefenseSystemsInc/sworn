"""Tests for AU+CM evidence integrity kernel."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sworn.kernels.cmmc.evidence_integrity import evaluate
from sworn.kernels.sdk import KernelInput


def _write_log(log_path: Path, count: int = 3) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = "genesis"
    for i in range(count):
        entry = {
            "timestamp": f"2026-01-0{i+1}T00:00:00Z",
            "actor": "test", "tool": None, "files": [f"f{i}.py"],
            "gates": {"identity": "PASS"}, "kernels": [],
            "decision": "PASS", "reason": "", "resolution_trace": {},
            "prev_hash": prev_hash, "signature": "",
        }
        canonical = dict(entry)
        canonical["signature"] = ""
        canonical_json = json.dumps(canonical, separators=(",", ":"), sort_keys=True)
        prev_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
        line = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        with log_path.open("a") as f:
            f.write(line + "\n")


class TestEvidenceIntegrity:
    def test_valid_chain_passes(self, tmp_path: Path):
        log_path = tmp_path / ".sworn" / "evidence.jsonl"
        _write_log(log_path)
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"evidence_log_path": ".sworn/evidence.jsonl", "signing_pub_path": ".sworn/signing.pub"},
        )
        result = evaluate(inp)
        assert result.decision == "PASS"

    def test_no_log_passes(self, tmp_path: Path):
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"evidence_log_path": ".sworn/evidence.jsonl", "signing_pub_path": ".sworn/signing.pub"},
        )
        result = evaluate(inp)
        assert result.decision == "PASS"

    def test_broken_chain_blocked(self, tmp_path: Path):
        log_path = tmp_path / ".sworn" / "evidence.jsonl"
        _write_log(log_path)
        lines = log_path.read_text().splitlines()
        entry = json.loads(lines[1])
        entry["actor"] = "tampered"
        lines[1] = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        log_path.write_text("\n".join(lines) + "\n")

        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"evidence_log_path": ".sworn/evidence.jsonl", "signing_pub_path": ".sworn/signing.pub"},
        )
        result = evaluate(inp)
        assert result.decision == "BLOCKED"
        assert any("BROKEN" in e for e in result.evidence_summary)

    def test_control_ids_in_rules(self, tmp_path: Path):
        log_path = tmp_path / ".sworn" / "evidence.jsonl"
        _write_log(log_path)
        inp = KernelInput(
            files=["a.py"], actor="test", tool=None, repo_root=str(tmp_path),
            config={"evidence_log_path": ".sworn/evidence.jsonl", "signing_pub_path": ".sworn/signing.pub"},
        )
        result = evaluate(inp)
        assert "AU.L2-3.3.1" in result.triggered_rules
        assert "CM.L2-3.4.1" in result.triggered_rules
