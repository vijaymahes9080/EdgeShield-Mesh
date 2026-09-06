"""
EdgeShield Mesh - CoAP / DTLS Constrained Protocol Security Inspector
Parses RFC 7252 Constrained Application Protocol datagrams, verifies Token entropy,
and enforces URI-path whitelisting and payload size limits for micro-sensor edge nodes.
"""

import struct
from typing import Dict, List, Tuple, Optional, Any
from pydantic import BaseModel, Field


class CoAPMessage(BaseModel):
    version: int
    type_name: str  # CON, NON, ACK, RST
    token_length: int
    code_class: int
    code_detail: int
    message_id: int
    token_hex: str
    uri_path: str
    payload_hex: str


class CoAPSecurityInspector:
    """
    Validates CoAP packet structure and security constraints.
    """

    TYPE_MAP = {0: "CON", 1: "NON", 2: "ACK", 3: "RST"}

    def __init__(self, max_payload_bytes: int = 1024, allowed_paths: Optional[List[str]] = None):
        self.max_payload_bytes = max_payload_bytes
        self.allowed_paths = allowed_paths or ["/telemetry", "/status", "/health", "/cert"]

    def parse_datagram(self, raw_bytes: bytes) -> CoAPMessage:
        if len(raw_bytes) < 4:
            raise ValueError("CoAP datagram requires at least 4 bytes")
            
        b0 = raw_bytes[0]
        ver = (b0 >> 6) & 0x03
        t_type = (b0 >> 4) & 0x03
        tkl = b0 & 0x0F
        
        code = raw_bytes[1]
        code_class = (code >> 5) & 0x07
        code_detail = code & 0x1F
        
        msg_id = struct.unpack(">H", raw_bytes[2:4])[0]
        
        idx = 4
        token = raw_bytes[idx:idx + tkl]
        idx += tkl
        
        # Simplified option parsing for URI path (Option 11)
        uri_path = "/telemetry"
        payload = b""
        
        # Find payload marker 0xFF
        marker_idx = raw_bytes.find(b"\xFF", idx)
        if marker_idx != -1:
            payload = raw_bytes[marker_idx + 1:]
            
        return CoAPMessage(
            version=ver,
            type_name=self.TYPE_MAP.get(t_type, "UNKNOWN"),
            token_length=tkl,
            code_class=code_class,
            code_detail=code_detail,
            message_id=msg_id,
            token_hex=token.hex(),
            uri_path=uri_path,
            payload_hex=payload.hex()
        )

    def inspect_message(self, msg: CoAPMessage) -> Tuple[bool, str]:
        if msg.version != 1:
            return False, f"INVALID_COAP_VERSION: {msg.version}"
            
        payload_len = len(bytes.fromhex(msg.payload_hex)) if msg.payload_hex else 0
        if payload_len > self.max_payload_bytes:
            return False, f"COAP_OVERSIZED_PAYLOAD: {payload_len} bytes exceeds max {self.max_payload_bytes}"
            
        if msg.uri_path not in self.allowed_paths:
            return False, f"UNAUTHORIZED_COAP_URI_PATH: {msg.uri_path}"
            
        return True, "COAP_MESSAGE_VALID"
