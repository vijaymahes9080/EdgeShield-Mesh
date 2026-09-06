"""
Sensor Metric Range and Physics Validator
Validates sensor metrics against absolute physical bounds and operating envelopes.
"""
from typing import Dict, Any, List, Tuple, Optional
from packages.shared.models import NormalizedTelemetry

DEFAULT_BOUNDS: Dict[str, Tuple[float, float]] = {
    # Soil & Agriculture
    "soil_moisture_pct": (0.0, 100.0),
    "soil_temp_c": (-20.0, 60.0),
    # Weather & Atmosphere
    "ambient_temp_c": (-40.0, 70.0),
    "temp_c": (-40.0, 70.0),
    "humidity_pct": (0.0, 100.0),
    "solar_irradiance_w_m2": (0.0, 1500.0),
    "wind_speed_mps": (0.0, 75.0),
    "rainfall_mm": (0.0, 500.0),
    "co2_ppm": (200.0, 10000.0),
    "light_lux": (0.0, 150000.0),
    # Actuators & Hydraulics
    "line_pressure_psi": (0.0, 150.0),
    "flow_rate_lpm": (0.0, 1000.0),
    # Power
    "pv_voltage_v": (0.0, 200.0),
    "pv_current_a": (0.0, 50.0),
    "pump_rpm": (0.0, 6000.0),
    "inverter_temp_c": (-20.0, 100.0),
    "battery_level": (0.0, 100.0),
    "signal_rssi": (-140.0, 0.0),
}


class SensorRangeChecker:
    def __init__(self, custom_bounds: Optional[Dict[str, Tuple[float, float]]] = None):
        self.bounds = DEFAULT_BOUNDS.copy()
        if custom_bounds:
            self.bounds.update(custom_bounds)

    def check_measurements(self, telemetry: NormalizedTelemetry) -> List[Tuple[str, float, float, float]]:
        """
        Returns list of violations: (metric_name, observed_value, min_bound, max_bound)
        """
        violations = []
        # Check direct measurements
        for metric, val in telemetry.measurements.items():
            if isinstance(val, (int, float)):
                if metric in self.bounds:
                    min_b, max_b = self.bounds[metric]
                    if val < min_b or val > max_b:
                        violations.append((metric, float(val), min_b, max_b))

        # Check battery level if present
        if telemetry.battery_level is not None:
            min_b, max_b = self.bounds["battery_level"]
            if telemetry.battery_level < min_b or telemetry.battery_level > max_b:
                violations.append(("battery_level", float(telemetry.battery_level), min_b, max_b))

        # Check RSSI if present
        if telemetry.signal_rssi is not None:
            min_b, max_b = self.bounds["signal_rssi"]
            if telemetry.signal_rssi < min_b or telemetry.signal_rssi > max_b:
                violations.append(("signal_rssi", float(telemetry.signal_rssi), min_b, max_b))

        return violations
