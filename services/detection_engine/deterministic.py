"""
EdgeShield Mesh - 8 Deterministic Anomaly Detectors
Each detector outputs:
- detector_id
- severity
- confidence
- observed_fields
- explanation
- evidence_ids
- recommended_next_step
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from packages.shared.models import (
    NormalizedTelemetry, RawTelemetry, DetectorResult, IncidentSeverity, Device, DeviceStatus
)
from services.ingestion.dedup_replay import DedupReplayTracker
from services.ingestion.range_checker import SensorRangeChecker


class DeterministicDetectors:
    def __init__(self):
        self.dedup_tracker = DedupReplayTracker()
        self.range_checker = SensorRangeChecker()
        self.publish_counts: Dict[str, List[datetime]] = {}  # device_id -> list of timestamps
        self.gateway_heartbeats: Dict[str, datetime] = {}

    # 1. Duplicate Message Detector
    def detect_duplicate_message(self, telemetry: NormalizedTelemetry) -> Optional[DetectorResult]:
        is_dup, reason = self.dedup_tracker.check_duplicate(telemetry)
        if is_dup:
            return DetectorResult(
                detector_id="duplicate_message",
                severity=IncidentSeverity.MEDIUM,
                confidence=0.95,
                device_id=telemetry.device_id,
                observed_fields={
                    "payload_hash": telemetry.payload_hash,
                    "seq": telemetry.seq,
                    "measurements": telemetry.measurements
                },
                explanation=f"Duplicate payload detected for device {telemetry.device_id}: {reason}",
                evidence_ids=[f"ev-dup-{telemetry.event_id[:8]}"],
                recommended_next_step="Inspect sensor firmware for replay or transmission retry storm."
            )
        return None

    # 2. Timestamp Rollback Detector
    def detect_timestamp_rollback(self, telemetry: NormalizedTelemetry) -> Optional[DetectorResult]:
        is_rollback, reason = self.dedup_tracker.check_replay_and_rollback(telemetry)
        if is_rollback:
            return DetectorResult(
                detector_id="timestamp_rollback",
                severity=IncidentSeverity.HIGH,
                confidence=0.98,
                device_id=telemetry.device_id,
                observed_fields={
                    "incoming_timestamp": telemetry.timestamp.isoformat(),
                    "seq": telemetry.seq,
                    "nonce": telemetry.nonce
                },
                explanation=f"Timestamp rollback or nonce replay anomaly detected: {reason}",
                evidence_ids=[f"ev-rollback-{telemetry.event_id[:8]}"],
                recommended_next_step="Verify device NTP sync or quarantine device if key reuse is suspected."
            )
        return None

    # 3. Burst Rate Detector
    def detect_burst_rate(self, telemetry: NormalizedTelemetry, max_rate_per_sec: int = 10) -> Optional[DetectorResult]:
        now = datetime.now(timezone.utc)
        dev_id = telemetry.device_id

        if dev_id not in self.publish_counts:
            self.publish_counts[dev_id] = []

        # Sliding window 1 second
        self.publish_counts[dev_id] = [t for t in self.publish_counts[dev_id] if (now - t).total_seconds() <= 1.0]
        self.publish_counts[dev_id].append(now)

        current_rate = len(self.publish_counts[dev_id])
        if current_rate > max_rate_per_sec:
            return DetectorResult(
                detector_id="burst_rate",
                severity=IncidentSeverity.HIGH,
                confidence=0.92,
                device_id=telemetry.device_id,
                observed_fields={
                    "observed_rate_msg_per_sec": current_rate,
                    "threshold_rate": max_rate_per_sec
                },
                explanation=f"Burst rate flood detected: device {dev_id} published {current_rate} msgs/sec exceeding limit of {max_rate_per_sec} msgs/sec.",
                evidence_ids=[f"ev-burst-{telemetry.event_id[:8]}"],
                recommended_next_step="Propose rate-limiting the device at the edge gateway."
            )
        return None

    # 4. Impossible Value Detector
    def detect_impossible_value(self, telemetry: NormalizedTelemetry) -> Optional[DetectorResult]:
        violations = self.range_checker.check_measurements(telemetry)
        if violations:
            violation_details = [
                f"{metric}={val} (allowed: [{min_b}, {max_b}])" for metric, val, min_b, max_b in violations
            ]
            return DetectorResult(
                detector_id="impossible_value",
                severity=IncidentSeverity.HIGH,
                confidence=0.99,
                device_id=telemetry.device_id,
                observed_fields={
                    "violations": violation_details,
                    "measurements": telemetry.measurements
                },
                explanation=f"Physically impossible telemetry values observed on {telemetry.device_id}: {', '.join(violation_details)}",
                evidence_ids=[f"ev-phys-{telemetry.event_id[:8]}"],
                recommended_next_step="Inspect physical sensor probe and recalibrate or isolate actuator inputs."
            )
        return None

    # 5. Device Silence Detector
    def detect_device_silence(self, device: Device, current_time: datetime) -> Optional[DetectorResult]:
        expected_interval = device.telemetry_interval_sec
        silence_threshold = expected_interval * 3
        silence_duration = (current_time - device.last_seen).total_seconds()

        if silence_duration > silence_threshold and device.status == DeviceStatus.ACTIVE:
            return DetectorResult(
                detector_id="device_silence",
                severity=IncidentSeverity.MEDIUM,
                confidence=0.88,
                device_id=device.id,
                observed_fields={
                    "last_seen": device.last_seen.isoformat(),
                    "silence_duration_sec": round(silence_duration, 1),
                    "expected_interval_sec": expected_interval,
                    "threshold_sec": silence_threshold
                },
                explanation=f"Device {device.id} has been silent for {silence_duration:.1f}s (threshold {silence_threshold}s).",
                evidence_ids=[f"ev-silence-{device.id}"],
                recommended_next_step="Check device battery level, radio path, or edge gateway connectivity."
            )
        return None

    # 6. Unauthorized Topic Detector
    def detect_unauthorized_topic(self, device: Device, published_topic: str) -> Optional[DetectorResult]:
        # If device has expected topics and published topic is not in or matching expected
        is_allowed = False
        for expected in device.expected_topics:
            if expected.endswith("#") or expected.endswith("+"):
                # Wildcard pattern match
                prefix = expected.split("+")[0].split("#")[0]
                if published_topic.startswith(prefix):
                    is_allowed = True
                    break
            elif expected == published_topic:
                is_allowed = True
                break

        if not is_allowed and device.expected_topics:
            return DetectorResult(
                detector_id="unauthorized_topic",
                severity=IncidentSeverity.CRITICAL,
                confidence=1.0,
                device_id=device.id,
                observed_fields={
                    "published_topic": published_topic,
                    "expected_topics": device.expected_topics,
                    "device_type": device.device_type.value
                },
                explanation=f"Device {device.id} published to unauthorized topic '{published_topic}'. Expected topics: {device.expected_topics}",
                evidence_ids=[f"ev-acl-{device.id}"],
                recommended_next_step="Propose immediate ACL revocation or device isolation."
            )
        return None

    # 7. Firmware Age and CVE Risk Detector
    def detect_firmware_age_risk(self, device: Device, min_version: str = "1.0.0") -> Optional[DetectorResult]:
        # Compare semantic version
        fw = device.firmware_version.strip()
        is_vulnerable = False
        known_cves = device.metadata.get("vulnerabilities", [])

        # Check if version < min_version
        try:
            parts = [int(p) for p in fw.replace("v", "").split(".")]
            min_parts = [int(p) for p in min_version.split(".")]
            if parts < min_parts:
                is_vulnerable = True
        except Exception:
            is_vulnerable = True

        if is_vulnerable or known_cves:
            return DetectorResult(
                detector_id="firmware_age_risk",
                severity=IncidentSeverity.HIGH,
                confidence=0.95,
                device_id=device.id,
                observed_fields={
                    "current_firmware": fw,
                    "min_required_firmware": min_version,
                    "known_cves": known_cves
                },
                explanation=f"Device {device.id} is running deprecated/vulnerable firmware ({fw} < {min_version}). Known CVEs: {known_cves}",
                evidence_ids=[f"ev-fw-{device.id}"],
                recommended_next_step="Propose scheduling an Over-The-Air (OTA) firmware upgrade with operator approval."
            )
        return None

    # 8. Gateway Disconnect Detector
    def detect_gateway_disconnect(self, gateway_id: str, last_heartbeat: datetime, current_time: datetime, timeout_sec: int = 45) -> Optional[DetectorResult]:
        gap = (current_time - last_heartbeat).total_seconds()
        if gap > timeout_sec:
            return DetectorResult(
                detector_id="gateway_disconnect",
                severity=IncidentSeverity.CRITICAL,
                confidence=0.96,
                device_id=gateway_id,
                observed_fields={
                    "gateway_id": gateway_id,
                    "last_heartbeat": last_heartbeat.isoformat(),
                    "gap_sec": round(gap, 1),
                    "timeout_sec": timeout_sec
                },
                explanation=f"Edge Gateway {gateway_id} lost connection. No heartbeat for {gap:.1f}s (limit {timeout_sec}s).",
                evidence_ids=[f"ev-gw-{gateway_id}"],
                recommended_next_step="Check field backhaul cellular/LoRa gateway connection."
            )
        return None
