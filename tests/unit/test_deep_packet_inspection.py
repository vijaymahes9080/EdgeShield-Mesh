"""
Unit tests for LoRaWAN, CCSDS Satellite, Modbus-TCP, and CoAP Deep Packet Inspection.
"""

import pytest
import struct
from packages.shared.protocols.lorawan_dpi import LoRaWANDPI
from packages.shared.protocols.satellite_interceptor import SatelliteCCSDSInspector
from packages.shared.protocols.modbus_tcp_guardian import ModbusTCPGuardian
from packages.shared.protocols.coap_dtls_inspector import CoAPSecurityInspector


def test_lorawan_dpi_and_anti_replay():
    dpi = LoRaWANDPI()
    
    # Construct a valid unconfirmed uplink frame (MType=2, Major=0)
    # DevAddr: 0x01020304, FCtrl: 0x00, FCnt: 1, FPort: 10, Payload: b"OK", MIC: b"\x11\x22\x33\x44"
    raw_frame_1 = bytes([0x40]) + struct.pack("<I", 0x01020304) + bytes([0x00]) + struct.pack("<H", 1) + bytes([10, 0x4F, 0x4B, 0x11, 0x22, 0x33, 0x44])
    
    frame1 = dpi.parse_phy_payload(raw_frame_1)
    valid1, msg1 = dpi.validate_frame(frame1)
    assert valid1 is True
    
    # Frame 2 with same FCnt (1) -> Replay attack blocked!
    frame2 = dpi.parse_phy_payload(raw_frame_1)
    valid2, msg2 = dpi.validate_frame(frame2)
    assert valid2 is False
    assert "REPLAY_ATTACK_DETECTED" in msg2


def test_satellite_ccsds_inspector():
    inspector = SatelliteCCSDSInspector()
    
    # Build CCSDS header: Version 0, Telemetry, APID 0x10, Seq 10, Length 4
    # h1: (0 << 13) | (0 << 12) | (0 << 11) | 0x10 = 0x0010
    # h2: (3 << 14) | 10 = 0xC00A
    # length: 3
    hdr = struct.pack(">HHH", 0x0010, 0xC00A, 3)
    payload = b"TEST"
    pkt_bytes = hdr + payload
    
    pkt = inspector.parse_packet(pkt_bytes)
    assert pkt.apid == 0x10
    assert pkt.packet_sequence_count == 10
    
    valid, msg = inspector.validate_packet(pkt)
    assert valid is True
    
    # Test unauthorized APID
    unauth_hdr = struct.pack(">HHH", 0x0555, 0xC00B, 3)
    pkt_unauth = inspector.parse_packet(unauth_hdr + payload)
    valid_u, msg_u = inspector.validate_packet(pkt_unauth)
    assert valid_u is False
    assert "UNAUTHORIZED_APID_INJECTION" in msg_u


def test_modbus_tcp_guardian():
    guardian = ModbusTCPGuardian(read_only_mode=True)
    
    # Modbus Read Holding Registers (Function Code 0x03)
    mb_read = struct.pack(">HHHB", 1, 0, 6, 1) + bytes([0x03, 0x00, 0x64, 0x00, 0x0A])
    frame_read = guardian.parse_mbap_frame(mb_read)
    valid_r, _ = guardian.inspect_frame(frame_read)
    assert valid_r is True
    
    # Modbus Write Single Coil (Function Code 0x05) in read_only_mode -> blocked!
    mb_write = struct.pack(">HHHB", 2, 0, 6, 1) + bytes([0x05, 0x00, 0x64, 0xFF, 0x00])
    frame_write = guardian.parse_mbap_frame(mb_write)
    valid_w, msg_w = guardian.inspect_frame(frame_write)
    assert valid_w is False
    assert "WRITE_BLOCKED_IN_READ_ONLY_MODE" in msg_w


def test_coap_security_inspector():
    inspector = CoAPSecurityInspector(max_payload_bytes=100)
    
    # CoAP GET /telemetry message
    coap_bytes = bytes([0x40, 0x01, 0x12, 0x34]) + b"\xFF" + b"sensor_data"
    msg = inspector.parse_datagram(coap_bytes)
    assert msg.type_name == "CON"
    assert msg.message_id == 0x1234
    
    valid, _ = inspector.inspect_message(msg)
    assert valid is True
