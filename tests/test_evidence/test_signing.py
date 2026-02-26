"""Tests for Ed25519 evidence signing."""
from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from sworn.evidence.signing import (
    SigningError,
    generate_keypair,
    load_signing_key,
    load_verify_key,
    sign_entry,
    verify_signature,
)


@pytest.fixture
def key_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".sworn"
    d.mkdir()
    return d


class TestKeypairGeneration:
    def test_generate_creates_files(self, key_dir: Path):
        priv, pub = generate_keypair(key_dir)
        assert priv.exists()
        assert pub.exists()

    def test_private_key_permissions_600(self, key_dir: Path):
        priv, _ = generate_keypair(key_dir)
        mode = stat.S_IMODE(os.stat(priv).st_mode)
        assert mode == 0o600

    def test_refuses_overwrite(self, key_dir: Path):
        generate_keypair(key_dir)
        with pytest.raises(SigningError, match="already exists"):
            generate_keypair(key_dir)

    def test_pub_key_is_hex(self, key_dir: Path):
        _, pub = generate_keypair(key_dir)
        content = pub.read_text().strip()
        bytes.fromhex(content)  # should not raise


class TestKeyLoading:
    def test_load_roundtrip(self, key_dir: Path):
        priv_path, pub_path = generate_keypair(key_dir)
        sk = load_signing_key(priv_path)
        vk = load_verify_key(pub_path)
        assert sk is not None
        assert vk is not None

    def test_corrupt_key_fails_closed(self, key_dir: Path):
        key_file = key_dir / "signing.key"
        key_file.write_text("not-valid-hex\n")
        with pytest.raises(SigningError, match="Failed to load"):
            load_signing_key(key_file)

    def test_missing_key_fails_closed(self, key_dir: Path):
        with pytest.raises(SigningError):
            load_signing_key(key_dir / "nonexistent.key")


class TestSignAndVerify:
    def test_sign_and_verify(self, key_dir: Path):
        priv_path, pub_path = generate_keypair(key_dir)
        sk = load_signing_key(priv_path)
        vk = load_verify_key(pub_path)

        data = '{"decision":"PASS","timestamp":"2026-01-01T00:00:00Z"}'
        sig = sign_entry(sk, data)
        assert verify_signature(vk, data, sig)

    def test_tampered_data_fails(self, key_dir: Path):
        priv_path, pub_path = generate_keypair(key_dir)
        sk = load_signing_key(priv_path)
        vk = load_verify_key(pub_path)

        data = '{"decision":"PASS"}'
        sig = sign_entry(sk, data)
        assert not verify_signature(vk, data + "x", sig)

    def test_wrong_key_fails(self, tmp_path: Path):
        d1 = tmp_path / "k1"
        d1.mkdir()
        d2 = tmp_path / "k2"
        d2.mkdir()

        p1, _ = generate_keypair(d1)
        _, pub2 = generate_keypair(d2)

        sk1 = load_signing_key(p1)
        vk2 = load_verify_key(pub2)

        data = '{"test": true}'
        sig = sign_entry(sk1, data)
        assert not verify_signature(vk2, data, sig)

    def test_signature_deterministic(self, key_dir: Path):
        priv_path, _ = generate_keypair(key_dir)
        sk = load_signing_key(priv_path)

        data = '{"stable":"content"}'
        sig1 = sign_entry(sk, data)
        sig2 = sign_entry(sk, data)
        # Ed25519 signatures are deterministic for same key + message
        assert sig1 == sig2
