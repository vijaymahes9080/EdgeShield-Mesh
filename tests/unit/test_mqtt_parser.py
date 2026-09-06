"""
Unit Tests for Telemetry Ingestion and Validation
"""
import json
import pytest
from packages.shared.models import RawTelemetry
from services.ingestion.validator import TelemetryValidator, MAX_PAYLOAD_SIZE_BYTES


def test_valid_telemetry_payload():
    validator = TelemetryValidator()
    payload = json.dumps({
        "device_id": "soil-sensor-01",
        "device_type": "soil_sensor",
        "zone": "zone_a_north_field",
        "seq": 101,
        "nonce": "n101abc",
        "measurements": {
            "soil_moisture_pct": 34.5,
            "soil_temp_c": 22.1
        },
        "battery_level": 94.0,
        "signal_rssi": -65
    })
    raw = RawTelemetry(
        topic="edgeshield/soil-sensor-01/telemetry",
        payload_raw=payload
    )
    res = validator.validate_and_normalize(raw)
    assert res.is_valid is True
    assert res.normalized is not None
    assert res.normalized.device_id == "soil-sensor-01"
    assert res.normalized.measurements["soil_moisture_pct"] == 34.5
    assert len(res.normalized.payload_hash) == 64


def test_oversized_payload_rejected():
    validator = TelemetryValidator(max_size_bytes=100)
    huge_payload = json.dumps({"device_id": "soil-sensor-01", "junk": "A" * 200})
    raw = RawTelemetry(
        topic="edgeshield/soil-sensor-01/telemetry",
        payload_raw=huge_payload
    )
    res = validator.validate_and_normalize(raw)
    assert res.is_valid is False
    assert any("exceeds limit" in err for err in res.errors)


def test_malformed_json_rejected():
    validator = TelemetryValidator()
    raw = RawTelemetry(
        topic="edgeshield/soil-sensor-01/telemetry",
        payload_raw="INVALID_JSON_STREAM_<<<"
    )
    res = validator.validate_and_normalize(raw)
    assert res.is_valid is False
    assert any("Invalid JSON" in err for err in res.errors)


def test_device_id_extracted_from_topic_if_missing_in_body():
    validator = TelemetryValidator()
    payload = json.dumps({
        "measurements": {"temp_c": 25.0}
    })
    raw = RawTelemetry(
        topic="edgeshield/weather-station-01/telemetry",
        payload_raw=payload
    )
    res = validator.validate_and_normalize(raw)
    assert res.is_valid is True
    assert res.normalized.device_id == "weather-station-01"
