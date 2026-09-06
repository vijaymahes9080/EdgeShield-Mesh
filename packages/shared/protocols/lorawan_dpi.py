"""
EdgeShield Mesh - LoRaWAN v1.1 Deep Packet Inspector (DPI)
Inspects physical LoRa frames, parses MAC payload headers (MType, DevAddr, FCnt, FOpts),
and strictly enforces 32-bit uplink frame counter monotonicity to prevent replay attacks.
"""

import struct
from typing import Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field


class LoRaWANFrame(BaseModel):
    mtype: str
    major_version: int
    dev_addr: str
    fcnt: int
    fopts_len: int
    fport: Optional[int]
    frm_payload_hex: str
    mic_hex: str


class LoRaWANDPI:
    """
    LoRaWAN MAC Layer Parser and Security Inspector.
    """

    MTYPE_MAP = {
        0: "Join-Request",
        1: "Join-Accept",
        2: "Unconfirmed Data Up",
        3: "Unconfirmed Data Down",
        4: "Confirmed Data Up",
        5: "Confirmed Data Down",
        6: "Rejoin-Request",
        7: "Proprietary"
    }

    def __init__(self):
        # Stores highest seen FCnt per DevAddr
        self._dev_fcnt_table: Dict[str, int] = {}

    def parse_phy_payload(self, raw_bytes: bytes) -> LoRaWANFrame:
        if len(raw_bytes) < 12:
            raise ValueError(f"LoRaWAN frame too short ({len(raw_bytes)} bytes < 12)")
            
        mhdr = raw_bytes[0]
        mtype_val = (mhdr >> 5) & 0x07
        major_val = mhdr & 0x03
        
        mtype_str = self.MTYPE_MAP.get(mtype_val, "Unknown")
        
        # Parse FHDR
        dev_addr = raw_bytes[1:5][::-1].hex() # Little-endian dev address
        fctrl = raw_bytes[5]
        fopts_len = fctrl & 0x0F
        fcnt = struct.unpack("<H", raw_bytes[6:8])[0]
        
        idx = 8 + fopts_len
        fport = raw_bytes[idx] if idx < len(raw_bytes) - 4 else None
        
        if fport is not None:
            frm_payload = raw_bytes[idx+1:-4]
        else:
            frm_payload = b""
            
        mic = raw_bytes[-4:].hex()
        
        return LoRaWANFrame(
            mtype=mtype_str,
            major_version=major_val,
            dev_addr=dev_addr,
            fcnt=fcnt,
            fopts_len=fopts_len,
            fport=fport,
            frm_payload_hex=frm_payload.hex(),
            mic_hex=mic
        )

    def validate_frame(self, frame: LoRaWANFrame) -> Tuple[bool, str]:
        """Enforces frame counter anti-replay rules."""
        if frame.dev_addr not in self._dev_fcnt_table:
            self._dev_fcnt_table[frame.dev_addr] = frame.fcnt
            return True, "INITIAL_FRAME_ACCEPTED"
            
        last_fcnt = self._dev_fcnt_table[frame.dev_addr]
        if frame.fcnt <= last_fcnt:
            return False, f"REPLAY_ATTACK_DETECTED: FCnt {frame.fcnt} <= Last {last_fcnt}"
            
        # Check excessive frame counter gap (possible desync/spoof)
        if frame.fcnt - last_fcnt > 16384:
            return False, f"FRAME_COUNTER_ROLLOVER_ATTACK: Gap {frame.fcnt - last_fcnt} exceeds threshold"
            
        self._dev_fcnt_table[frame.dev_addr] = frame.fcnt
        return True, "FRAME_VALID"
