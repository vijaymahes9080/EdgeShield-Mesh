"""
EdgeShield Mesh - Multi-Modal Optical & Thermal Vision Analyzer
Inspects edge enclosure security camera feeds, thermal infrared gradients, and QR seal integrity
to detect physical tampering, lock drilling, or enclosure pry attempts on remote IoT gateways.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import time


class VisionTamperAnalysis(BaseModel):
    enclosure_id: str
    is_physical_tamper_detected: bool
    optical_anomaly_type: Optional[str] = None
    thermal_hotspot_delta_c: float = 0.0
    qr_tamper_seal_valid: bool = True
    confidence: float
    recommended_action: str
    analyzed_at: float = Field(default_factory=time.time)


class MultiModalVisionAnalyzer:
    """
    Evaluates simulated optical and thermal camera frames from IoT enclosure micro-sensors.
    """

    @staticmethod
    def analyze_enclosure_frame(enclosure_id: str, optical_lux: float, thermal_delta_c: float, seal_intact: bool) -> VisionTamperAnalysis:
        is_tampered = False
        anomaly = None
        
        if not seal_intact:
            is_tampered = True
            anomaly = "PHYSICAL_TAMPER_SEAL_BROKEN"
        elif optical_lux > 500.0:  # Sudden bright light inside closed dark enclosure
            is_tampered = True
            anomaly = "ENCLOSURE_DOOR_FORCED_OPEN"
        elif thermal_delta_c > 25.0:
            is_tampered = True
            anomaly = "EXTREME_THERMAL_RUNAWAY_OR_FIRE"
            
        action = "Dispatch physical field technician immediately and lock cryptographic flash keys" if is_tampered else "Enclosure secure: Maintain passive monitoring"
        
        return VisionTamperAnalysis(
            enclosure_id=enclosure_id,
            is_physical_tamper_detected=is_tampered,
            optical_anomaly_type=anomaly,
            thermal_hotspot_delta_c=thermal_delta_c,
            qr_tamper_seal_valid=seal_intact,
            confidence=0.96 if is_tampered else 0.99,
            recommended_action=action
        )
