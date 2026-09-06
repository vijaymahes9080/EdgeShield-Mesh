"""
EdgeShield Mesh - Unified Detection Engine
Processes incoming telemetry, runs all active detectors, builds EvidenceItems,
and triggers Incident records.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from packages.shared.models import (
    NormalizedTelemetry, RawTelemetry, DetectorResult, Incident, EvidenceItem,
    IncidentSeverity, IncidentStatus, Device
)
from services.detection_engine.detectors import DeterministicDetectors
from services.detection_engine.statistical import StatisticalBaselineEngine


class DetectionEngine:
    def __init__(self):
        self.deterministic = DeterministicDetectors()
        self.statistical = StatisticalBaselineEngine()

    def evaluate_telemetry(
        self,
        telemetry: NormalizedTelemetry,
        device: Optional[Device] = None
    ) -> List[DetectorResult]:
        """
        Runs all detectors against an incoming telemetry event.
        """
        results: List[DetectorResult] = []

        # 1. Duplicate check
        r_dup = self.deterministic.detect_duplicate_message(telemetry)
        if r_dup:
            results.append(r_dup)

        # 2. Timestamp rollback check
        r_roll = self.deterministic.detect_timestamp_rollback(telemetry)
        if r_roll:
            results.append(r_roll)

        # 3. Burst rate check
        r_burst = self.deterministic.detect_burst_rate(telemetry)
        if r_burst:
            results.append(r_burst)

        # 4. Impossible values check
        r_imp = self.deterministic.detect_impossible_value(telemetry)
        if r_imp:
            results.append(r_imp)

        # 5. Device-specific checks (if device profile is known)
        if device:
            # Check firmware vulnerability
            r_fw = self.deterministic.detect_firmware_age_risk(device)
            if r_fw:
                results.append(r_fw)

        # 6. Statistical baseline checks
        r_stats = self.statistical.update_and_detect(telemetry)
        results.extend(r_stats)

        return results

    def check_unauthorized_publish(self, device: Device, topic: str) -> Optional[DetectorResult]:
        return self.deterministic.detect_unauthorized_topic(device, topic)

    def check_silence(self, device: Device, current_time: Optional[datetime] = None) -> Optional[DetectorResult]:
        if not current_time:
            current_time = datetime.now(timezone.utc)
        return self.deterministic.detect_device_silence(device, current_time)

    def check_gateway(self, gateway_id: str, last_heartbeat: datetime, current_time: Optional[datetime] = None) -> Optional[DetectorResult]:
        if not current_time:
            current_time = datetime.now(timezone.utc)
        return self.deterministic.detect_gateway_disconnect(gateway_id, last_heartbeat, current_time)


# Global detection engine instance
detection_engine = DetectionEngine()
