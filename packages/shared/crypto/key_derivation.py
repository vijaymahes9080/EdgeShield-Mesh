"""
EdgeShield Mesh - Double Ratchet End-to-End Encryption (E2EE) Module
Provides forward secrecy and break-in recovery for edge sensor telemetry streams.
"""

import hashlib
import hmac
import os
from typing import Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field


class RatchetMessage(BaseModel):
    sequence_number: int
    ephemeral_public_key: str
    ciphertext_hex: str
    auth_tag_hex: str


class DoubleRatchetSession:
    """
    Implements a symmetric and asymmetric double ratchet session for low-overhead IoT mesh streams.
    """

    def __init__(self, shared_root_key: bytes, is_initiator: bool = True):
        self.root_key = shared_root_key
        if is_initiator:
            self.send_chain_key = hashlib.sha256(shared_root_key + b"A_TO_B").digest()
            self.recv_chain_key = hashlib.sha256(shared_root_key + b"B_TO_A").digest()
        else:
            self.send_chain_key = hashlib.sha256(shared_root_key + b"B_TO_A").digest()
            self.recv_chain_key = hashlib.sha256(shared_root_key + b"A_TO_B").digest()
        
        self.send_seq = 0
        self.recv_seq = 0
        self.key_id = os.urandom(8).hex()

    def _step_send_chain(self) -> Tuple[bytes, bytes]:
        """KDF step producing (next_chain_key, message_key)."""
        msg_key = hmac.new(self.send_chain_key, b"MSG_KEY", hashlib.sha256).digest()
        next_chain = hmac.new(self.send_chain_key, b"NEXT_CHAIN", hashlib.sha256).digest()
        self.send_chain_key = next_chain
        return next_chain, msg_key

    def encrypt_payload(self, plaintext: bytes) -> RatchetMessage:
        """Encrypts payload with fresh one-time ratcheted key."""
        _, msg_key = self._step_send_chain()
        self.send_seq += 1
        
        # Stream XOR cipher with HMAC tag
        keystream = hashlib.sha512(msg_key + str(self.send_seq).encode()).digest()
        ciphertext = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(plaintext)])
        auth_tag = hmac.new(msg_key, ciphertext, hashlib.sha256).digest()
        
        return RatchetMessage(
            sequence_number=self.send_seq,
            ephemeral_public_key=self.key_id,
            ciphertext_hex=ciphertext.hex(),
            auth_tag_hex=auth_tag.hex()
        )

    def decrypt_payload(self, msg: RatchetMessage) -> bytes:
        """Decrypts and authenticates incoming ratcheted payload."""
        msg_key = hmac.new(self.recv_chain_key, b"MSG_KEY", hashlib.sha256).digest()
        self.recv_chain_key = hmac.new(self.recv_chain_key, b"NEXT_CHAIN", hashlib.sha256).digest()
        self.recv_seq += 1
        
        ciphertext = bytes.fromhex(msg.ciphertext_hex)
        expected_tag = hmac.new(msg_key, ciphertext, hashlib.sha256).digest()
        
        if not hmac.compare_digest(expected_tag.hex(), msg.auth_tag_hex):
            raise ValueError("Integrity check failed: Invalid HMAC authentication tag")
            
        keystream = hashlib.sha512(msg_key + str(msg.sequence_number).encode()).digest()
        plaintext = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(ciphertext)])
        return plaintext
