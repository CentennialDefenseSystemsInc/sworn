"""AU+CM cross-cut — Evidence integrity: hash chain and signatures valid."""
from __future__ import annotations

from pathlib import Path

from sworn.kernels.sdk import KernelInput, KernelResult


def evaluate(kernel_input: KernelInput) -> KernelResult:
    """BLOCKED when evidence chain is broken or signatures invalid."""
    from sworn.evidence.log import verify_chain

    evidence: list[str] = []
    rules: list[str] = ["AU.L2-3.3.1", "CM.L2-3.4.1"]

    repo_root = Path(kernel_input.repo_root)
    config = kernel_input.config
    log_path = repo_root / config.get("evidence_log_path", ".sworn/evidence.jsonl")

    if not log_path.exists():
        evidence.append("No evidence log found (new installation)")
        return KernelResult(
            decision="PASS",
            triggered_rules=rules,
            evidence_summary=evidence,
        )

    # Verify hash chain
    verify_key = None
    verify_key_dir = None
    pub_path = repo_root / config.get("signing_pub_path", ".sworn/keys/")
    if pub_path.exists():
        try:
            if pub_path.is_dir():
                verify_key_dir = pub_path
            else:
                from sworn.evidence.signing import load_verify_key
                verify_key = load_verify_key(pub_path)
        except Exception as exc:
            evidence.append(f"Could not load verify key: {exc}")

    if verify_key is not None:
        valid, msg = verify_chain(log_path, verify_key=verify_key)
    elif verify_key_dir is not None:
        valid, msg = verify_chain(log_path, verify_key_dir=verify_key_dir)
    else:
        valid, msg = verify_chain(log_path)

    if not valid:
        evidence.append(f"Evidence chain BROKEN: {msg}")
        return KernelResult(
            decision="BLOCKED",
            triggered_rules=rules,
            evidence_summary=evidence,
            required_next_action="Investigate evidence chain integrity breach",
        )

    evidence.append(f"Evidence chain valid: {msg}")
    if verify_key:
        evidence.append("Signatures verified")

    return KernelResult(
        decision="PASS",
        triggered_rules=rules,
        evidence_summary=evidence,
    )
