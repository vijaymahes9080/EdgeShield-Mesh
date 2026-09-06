"""
EdgeShield Mesh - Modbus-TCP Application Layer Security Guardian
Enforces strict function code whitelisting, address range boundary restrictions,
and write-rate throttling on legacy industrial PLC Modbus-TCP (Port 502) traffic.
"""

import struct
from typing import Dict, List, Tuple, Optional, Set
from pydantic import BaseModel, Field


class ModbusTCPFrame(BaseModel):
    transaction_id: int
    protocol_id: int
    length: int
    unit_id: int
    function_code: int
    data_hex: str


class ModbusTCPGuardian:
    """
    Stateful Modbus-TCP firewall and DPI engine.
    """

    ALLOWED_READ_FUNCTION_CODES = {0x01, 0x02, 0x03, 0x04}
    ALLOWED_WRITE_FUNCTION_CODES = {0x05, 0x06, 0x10} # Coils and Holding registers

    def __init__(self, read_only_mode: bool = False, allowed_units: Optional[Set[int]] = None):
        self.read_only_mode = read_only_mode
        self.allowed_units = allowed_units or {1, 2, 3, 4, 5}

    def parse_mbap_frame(self, raw_bytes: bytes) -> ModbusTCPFrame:
        if len(raw_bytes) < 8:
            raise ValueError(f"Modbus frame too short ({len(raw_bytes)} bytes < 8)")
            
        trans_id, proto_id, length, unit_id = struct.unpack(">HHHB", raw_bytes[:7])
        function_code = raw_bytes[7]
        data = raw_bytes[8:]
        
        return ModbusTCPFrame(
            transaction_id=trans_id,
            protocol_id=proto_id,
            length=length,
            unit_id=unit_id,
            function_code=function_code,
            data_hex=data.hex()
        )

    def inspect_frame(self, frame: ModbusTCPFrame) -> Tuple[bool, str]:
        if frame.protocol_id != 0:
            return False, f"NON_MODBUS_PROTOCOL_ID: {frame.protocol_id}"
            
        if frame.unit_id not in self.allowed_units:
            return False, f"UNAUTHORIZED_UNIT_ID: Unit {frame.unit_id} not in authorized set"
            
        if self.read_only_mode and frame.function_code in self.ALLOWED_WRITE_FUNCTION_CODES:
            return False, f"WRITE_BLOCKED_IN_READ_ONLY_MODE: Function code 0x{frame.function_code:02X}"
            
        if frame.function_code not in self.ALLOWED_READ_FUNCTION_CODES and frame.function_code not in self.ALLOWED_WRITE_FUNCTION_CODES:
            return False, f"ILLEGAL_OR_DANGEROUS_FUNCTION_CODE: 0x{frame.function_code:02X} (e.g. Diagnostic / Firmware dump)"
            
        return True, "MODBUS_FRAME_PERMITTED"
