"""
Unit tests for Post-Quantum Cryptography, Zero-Knowledge Proofs, DevID, and Double Ratchet.
"""

import pytest
import os
from packages.shared.crypto.pqc import PQCKeyExchange, PQCDigitalSigner
from packages.shared.crypto.zkp import ZeroKnowledgeTelemetryProver, ZeroKnowledgeTelemetryVerifier
from packages.shared.crypto.device_identity import DeviceIdentityManager
from packages.shared.crypto.key_derivation import DoubleRatchetSession


def test_pqc_key_exchange():
    alice = PQCKeyExchange(key_id="alice-edge-node")
    bob = PQCKeyExchange(key_id="bob-gateway")
    
    # Alice encapsulates against Bob's public key
    ciphertext, alice_shared = alice.encapsulate(bob.public_key_hex)
    
    # Bob decapsulates
    bob_shared = bob.decapsulate(ciphertext, alice.public_key_hex)
    
    assert alice_shared == bob_shared
    assert len(alice_shared) == 32


def test_pqc_digital_signature():
    signer = PQCDigitalSigner(key_id="sensor-alpha")
    payload = b'{"sensor_id": "moisture-01", "moisture": 42.5}'
    
    header = signer.sign_payload(payload)
    assert header.public_key_id == "sensor-alpha"
    assert signer.verify_signature(payload, header) is True
    assert signer.verify_signature(b'tampered_payload', header) is False


def test_zkp_telemetry_prover_verifier():
    # Prove that 45.2% is within valid soil moisture range [0, 100]
    proof = ZeroKnowledgeTelemetryProver.generate_proof(
        device_id="soil-moisture-alpha",
        value=45.2,
        min_val=0.0,
        max_val=100.0
    )
    
    assert ZeroKnowledgeTelemetryVerifier.verify_proof(proof) is True
    
    # Tampering challenge fails verification
    proof.challenge = "deadbeef" * 8
    assert ZeroKnowledgeTelemetryVerifier.verify_proof(proof) is False


def test_device_identity_and_attestation():
    ca_secret = os.urandom(32)
    id_mgr = DeviceIdentityManager(root_ca_secret=ca_secret)
    tpm_key = os.urandom(32)
    fw_hash = "a" * 64
    
    cert = id_mgr.issue_idevid(
        dev_id="irrigation-valve-01",
        manufacturer="AgriShield Systems",
        model="AS-VALVE-X",
        serial="SN-99881122",
        tpm_pubkey=tpm_key,
        fw_hash=fw_hash
    )
    
    assert id_mgr.verify_idevid(cert) is True
    
    # Valid PCR attestation
    import hashlib
    nonce = "random-nonce-123"
    pcr_digest = hashlib.sha256(fw_hash.encode() + nonce.encode()).hexdigest()
    assert id_mgr.attest_tpm_quote(cert, nonce, pcr_digest, "dummy_sig") is True


def test_double_ratchet_session():
    shared_root = os.urandom(32)
    alice = DoubleRatchetSession(shared_root_key=shared_root, is_initiator=True)
    bob = DoubleRatchetSession(shared_root_key=shared_root, is_initiator=False)
    
    msg1 = alice.encrypt_payload(b"Telemetry Sample 1")
    decrypted1 = bob.decrypt_payload(msg1)
    assert decrypted1 == b"Telemetry Sample 1"
    
    msg2 = alice.encrypt_payload(b"Telemetry Sample 2")
    decrypted2 = bob.decrypt_payload(msg2)
    assert decrypted2 == b"Telemetry Sample 2"
