"""Ed25519 evidence signing — isolated key material module."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class SigningError(Exception):
    """Base error for signing operations."""


class SigningUnavailableError(SigningError):
    """PyNaCl not installed but signing key exists."""


def _nacl_available() -> bool:
    """Check if PyNaCl is importable."""
    try:
        import nacl.signing  # noqa: F401
        return True
    except ImportError:
        return False


def generate_keypair(key_dir: Path) -> tuple[Path, Path]:
    """Generate Ed25519 keypair. Returns (private_path, public_path).

    Private key file is set to 0600.
    Raises SigningError if PyNaCl is not installed or key already exists.
    """
    if not _nacl_available():
        raise SigningUnavailableError(
            "PyNaCl is required for signing: pip install pynacl"
        )

    import nacl.signing

    priv_path = key_dir / "signing.key"
    pub_path = key_dir / "signing.pub"

    if priv_path.exists():
        raise SigningError(f"Signing key already exists: {priv_path}")

    key_dir.mkdir(parents=True, exist_ok=True)

    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    priv_path.write_text(signing_key.encode().hex() + "\n")
    os.chmod(priv_path, 0o600)

    pub_path.write_text(verify_key.encode().hex() + "\n")

    return priv_path, pub_path


def load_signing_key(path: Path) -> Any:
    """Load Ed25519 signing key from hex file.

    Raises SigningError on failure. Fails closed.
    """
    if not _nacl_available():
        raise SigningUnavailableError(
            "PyNaCl is required for signing: pip install pynacl"
        )

    import nacl.signing

    try:
        key_hex = path.read_text().strip()
        key_bytes = bytes.fromhex(key_hex)
        return nacl.signing.SigningKey(key_bytes)
    except Exception as exc:
        raise SigningError(f"Failed to load signing key: {exc}") from exc


def load_verify_key(path: Path) -> Any:
    """Load Ed25519 verify key from hex file.

    Raises SigningError on failure. Fails closed.
    """
    if not _nacl_available():
        raise SigningUnavailableError(
            "PyNaCl is required for verification: pip install pynacl"
        )

    import nacl.signing

    try:
        key_hex = path.read_text().strip()
        key_bytes = bytes.fromhex(key_hex)
        return nacl.signing.VerifyKey(key_bytes)
    except Exception as exc:
        raise SigningError(f"Failed to load verify key: {exc}") from exc


def sign_entry(signing_key: Any, canonical_json: str) -> str:
    """Sign canonical JSON string, return hex signature.

    Raises SigningError on failure. Fails closed.
    """
    try:
        signed = signing_key.sign(canonical_json.encode())
        return signed.signature.hex()
    except Exception as exc:
        raise SigningError(f"Failed to sign entry: {exc}") from exc


def verify_signature(verify_key: Any, canonical_json: str, sig_hex: str) -> bool:
    """Verify signature on canonical JSON. Returns True if valid."""
    try:
        sig_bytes = bytes.fromhex(sig_hex)
        verify_key.verify(canonical_json.encode(), sig_bytes)
        return True
    except Exception:
        return False
