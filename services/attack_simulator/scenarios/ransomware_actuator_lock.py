"""
EdgeShield Mesh - Attack Scenario: ICS Ransomware Actuator Lock
Simulates an extortion threat vector where malware locks digital valves in open/closed states,
overwrites configuration memory with encrypted blobs, and issues extortion demands via MQTT topic messages.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import time


class RansomwarePayload(BaseModel):
    attack_name: str = "AGRI_LOCK_ICS_RANSOMWARE"
    target_actuators: List[str]
    locked_state: str  # PERMANENTLY_CLOSED / PERMANENTLY_OPEN
    ransom_demand_topic: str
    ransom_note: str
    encryption_algorithm: str
    timestamp: float = Field(default_factory=time.time)


class RansomwareActuatorLockScenario:
    """
    Simulates operational extortion attack targeting smart farm irrigation grids.
    """

    @staticmethod
    def trigger_actuator_lock(target_valves: Optional[List[str]] = None) -> RansomwarePayload:
        valves = target_valves or ["valve-gamma-01", "valve-gamma-02", "solar-pump-delta"]
        return RansomwarePayload(
            target_actuators=valves,
            locked_state="PERMANENTLY_CLOSED",
            ransom_demand_topic="agri/emergency/ransom_notice",
            ransom_note="CRITICAL WARNING: All field irrigation valves have been cryptographically locked. Crop dehydration will begin within 4 hours. Contact unlock@threat-group.onion with 2.5 XMR.",
            encryption_algorithm="ChaCha20-Poly1305 (Flash registers overwritten)"
        )
