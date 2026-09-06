"""
EdgeShield Mesh - Attack Scenario: SolarWinds-Style Malicious OTA Firmware Tamper
Simulates man-in-the-middle interception of an unencrypted OTA firmware download,
modifying the binary image payload while forging checksums to hijack MCU execution vectors.
"""

import hashlib
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field


class TamperedOTAPayload(BaseModel):
    version: str
    target_model: str
    original_sha256: str
    tampered_sha256: str
    injected_exploit_vector: str
    is_signature_forged: bool


class SolarWindsOTATamperScenario:
    """
    Generates realistic OTA update injection attacks.
    """

    @staticmethod
    def construct_tampered_update(device_model: str = "AS-SOIL-ALPHA-v1.2.0") -> TamperedOTAPayload:
        clean_bin = b"\x7FELF_CLEAN_FIRMWARE_PAYLOAD_V120"
        orig_hash = hashlib.sha256(clean_bin).hexdigest()
        
        # Injected rootkit payload
        tampered_bin = clean_bin + b"\x90\x90\x90_INJECTED_ROOTKIT_PAYLOAD_REVERSE_SHELL"
        tampered_hash = hashlib.sha256(tampered_bin).hexdigest()
        
        return TamperedOTAPayload(
            version="v1.2.1-SECURITY-HOTFIX-SPOOFED",
            target_model=device_model,
            original_sha256=orig_hash,
            tampered_sha256=tampered_hash,
            injected_exploit_vector="Rogue TCP callback payload hooked into FreeRTOS task scheduler",
            is_signature_forged=True
        )
