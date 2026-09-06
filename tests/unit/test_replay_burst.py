"""
Unit Tests for Replay, Nonce Reuse, and Rate Flooding
"""
import pytest
from datetime import datetime, timezone, timedelta
from packages.shared.models import NormalizedTelemetry
from services.ingestion.dedup_replay import DedupReplayTracker
from services.attack_simulator.manager import attack_manager


def test_nonce_reuse_detection():
    tracker = DedupReplayTracker()
    now = datetime.now(timezone.utc)
    t1 = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        nonce="nonce-secure-999",
        timestamp=now
    )
    is_replay1, _ = tracker.check_replay_and_rollback(t1)
    assert is_replay1 is False

    # Second packet reusing exact same nonce
    t2 = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        nonce="nonce-secure-999",
        timestamp=now + timedelta(seconds=1)
    )
    is_replay2, reason = tracker.check_replay_and_rollback(t2)
    assert is_replay2 is True
    assert "Reused cryptographic nonce" in reason


def test_attack_simulator_replay_generator():
    p1, p2 = attack_manager.generate_replay_attack("soil-sensor-01")
    assert p1.payload_raw == p2.payload_raw
    assert p1.topic == p2.topic
    assert p1.source_ip != p2.source_ip  # Injected from rogue source
