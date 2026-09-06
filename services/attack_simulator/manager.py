"""
EdgeShield Mesh - Attack Simulator Manager
Provides safe, local-only reproducible generators for 7 IoT attack vectors:
1. Replay Attack
2. Burst Publish Flood
3. Invalid Payload Injection
4. Unauthorized Topic Access
5. Timestamp Rollback
6. Sensor Spoofing (Impossible Values)
7. Gateway Disconnect & Device Silence
"""
import uuid
import time
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple
from packages.shared.models import RawTelemetry, NormalizedTelemetry, Device
from services.attack_simulator.virtual_devices import ag_simulator


class AttackSimulatorManager:
    def __init__(self):
        self.active_attacks: List[Dict[str, Any]] = []

    # 1. Replay Attack
    def generate_replay_attack(self, target_device: str = "soil-sensor-01") -> Tuple[RawTelemetry, RawTelemetry]:
        """
        Produces an initial valid packet, followed immediately by an identical replay packet.
        """
        norm1 = ag_simulator.generate_telemetry_for_device(target_device)
        raw_payload = json.dumps({
            "device_id": norm1.device_id,
            "device_type": norm1.device_type,
            "zone": norm1.zone,
            "seq": norm1.seq,
            "nonce": norm1.nonce,
            "timestamp": norm1.timestamp.isoformat(),
            "measurements": norm1.measurements
        })

        packet1 = RawTelemetry(
            topic=f"edgeshield/{target_device}/telemetry",
            payload_raw=raw_payload,
            source_ip="192.168.10.101"
        )
        packet2_replayed = RawTelemetry(
            topic=f"edgeshield/{target_device}/telemetry",
            payload_raw=raw_payload,  # Exact duplicate payload and nonce
            source_ip="192.168.10.254"  # Rogue injector IP
        )
        return packet1, packet2_replayed

    # 2. Burst Publish Flood
    def generate_burst_flood(self, target_device: str = "soil-sensor-01", count: int = 20) -> List[RawTelemetry]:
        packets = []
        for i in range(count):
            norm = ag_simulator.generate_telemetry_for_device(target_device)
            raw = RawTelemetry(
                topic=f"edgeshield/{target_device}/telemetry",
                payload_raw=json.dumps({
                    "device_id": target_device,
                    "seq": 9000 + i,
                    "nonce": f"burst-{i}",
                    "measurements": norm.measurements,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                source_ip="192.168.10.101"
            )
            packets.append(raw)
        return packets

    # 3. Invalid Payload Injection
    def generate_invalid_payload(self, target_device: str = "greenhouse-env-01") -> RawTelemetry:
        corrupted_payload = "CORRUPTED_HEX_BYTESTREAM_0xFF_0x00_{'device_id':'greenhouse-env-01', unclosed_json"
        return RawTelemetry(
            topic=f"edgeshield/{target_device}/telemetry",
            payload_raw=corrupted_payload,
            source_ip="192.168.10.105"
        )

    # 4. Unauthorized Topic Access
    def generate_unauthorized_topic_attack(self) -> Tuple[Device, str, RawTelemetry]:
        """
        Soil probe attempts to publish actuator control commands to valve controller topic.
        """
        attacker_device = Device(
            id="soil-sensor-01",
            name="Soil Moisture Alpha",
            device_type="soil_sensor",
            zone="zone_a_north_field",
            expected_topics=["edgeshield/soil-sensor-01/telemetry", "edgeshield/soil-sensor-01/status"]
        )
        rogue_topic = "edgeshield/valve-controller-01/cmd/state"
        raw = RawTelemetry(
            topic=rogue_topic,
            payload_raw=json.dumps({
                "command": "FORCE_VALVE_OPEN",
                "duration_minutes": 120,
                "attacker_signature": "MALICIOUS_OVERRIDE"
            }),
            source_ip="192.168.10.101"
        )
        return attacker_device, rogue_topic, raw

    # 5. Timestamp Rollback Attack
    def generate_timestamp_rollback(self, target_device: str = "weather-station-01") -> RawTelemetry:
        past_ts = datetime.now(timezone.utc) - timedelta(hours=4)
        raw = RawTelemetry(
            topic=f"edgeshield/{target_device}/telemetry",
            payload_raw=json.dumps({
                "device_id": target_device,
                "device_type": "weather_station",
                "zone": "zone_b_weather_tower",
                "seq": 12,
                "nonce": "old-nonce-12",
                "timestamp": past_ts.isoformat(),
                "measurements": {
                    "ambient_temp_c": 12.0,
                    "humidity_pct": 95.0
                }
            }),
            source_ip="192.168.10.102"
        )
        return raw

    # 6. Sensor Spoofing (Physically Impossible Values)
    def generate_sensor_spoofing(self, target_device: str = "soil-sensor-01") -> RawTelemetry:
        raw = RawTelemetry(
            topic=f"edgeshield/{target_device}/telemetry",
            payload_raw=json.dumps({
                "device_id": target_device,
                "device_type": "soil_sensor",
                "zone": "zone_a_north_field",
                "seq": 555,
                "nonce": uuid.uuid4().hex[:8],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "measurements": {
                    "soil_moisture_pct": 450.0,  # Physically impossible (>100%)
                    "soil_temp_c": 850.0        # Impossible soil temp
                }
            }),
            source_ip="192.168.10.101"
        )
        return raw

    # 7. Gateway Disconnect & Unannounced Device Silence
    def generate_gateway_disconnect(self, gateway_id: str = "gw-field-alpha") -> Tuple[str, datetime, datetime]:
        last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=120)
        current_time = datetime.now(timezone.utc)
        return gateway_id, last_heartbeat, current_time


# Global attack simulator
attack_manager = AttackSimulatorManager()
