"""
EdgeShield Mesh - Adaptive MQTT Connection Tarpit
Dynamically slows down and traps malicious scanning scanners and brute-force bots
by trickling TCP keep-alives and byte fragments, wasting adversary resources while extracting TTP telemetry.
"""

import time
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class TarpitSession(BaseModel):
    session_id: str
    attacker_ip: str
    delay_ms_per_byte: int
    trapped_duration_seconds: float = 0.0
    bytes_sent: int = 0
    is_active: bool = True
    started_at: float = Field(default_factory=time.time)


class AdaptiveTarpitController:
    """
    Manages rate-limiting and connection trapping for offending source IPs.
    """

    def __init__(self, default_delay_ms: int = 500, max_tarpit_duration: float = 300.0):
        self.default_delay_ms = default_delay_ms
        self.max_tarpit_duration = max_tarpit_duration
        self.active_sessions: Dict[str, TarpitSession] = {}

    def trap_ip(self, attacker_ip: str, severity_multiplier: float = 1.0) -> TarpitSession:
        delay = int(self.default_delay_ms * severity_multiplier)
        session = TarpitSession(
            session_id=f"tarpit-{attacker_ip}",
            attacker_ip=attacker_ip,
            delay_ms_per_byte=delay
        )
        self.active_sessions[attacker_ip] = session
        return session

    def stream_byte_chunk(self, attacker_ip: str, chunk_size: int = 1) -> Optional[int]:
        """Simulates trickling data to the adversary."""
        session = self.active_sessions.get(attacker_ip)
        if not session or not session.is_active:
            return None
            
        elapsed = time.time() - session.started_at
        if elapsed > self.max_tarpit_duration:
            session.is_active = False
            return None
            
        session.bytes_sent += chunk_size
        session.trapped_duration_seconds = elapsed
        return session.delay_ms_per_byte * chunk_size

    def release_ip(self, attacker_ip: str):
        if attacker_ip in self.active_sessions:
            self.active_sessions[attacker_ip].is_active = False
