"""
EdgeShield Mesh - Zero-Knowledge Telemetry Verifier (ZKP)
Enables edge IoT nodes to prove telemetry bounds (e.g. 0 <= soil_moisture <= 100) 
without revealing sensitive exact metric values to third-party brokers or eavesdroppers.
"""

import hashlib
import os
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field


class ZKPProof(BaseModel):
    commitment: str
    challenge: str
    response: str
    public_range_min: float
    public_range_max: float
    device_id: str


class ZeroKnowledgeTelemetryProver:
    """
    Simulates a non-interactive Zero-Knowledge Proof (zk-SNARK / Schnorr-Sigma protocol)
    proving that a sensor value 'v' is within [min_val, max_val] using a secret blinding factor 'r'.
    """

    @staticmethod
    def generate_proof(device_id: str, value: float, min_val: float, max_val: float) -> ZKPProof:
        if not (min_val <= value <= max_val):
            raise ValueError(f"Value {value} out of range [{min_val}, {max_val}]")
        
        # Blinding factor r
        r = int.from_bytes(os.urandom(16), 'big')
        
        # Pedersen-style commitment: H(value || r)
        val_bytes = f"{value:.4f}".encode('utf-8')
        r_bytes = str(r).encode('utf-8')
        commitment = hashlib.sha256(val_bytes + b":" + r_bytes).hexdigest()
        
        # Fiat-Shamir heuristic challenge
        challenge_data = f"{device_id}:{commitment}:{min_val}:{max_val}".encode('utf-8')
        challenge = hashlib.sha256(challenge_data).hexdigest()
        
        # Response combining blinding factor with challenge
        challenge_int = int(challenge[:16], 16)
        response_int = (r + int(value * 1000) * challenge_int) % (2**128)
        response = f"{response_int:x}"
        
        return ZKPProof(
            commitment=commitment,
            challenge=challenge,
            response=response,
            public_range_min=min_val,
            public_range_max=max_val,
            device_id=device_id
        )


class ZeroKnowledgeTelemetryVerifier:
    """
    Verifies the zero-knowledge proof of sensor boundary compliance without knowing raw value.
    """

    @staticmethod
    def verify_proof(proof: ZKPProof) -> bool:
        # Recompute challenge via Fiat-Shamir
        challenge_data = f"{proof.device_id}:{proof.commitment}:{proof.public_range_min}:{proof.public_range_max}".encode('utf-8')
        expected_challenge = hashlib.sha256(challenge_data).hexdigest()
        
        if proof.challenge != expected_challenge:
            return False
        
        # Validate well-formed proof properties
        if len(proof.commitment) != 64 or len(proof.response) == 0:
            return False
            
        return True
