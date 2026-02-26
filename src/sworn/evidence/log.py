"""Evidence log — append-only JSONL with optional SHA256 hash chain."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EvidenceEntry:
    """A single gate pipeline execution record."""

    timestamp: str
    actor: str
    tool: str | None
    files: list[str]
    gates: dict[str, str]
    kernels: list[dict[str, Any]]
    decision: str
    reason: str = ""
    prev_hash: str = "genesis"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_entry(entry_json: str) -> str:
    return hashlib.sha256(entry_json.encode()).hexdigest()


def read_last_hash(log_path: Path) -> str:
    """Read the hash of the last entry. Returns 'genesis' if log is empty."""
    if not log_path.exists():
        return "genesis"
    try:
        with log_path.open("r") as f:
            last_line = ""
            for line in f:
                line = line.strip()
                if line:
                    last_line = line
            if not last_line:
                return "genesis"
            return _hash_entry(last_line)
    except Exception:
        return "genesis"


def append_entry(
    log_path: Path,
    entry: EvidenceEntry,
    hash_chain: bool = True,
) -> None:
    """Append an evidence entry to the JSONL log."""
    if hash_chain:
        entry.prev_hash = read_last_hash(log_path)

    entry_dict = asdict(entry)
    entry_json = json.dumps(entry_dict, separators=(",", ":"), sort_keys=True)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(entry_json + "\n")


def read_entries(log_path: Path) -> list[dict[str, Any]]:
    """Read all entries from evidence log."""
    if not log_path.exists():
        return []

    entries: list[dict[str, Any]] = []
    with log_path.open("r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def verify_chain(log_path: Path) -> tuple[bool, str]:
    """Verify the hash chain integrity. Returns (valid, message)."""
    if not log_path.exists():
        return True, "No evidence log found"

    prev_hash = "genesis"
    line_num = 0

    with log_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line_num += 1

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                return False, f"Line {line_num}: invalid JSON"

            stored_hash = entry.get("prev_hash", "")
            if stored_hash != prev_hash:
                return False, (
                    f"Line {line_num}: hash chain broken "
                    f"(expected {prev_hash[:16]}..., got {stored_hash[:16]}...)"
                )

            prev_hash = _hash_entry(line)

    return True, f"Chain valid: {line_num} entries"
