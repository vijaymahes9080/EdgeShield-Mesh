"""
Telemetry Ingestion Validator
Enforces maximum size (64KB), JSON syntax, timestamp normalization, and type boundaries.
"""
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from packages.shared.models import RawTelemetry, NormalizedTelemetry, TelemetryValidationResult

MAX_PAYLOAD_SIZE_BYTES = 64 * 1024  # 64 KB


class TelemetryValidator:
    def __init__(self, max_size_bytes: int = MAX_PAYLOAD_SIZE_BYTES):
        self.max_size_bytes = max_size_bytes

    def validate_and_normalize(self, raw: RawTelemetry) -> TelemetryValidationResult:
        errors = []

        # 1. Check size limit
        payload_bytes = raw.payload_raw.encode("utf-8")
        raw.byte_size = len(payload_bytes)
        if raw.byte_size > self.max_size_bytes:
            errors.append(f"Payload size {raw.byte_size} bytes exceeds limit of {self.max_size_bytes} bytes")
            return TelemetryValidationResult(is_valid=False, errors=errors)

        # 2. Parse JSON
        try:
            parsed = json.loads(raw.payload_raw)
            if not isinstance(parsed, dict):
                errors.append("Payload must be a valid JSON object")
                return TelemetryValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            errors.append(f"Invalid JSON payload: {str(e)}")
            return TelemetryValidationResult(is_valid=False, errors=errors)

        # 3. Extract required fields
        device_id = parsed.get("device_id")
        if not device_id or not isinstance(device_id, str):
            # Extract from topic if not in payload (e.g. edgeshield/{device_id}/telemetry)
            topic_parts = raw.topic.split("/")
            if len(topic_parts) >= 2 and topic_parts[0] == "edgeshield":
                device_id = topic_parts[1]
            else:
                errors.append("Missing required field 'device_id'")
                return TelemetryValidationResult(is_valid=False, errors=errors)

        device_type = parsed.get("device_type", "unknown")
        zone = parsed.get("zone", "unassigned")
        seq = parsed.get("seq", 0)
        nonce = str(parsed.get("nonce", ""))

        # 4. Timestamp normalization
        raw_ts = parsed.get("timestamp")
        normalized_ts = datetime.now(timezone.utc)
        if raw_ts:
            try:
                if isinstance(raw_ts, (int, float)):
                    normalized_ts = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
                elif isinstance(raw_ts, str):
                    normalized_ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except Exception:
                errors.append(f"Invalid timestamp format: {raw_ts}, defaulted to server time")

        # 5. Extract measurements & calculate hash
        measurements = parsed.get("measurements", {})
        if not measurements:
            # Check if top-level fields are measurements
            excluded = {"device_id", "device_type", "zone", "seq", "nonce", "timestamp", "battery_level", "signal_rssi"}
            measurements = {k: v for k, v in parsed.items() if k not in excluded}

        battery_level = parsed.get("battery_level")
        signal_rssi = parsed.get("signal_rssi")

        # Payload hash including sequence and measurements
        hasher = hashlib.sha256()
        hash_payload = {
            "device_id": device_id,
            "seq": seq,
            "nonce": nonce,
            "measurements": measurements
        }
        hasher.update(json.dumps(hash_payload, sort_keys=True).encode("utf-8"))
        payload_hash = hasher.hexdigest()

        normalized = NormalizedTelemetry(
            device_id=device_id,
            device_type=device_type,
            zone=zone,
            timestamp=normalized_ts,
            seq=int(seq) if isinstance(seq, (int, float)) else 0,
            nonce=nonce,
            payload_hash=payload_hash,
            battery_level=float(battery_level) if battery_level is not None else None,
            signal_rssi=int(signal_rssi) if signal_rssi is not None else None,
            measurements=measurements,
            is_valid=len(errors) == 0,
            validation_errors=errors,
            raw_id=raw.raw_id
        )

        return TelemetryValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            normalized=normalized
        )
