"""
EdgeShield Mesh - Edge Gateway and ACL Controller
Manages topic permissions, validates device identities, and drops rogue packets at the edge.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from packages.shared.models import Device, TopicPermission, RawTelemetry, NormalizedTelemetry
from services.ingestion.validator import TelemetryValidator
from services.detection_engine.engine import detection_engine


class EdgeGateway:
    def __init__(self, gateway_id: str = "gw-field-alpha"):
        self.gateway_id = gateway_id
        self.validator = TelemetryValidator()
        self.last_heartbeat = datetime.now(timezone.utc)
        self.is_online = True

    def process_incoming_raw_packet(
        self,
        raw_packet: RawTelemetry,
        device: Optional[Device] = None
    ) -> Tuple[Optional[NormalizedTelemetry], List[str]]:
        """
        Validates ACL permissions, parses payload, and checks edge rules.
        Returns (normalized_telemetry_or_none, list_of_errors_or_anomalies)
        """
        self.last_heartbeat = datetime.now(timezone.utc)
        errors = []

        # 1. Edge ACL check if device is registered
        if device:
            unauthorized_res = detection_engine.check_unauthorized_publish(device, raw_packet.topic)
            if unauthorized_res:
                errors.append(f"ACL VIOLATION: Device {device.id} is not permitted to publish to {raw_packet.topic}")
                return None, errors

        # 2. Schema and size validation
        val_result = self.validator.validate_and_normalize(raw_packet)
        if not val_result.is_valid:
            return None, val_result.errors

        return val_result.normalized, []


# Global edge gateway
edge_gateway = EdgeGateway()
