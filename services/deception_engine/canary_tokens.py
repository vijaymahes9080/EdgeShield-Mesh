"""
EdgeShield Mesh - Canary Token Generator & Tripline Monitor
Injects unique cryptographic canary credentials, API tokens, and dummy topics 
into firmware binaries, git repos, and internal MQTT brokers to instantly alert on exfiltration.
"""

import hashlib
import hmac
import time
from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class CanaryToken(BaseModel):
    token_id: str
    token_secret: str
    token_type: str  # MQTT_TOPIC, API_KEY, CONFIG_CREDENTIAL
    injected_location: str
    created_at: float = Field(default_factory=time.time)


class CanaryTripAlert(BaseModel):
    token_id: str
    token_type: str
    injected_location: str
    source_ip: str
    trigger_context: str
    timestamp: float = Field(default_factory=time.time)


class CanaryTokenManager:
    """
    Manages active tripwires and validates unauthorized canary token access.
    """

    def __init__(self, master_secret: bytes):
        self._master_secret = master_secret
        self.active_canaries: Dict[str, CanaryToken] = {}
        self.tripped_alerts: List[CanaryTripAlert] = []

    def generate_token(self, token_type: str, injected_location: str) -> CanaryToken:
        token_id = hashlib.sha256(f"{token_type}:{injected_location}:{time.time()}".encode()).hexdigest()[:16]
        token_secret = hmac.new(self._master_secret, token_id.encode(), hashlib.sha256).hexdigest()
        
        token = CanaryToken(
            token_id=token_id,
            token_secret=token_secret,
            token_type=token_type,
            injected_location=injected_location
        )
        self.active_canaries[token_id] = token
        self.active_canaries[token_secret] = token
        return token

    def check_access_and_trip(self, candidate_token_or_secret: str, source_ip: str, context: str) -> Optional[CanaryTripAlert]:
        if candidate_token_or_secret in self.active_canaries:
            canary = self.active_canaries[candidate_token_or_secret]
            alert = CanaryTripAlert(
                token_id=canary.token_id,
                token_type=canary.token_type,
                injected_location=canary.injected_location,
                source_ip=source_ip,
                trigger_context=context
            )
            self.tripped_alerts.append(alert)
            return alert
        return None
