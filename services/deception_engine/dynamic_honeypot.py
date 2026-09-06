"""
EdgeShield Mesh - Dynamic Shadow Twin Honeypot
Generates realistic deceptive virtual shadow twins of critical field PLCs, RTUs,
and irrigation actuators to lure, deceive, and profile active threat actors.
"""

import time
import random
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DecoyInteraction(BaseModel):
    honeypot_id: str
    attacker_ip: str
    protocol: str
    command_executed: str
    timestamp: float = Field(default_factory=time.time)
    captured_payload: str


class DynamicHoneypotTwin:
    """
    Simulates high-interaction deceptive industrial controllers (Modbus, MQTT, CoAP).
    """

    def __init__(self, honeypot_id: str, device_type: str = "Siemens_S7_1200_PLC"):
        self.honeypot_id = honeypot_id
        self.device_type = device_type
        self.virtual_registers: Dict[int, int] = {i: random.randint(100, 500) for i in range(100)}
        self.interaction_log: List[DecoyInteraction] = []

    def handle_modbus_read(self, attacker_ip: str, register_addr: int) -> int:
        val = self.virtual_registers.get(register_addr, 0)
        self.interaction_log.append(DecoyInteraction(
            honeypot_id=self.honeypot_id,
            attacker_ip=attacker_ip,
            protocol="MODBUS_TCP",
            command_executed=f"READ_HOLDING_REG_{register_addr}",
            captured_payload=f"ADDR={register_addr},VAL={val}"
        ))
        return val

    def handle_modbus_write(self, attacker_ip: str, register_addr: int, value: int) -> bool:
        self.virtual_registers[register_addr] = value
        self.interaction_log.append(DecoyInteraction(
            honeypot_id=self.honeypot_id,
            attacker_ip=attacker_ip,
            protocol="MODBUS_TCP",
            command_executed=f"WRITE_HOLDING_REG_{register_addr}",
            captured_payload=f"ADDR={register_addr},NEW_VAL={value}"
        ))
        return True

    def get_trapped_interactions(self) -> List[DecoyInteraction]:
        return self.interaction_log
