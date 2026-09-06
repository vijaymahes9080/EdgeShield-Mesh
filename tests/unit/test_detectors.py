"""
Unit Tests for All 8 Deterministic Detectors & Statistical Baseline
"""
import pytest
from datetime import datetime, timezone, timedelta
from packages.shared.models import NormalizedTelemetry, Device, DeviceType, DeviceStatus
from services.detection_engine.detectors import DeterministicDetectors
from services.detection_engine.statistical import StatisticalBaselineEngine


@pytest.fixture
def detectors():
    return DeterministicDetectors()


@pytest.fixture
def sample_device():
    return Device(
        id="soil-sensor-01",
        name="Soil Moisture Alpha",
        device_type=DeviceType.SOIL_SENSOR,
        zone="zone_a_north_field",
        status=DeviceStatus.ACTIVE,
        firmware_version="1.2.0",
        expected_topics=["edgeshield/soil-sensor-01/telemetry", "edgeshield/soil-sensor-01/status"]
    )


# 1. Duplicate Message Detector
def test_detect_duplicate_message(detectors):
    t1 = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        payload_hash="hash_alpha_1234567890abcdef1234567890abcdef",
        measurements={"moisture": 35.0}
    )
    res1 = detectors.detect_duplicate_message(t1)
    assert res1 is None

    # Exact duplicate
    res2 = detectors.detect_duplicate_message(t1)
    assert res2 is not None
    assert res2.detector_id == "duplicate_message"
    assert res2.confidence >= 0.90


# 2. Timestamp Rollback Detector
def test_detect_timestamp_rollback(detectors):
    now = datetime.now(timezone.utc)
    t1 = NormalizedTelemetry(
        device_id="weather-station-01",
        device_type="weather_station",
        zone="zone_b_weather_tower",
        timestamp=now,
        seq=10,
        measurements={"temp": 20.0}
    )
    detectors.detect_timestamp_rollback(t1)

    # Rollback timestamp (1 hour in the past)
    t2_past = NormalizedTelemetry(
        device_id="weather-station-01",
        device_type="weather_station",
        zone="zone_b_weather_tower",
        timestamp=now - timedelta(hours=1),
        seq=11,
        measurements={"temp": 18.0}
    )
    res = detectors.detect_timestamp_rollback(t2_past)
    assert res is not None
    assert res.detector_id == "timestamp_rollback"


# 3. Burst Rate Detector
def test_detect_burst_rate(detectors):
    t = NormalizedTelemetry(
        device_id="burst-node-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        measurements={"moisture": 30.0}
    )
    # Send 15 messages in rapid succession
    last_res = None
    for _ in range(15):
        res = detectors.detect_burst_rate(t, max_rate_per_sec=10)
        if res:
            last_res = res

    assert last_res is not None
    assert last_res.detector_id == "burst_rate"


# 4. Impossible Value Detector
def test_detect_impossible_value(detectors):
    t_normal = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        measurements={"soil_moisture_pct": 45.0, "soil_temp_c": 22.0}
    )
    assert detectors.detect_impossible_value(t_normal) is None

    # Impossible: soil moisture 450%, temp 850°C
    t_spoofed = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        measurements={"soil_moisture_pct": 450.0, "soil_temp_c": 850.0}
    )
    res = detectors.detect_impossible_value(t_spoofed)
    assert res is not None
    assert res.detector_id == "impossible_value"


# 5. Device Silence Detector
def test_detect_device_silence(detectors, sample_device):
    now = datetime.now(timezone.utc)
    sample_device.last_seen = now - timedelta(seconds=10)
    sample_device.telemetry_interval_sec = 10

    # 10s is normal
    assert detectors.detect_device_silence(sample_device, now) is None

    # 45s (> 3x interval of 10s = 30s)
    sample_device.last_seen = now - timedelta(seconds=45)
    res = detectors.detect_device_silence(sample_device, now)
    assert res is not None
    assert res.detector_id == "device_silence"


# 6. Unauthorized Topic Detector
def test_detect_unauthorized_topic(detectors, sample_device):
    # Allowed topic
    assert detectors.detect_unauthorized_topic(sample_device, "edgeshield/soil-sensor-01/telemetry") is None

    # Rogue publish to valve actuator command topic
    res = detectors.detect_unauthorized_topic(sample_device, "edgeshield/valve-controller-01/cmd/state")
    assert res is not None
    assert res.detector_id == "unauthorized_topic"
    assert res.severity.value == "critical"


# 7. Firmware Age & CVE Risk Detector
def test_detect_firmware_age_risk(detectors, sample_device):
    sample_device.firmware_version = "1.2.0"
    sample_device.metadata = {}
    assert detectors.detect_firmware_age_risk(sample_device, min_version="1.0.0") is None

    # Vulnerable legacy firmware 0.9.1 with known CVE
    vulnerable_device = Device(
        id="greenhouse-env-01",
        name="Greenhouse Monitor",
        device_type=DeviceType.GREENHOUSE_MONITOR,
        zone="zone_d_greenhouse",
        firmware_version="0.9.1",
        metadata={"vulnerabilities": ["CVE-2024-IoT-9912"]}
    )
    res = detectors.detect_firmware_age_risk(vulnerable_device, min_version="1.0.0")
    assert res is not None
    assert res.detector_id == "firmware_age_risk"


# 8. Gateway Disconnect Detector
def test_detect_gateway_disconnect(detectors):
    now = datetime.now(timezone.utc)
    hb_good = now - timedelta(seconds=10)
    assert detectors.detect_gateway_disconnect("gw-01", hb_good, now, timeout_sec=45) is None

    hb_bad = now - timedelta(seconds=90)
    res = detectors.detect_gateway_disconnect("gw-01", hb_bad, now, timeout_sec=45)
    assert res is not None
    assert res.detector_id == "gateway_disconnect"


# Statistical Baseline Detector
def test_statistical_baseline_anomaly():
    stat_engine = StatisticalBaselineEngine(min_samples=5, z_score_threshold=3.0)
    
    # Train normal baseline around 30.0 with small variance
    for i in range(10):
        t = NormalizedTelemetry(
            device_id="soil-sensor-01",
            device_type="soil_sensor",
            zone="zone_a_north_field",
            measurements={"soil_moisture_pct": 30.0 + (i % 2) * 0.5}
        )
        stat_engine.update_and_detect(t)

    # Anomaly reading: 50.0 (far from mean 30.25)
    t_outlier = NormalizedTelemetry(
        device_id="soil-sensor-01",
        device_type="soil_sensor",
        zone="zone_a_north_field",
        measurements={"soil_moisture_pct": 55.0}
    )
    anomalies = stat_engine.update_and_detect(t_outlier)
    assert len(anomalies) > 0
    assert anomalies[0].detector_id == "statistical_drift"
