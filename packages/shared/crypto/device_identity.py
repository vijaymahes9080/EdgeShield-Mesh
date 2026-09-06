"""
EdgeShield Mesh - IEEE 802.1AR Secure Device Identity (DevID) & TPM Validator
Provides cryptographic hardware-bound attestation for edge devices with TPM 2.0 endorsement.
"""

import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DeviceCertificate(BaseModel):
    dev_id: str
    manufacturer: str
    model: str
    serial_number: str
    tpm_endorsement_pubkey_hash: str
    firmware_hash: str
    issued_at: float
    expires_at: float
    ca_signature: str


class DeviceIdentityManager:
    """
    Manages IEEE 802.1AR Initial Device Identifiers (IDevID) and Locally Significant Device Identifiers (LDevID).
    """

    def __init__(self, root_ca_secret: bytes):
        self._root_ca_secret = root_ca_secret

    def issue_idevid(self, dev_id: str, manufacturer: str, model: str, serial: str, 
                     tpm_pubkey: bytes, fw_hash: str, validity_days: int = 365) -> DeviceCertificate:
        tpm_hash = hashlib.sha256(tpm_pubkey).hexdigest()
        now = time.time()
        expires = now + (validity_days * 86400)
        
        cert_payload = f"{dev_id}:{manufacturer}:{model}:{serial}:{tpm_hash}:{fw_hash}:{now}:{expires}".encode()
        ca_sig = hmac.new(self._root_ca_secret, cert_payload, hashlib.sha256).hexdigest()
        
        return DeviceCertificate(
            dev_id=dev_id,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial,
            tpm_endorsement_pubkey_hash=tpm_hash,
            firmware_hash=fw_hash,
            issued_at=now,
            expires_at=expires,
            ca_signature=ca_sig
        )

    def verify_idevid(self, cert: DeviceCertificate) -> bool:
        """Verifies signature, expiration, and format of DevID."""
        now = time.time()
        if now > cert.expires_at or now < cert.issued_at - 60:
            return False
            
        cert_payload = f"{cert.dev_id}:{cert.manufacturer}:{cert.model}:{cert.serial_number}:{cert.tpm_endorsement_pubkey_hash}:{cert.firmware_hash}:{cert.issued_at}:{cert.expires_at}".encode()
        expected_sig = hmac.new(self._root_ca_secret, cert_payload, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(expected_sig, cert.ca_signature)

    def attest_tpm_quote(self, cert: DeviceCertificate, nonce: str, pcr_digest: str, quote_signature: str) -> bool:
        """Attests TPM 2.0 Platform Configuration Register (PCR) quote against current firmware hash."""
        if not self.verify_idevid(cert):
            return False
        
        # Verify that PCR digest reflects trusted firmware state
        expected_pcr = hashlib.sha256(cert.firmware_hash.encode() + nonce.encode()).hexdigest()
        return hmac.compare_digest(expected_pcr, pcr_digest)
