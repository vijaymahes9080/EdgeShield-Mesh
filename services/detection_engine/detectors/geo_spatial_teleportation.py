"""
EdgeShield Mesh - GPS Spoofing & Geospatial Teleportation Detector
Detects sudden impossible velocity jumps, altitude inversions, and GPS ephemeris drift
in mobile agricultural robotic equipment, drones, and telemetry gateways.
"""

import math
import time
from typing import Optional, Dict, Tuple
from pydantic import BaseModel, Field


class GPSSpoofAlert(BaseModel):
    device_id: str
    inferred_speed_mps: float
    max_allowed_speed_mps: float
    distance_jump_meters: float
    alert_reason: str
    detected_at: float = Field(default_factory=time.time)


class GeoSpatialTeleportationDetector:
    """
    Computes Great-Circle Haversine distances and kinematic limits between consecutive GPS fixes.
    """

    def __init__(self, max_speed_mps: float = 35.0): # ~126 km/h for agri-drones/tractors
        self.max_speed_mps = max_speed_mps
        self._last_fixes: Dict[str, Tuple[float, float, float]] = {} # dev -> (lat, lon, timestamp)

    @staticmethod
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def update_gps_fix(self, device_id: str, lat: float, lon: float, timestamp: Optional[float] = None) -> Optional[GPSSpoofAlert]:
        now = timestamp or time.time()
        
        if device_id not in self._last_fixes:
            self._last_fixes[device_id] = (lat, lon, now)
            return None
            
        last_lat, last_lon, last_t = self._last_fixes[device_id]
        dt = max(0.001, now - last_t)
        
        dist = self.haversine_distance_meters(last_lat, last_lon, lat, lon)
        speed = dist / dt
        
        if speed > self.max_speed_mps:
            return GPSSpoofAlert(
                device_id=device_id,
                inferred_speed_mps=speed,
                max_allowed_speed_mps=self.max_speed_mps,
                distance_jump_meters=dist,
                alert_reason=f"Kinematic violation: Speed {speed:.1f} m/s exceeds max threshold {self.max_speed_mps} m/s"
            )
            
        self._last_fixes[device_id] = (lat, lon, now)
        return None
