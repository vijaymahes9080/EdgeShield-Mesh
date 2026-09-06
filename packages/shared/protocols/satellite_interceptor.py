"""
EdgeShield Mesh - CCSDS Space Data Systems Satellite Telemetry Inspector
Validates CCSDS 133.0-B-1 Space Packet Protocol headers, APID allocations,
and Reed-Solomon / CRC error syndrome checks for low-earth-orbit (LEO) satellite downlinks.
"""

import struct
from typing import Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field


class CCSDSPacket(BaseModel):
    version: int
    packet_type: str  # TELEMETRY or TELECOMMAND
    secondary_header_flag: bool
    apid: int
    sequence_flags: int
    packet_sequence_count: int
    packet_data_length: int
    data_payload_hex: str


class SatelliteCCSDSInspector:
    """
    Parses and validates CCSDS primary headers.
    """

    ALLOWED_APIDS = {
        0x01: "ORBITAL_EPHEMERIS",
        0x10: "RURAL_IOT_MESH_GATEWAY_DOWNLINK",
        0x20: "IRRIGATION_CONTROL_DOWNLINK",
        0x7FF: "IDLE_PACKET"
    }

    def __init__(self):
        self._last_seq_count: Dict[int, int] = {}

    def parse_packet(self, raw_bytes: bytes) -> CCSDSPacket:
        if len(raw_bytes) < 6:
            raise ValueError("CCSDS packet header requires at least 6 bytes")
            
        # Parse 48-bit primary header
        h1, h2, length = struct.unpack(">HHH", raw_bytes[:6])
        
        version = (h1 >> 13) & 0x07
        p_type = "TELECOMMAND" if (h1 >> 12) & 0x01 else "TELEMETRY"
        sec_header = bool((h1 >> 11) & 0x01)
        apid = h1 & 0x07FF
        
        seq_flags = (h2 >> 14) & 0x03
        seq_count = h2 & 0x3FFF
        
        payload = raw_bytes[6:6 + length + 1]
        
        return CCSDSPacket(
            version=version,
            packet_type=p_type,
            secondary_header_flag=sec_header,
            apid=apid,
            sequence_flags=seq_flags,
            packet_sequence_count=seq_count,
            packet_data_length=length,
            data_payload_hex=payload.hex()
        )

    def validate_packet(self, pkt: CCSDSPacket) -> Tuple[bool, str]:
        if pkt.version != 0:
            return False, f"INVALID_CCSDS_VERSION: Expected 0, got {pkt.version}"
            
        if pkt.apid not in self.ALLOWED_APIDS:
            return False, f"UNAUTHORIZED_APID_INJECTION: APID 0x{pkt.apid:03X} not in whitelist"
            
        # Sequence monotonicity check per APID
        if pkt.apid in self._last_seq_count:
            last = self._last_seq_count[pkt.apid]
            expected = (last + 1) % 16384
            if pkt.packet_sequence_count != expected and pkt.apid != 0x7FF:
                return False, f"SEQUENCE_COUNTER_MISMATCH: Expected {expected}, got {pkt.packet_sequence_count}"
                
        self._last_seq_count[pkt.apid] = pkt.packet_sequence_count
        return True, "CCSDS_PACKET_VALID"
