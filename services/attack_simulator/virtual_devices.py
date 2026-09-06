"""
Simulated Smart Agriculture IoT Device Telemetry Generator
Generates realistic environmental curves (solar cycle, soil moisture dissipation, pump cycling)
for the 5 virtual agricultural devices.
"""
import math
import time
import uuid
import json
import random
from datetime import datetime, timezone
from typing import Dict, Any, List
from packages.shared.models import RawTelemetry, NormalizedTelemetry


class SmartAgDeviceSimulator:
    def __init__(self):
        self.seq_counters: Dict[str, int] = {
            "soil-sensor-01": 100,
            "weather-station-01": 100,
            "valve-controller-01": 100,
            "solar-pump-01": 100,
            "greenhouse-env-01": 100
        }
        self.base_soil_moisture = 42.5
        self.base_temp = 24.0

    def generate_telemetry_for_device(self, device_id: str, timestamp: datetime = None) -> NormalizedTelemetry:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        seq = self.seq_counters.get(device_id, 1)
        self.seq_counters[device_id] = seq + 1
        nonce = uuid.uuid4().hex[:12]

        # Diurnal fluctuation based on hour of day
        hour = timestamp.hour + timestamp.minute / 60.0
        sun_factor = max(0.0, math.sin(math.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0.0

        measurements: Dict[str, Any] = {}
        battery_level = 95.0 - (seq * 0.001) % 15.0
        rssi = -65 + random.randint(-5, 5)

        if device_id == "soil-sensor-01":
            # Soil moisture slowly dries down, soil temp follows ambient dampened
            self.base_soil_moisture = max(20.0, self.base_soil_moisture - 0.02 + random.uniform(-0.1, 0.1))
            measurements = {
                "soil_moisture_pct": round(self.base_soil_moisture, 2),
                "soil_temp_c": round(18.0 + (sun_factor * 8.0) + random.uniform(-0.2, 0.2), 2)
            }
            dev_type = "soil_sensor"
            zone = "zone_a_north_field"

        elif device_id == "weather-station-01":
            measurements = {
                "ambient_temp_c": round(15.0 + (sun_factor * 15.0) + random.uniform(-0.5, 0.5), 2),
                "humidity_pct": round(80.0 - (sun_factor * 40.0) + random.uniform(-2.0, 2.0), 2),
                "solar_irradiance_w_m2": round(sun_factor * 1100.0 + random.uniform(-10.0, 10.0), 1),
                "wind_speed_mps": round(2.5 + (random.random() * 4.0), 2),
                "rainfall_mm": 0.0
            }
            dev_type = "weather_station"
            zone = "zone_b_weather_tower"

        elif device_id == "valve-controller-01":
            is_open = sun_factor > 0.4 and self.base_soil_moisture < 35.0
            measurements = {
                "valve_state": "OPEN" if is_open else "CLOSED",
                "line_pressure_psi": round(45.0 + (10.0 * random.random()) if is_open else 65.0, 2),
                "flow_rate_lpm": round(120.0 + (15.0 * random.random()) if is_open else 0.0, 2)
            }
            dev_type = "valve_controller"
            zone = "zone_a_irrigation"

        elif device_id == "solar-pump-01":
            pv_v = round(sun_factor * 85.0 + random.uniform(-1.0, 1.0), 2)
            pv_a = round(sun_factor * 18.0 + random.uniform(-0.5, 0.5), 2)
            rpm = round(sun_factor * 3200.0)
            measurements = {
                "pv_voltage_v": pv_v,
                "pv_current_a": pv_a,
                "pump_rpm": rpm,
                "inverter_temp_c": round(25.0 + (sun_factor * 30.0), 1)
            }
            dev_type = "power_subsystem"
            zone = "zone_c_solar_array"

        elif device_id == "greenhouse-env-01":
            measurements = {
                "co2_ppm": round(750.0 + (sun_factor * 400.0) + random.uniform(-20, 20), 1),
                "humidity_pct": round(65.0 + random.uniform(-3, 3), 1),
                "temp_c": round(22.0 + (sun_factor * 10.0), 1),
                "light_lux": round(sun_factor * 45000.0, 0)
            }
            dev_type = "greenhouse_monitor"
            zone = "zone_d_greenhouse"

        else:
            measurements = {"status": "ok"}
            dev_type = "generic_sensor"
            zone = "general_field"

        return NormalizedTelemetry(
            device_id=device_id,
            device_type=dev_type,
            zone=zone,
            timestamp=timestamp,
            seq=seq,
            nonce=nonce,
            battery_level=round(battery_level, 1),
            signal_rssi=rssi,
            measurements=measurements,
            is_valid=True
        )


# Global smart ag generator
ag_simulator = SmartAgDeviceSimulator()
