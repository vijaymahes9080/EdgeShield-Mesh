"""
Unit tests for Dynamic Honeypot, Tarpit Controller, Canary Tokens, and MITRE ICS Profiler.
"""

import pytest
import time
from services.deception_engine.dynamic_honeypot import DynamicHoneypotTwin
from services.deception_engine.tarpit_controller import AdaptiveTarpitController
from services.deception_engine.canary_tokens import CanaryTokenManager
from services.deception_engine.attacker_profiler import ICSAttackerProfiler


def test_dynamic_honeypot_trap():
    twin = DynamicHoneypotTwin("honeypot-plc-01")
    
    twin.handle_modbus_read("192.168.1.105", 40001)
    twin.handle_modbus_write("192.168.1.105", 40002, 9999)
    
    logs = twin.get_trapped_interactions()
    assert len(logs) == 2
    assert logs[1].command_executed == "WRITE_HOLDING_REG_40002"
    assert "9999" in logs[1].captured_payload


def test_tarpit_controller():
    tarpit = AdaptiveTarpitController(default_delay_ms=200, max_tarpit_duration=10.0)
    
    session = tarpit.trap_ip("10.0.0.99", severity_multiplier=2.0)
    assert session.delay_ms_per_byte == 400
    assert session.is_active is True
    
    delay = tarpit.stream_byte_chunk("10.0.0.99", chunk_size=5)
    assert delay == 2000
    assert session.bytes_sent == 5


def test_canary_tokens():
    mgr = CanaryTokenManager(master_secret=b"canary_secret_key_123")
    token = mgr.generate_token("API_KEY", "firmware/config.json")
    
    # Non-canary string does not trigger
    res1 = mgr.check_access_and_trip("normal_jwt_token", "192.168.1.50", "GET /api/v1/status")
    assert res1 is None
    
    # Canary string triggers alert
    alert = mgr.check_access_and_trip(token.token_secret, "192.168.1.50", "GET /api/v1/sensors")
    assert alert is not None
    assert alert.token_id == token.token_id
    assert alert.injected_location == "firmware/config.json"


def test_mitre_ics_profiler():
    profiler = ICSAttackerProfiler()
    
    profile = profiler.record_adversary_event("192.168.1.200", "MODBUS_UNAUTHORIZED_WRITE")
    assert "Impair Process Control" in profile.identified_tactics
    assert len(profile.mapped_techniques) == 1
    assert profile.mapped_techniques[0].technique_id == "T0855"
    
    # Record second event
    profile = profiler.record_adversary_event("192.168.1.200", "CANARY_TOKEN_TRIPPED")
    assert "Initial Access" in profile.identified_tactics
    assert profile.threat_score >= 40.0
