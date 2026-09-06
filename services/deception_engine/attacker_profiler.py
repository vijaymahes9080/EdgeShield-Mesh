"""
EdgeShield Mesh - MITRE ATT&CK for ICS Threat Profiler
Correlates observed adversary telemetry, honeypot traps, and protocol violations
into standard MITRE ICS tactics (e.g. T0855 Unauthorized Command Message, T0812 Default Credentials).
"""

from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field
import time


class MitreTechnique(BaseModel):
    technique_id: str
    name: str
    tactic: str
    confidence: float
    description: str


class ThreatActorProfile(BaseModel):
    attacker_ip: str
    identified_tactics: List[str]
    mapped_techniques: List[MitreTechnique]
    threat_score: float
    first_seen: float
    last_seen: float


class ICSAttackerProfiler:
    """
    Automated mapper from raw deception/incident signals to MITRE ATT&CK for ICS.
    """

    TECHNIQUE_RULES = {
        "MODBUS_UNAUTHORIZED_WRITE": MitreTechnique(
            technique_id="T0855",
            name="Unauthorized Command Message",
            tactic="Impair Process Control",
            confidence=0.92,
            description="Adversary injected rogue Modbus register writes into PLC controller."
        ),
        "CANARY_TOKEN_TRIPPED": MitreTechnique(
            technique_id="T0812",
            name="Default Credentials / Token Exfiltration",
            tactic="Initial Access",
            confidence=0.98,
            description="Adversary accessed deceptive canary credentials planted in firmware."
        ),
        "HIGH_RATE_PORT_SCAN": MitreTechnique(
            technique_id="T0846",
            name="Network Connection Enumeration",
            tactic="Discovery",
            confidence=0.85,
            description="Adversary scanned edge subnet ports and MQTT topics."
        ),
        "FIRMWARE_TAMPER_DETECTED": MitreTechnique(
            technique_id="T0857",
            name="System Firmware Modification",
            tactic="Inhibit Response Function",
            confidence=0.95,
            description="Adversary attempted unauthorized Over-The-Air firmware injection."
        )
    }

    def __init__(self):
        self.profiles: Dict[str, ThreatActorProfile] = {}

    def record_adversary_event(self, attacker_ip: str, event_key: str) -> ThreatActorProfile:
        now = time.time()
        if attacker_ip not in self.profiles:
            self.profiles[attacker_ip] = ThreatActorProfile(
                attacker_ip=attacker_ip,
                identified_tactics=[],
                mapped_techniques=[],
                threat_score=0.0,
                first_seen=now,
                last_seen=now
            )
            
        profile = self.profiles[attacker_ip]
        profile.last_seen = now
        
        if event_key in self.TECHNIQUE_RULES:
            tech = self.TECHNIQUE_RULES[event_key]
            if tech.technique_id not in [t.technique_id for t in profile.mapped_techniques]:
                profile.mapped_techniques.append(tech)
                if tech.tactic not in profile.identified_tactics:
                    profile.identified_tactics.append(tech.tactic)
                profile.threat_score = min(100.0, profile.threat_score + (tech.confidence * 25.0))
                
        return profile
