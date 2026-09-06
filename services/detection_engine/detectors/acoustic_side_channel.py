"""
EdgeShield Mesh - Acoustic & Vibration Side-Channel Tamper Detector
Processes vibration harmonics and motor acoustic power spectrum signatures 
to detect mechanical bearing faults, cavitation, or physical actuator lock attacks.
"""

import math
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import time


class AcousticTamperAlert(BaseModel):
    device_id: str
    dominant_frequency_hz: float
    thd_ratio: float  # Total Harmonic Distortion
    vibration_energy_db: float
    tamper_type: str
    detected_at: float = Field(default_factory=time.time)


class AcousticSideChannelDetector:
    """
    Computes lightweight discrete Fourier spectral metrics over vibration time series.
    """

    def __init__(self, sample_rate_hz: float = 1000.0, nominal_motor_hz: float = 60.0):
        self.sample_rate = sample_rate_hz
        self.nominal_hz = nominal_motor_hz

    def analyze_waveform(self, device_id: str, samples: List[float]) -> Optional[AcousticTamperAlert]:
        if len(samples) < 32:
            return None
            
        n = len(samples)
        # Compute RMS energy
        rms = math.sqrt(sum(s**2 for s in samples) / n)
        db_energy = 20 * math.log10(max(1e-6, rms))
        
        # Simplified peak frequency estimation via Zero-Crossing Rate
        zero_crossings = sum(1 for i in range(1, n) if (samples[i] >= 0 and samples[i-1] < 0) or (samples[i] < 0 and samples[i-1] >= 0))
        estimated_hz = (zero_crossings * self.sample_rate) / (2.0 * n)
        
        # Harmonic distortion proxy
        variance = sum((s - rms)**2 for s in samples) / n
        thd = variance / (rms**2 + 1e-6)
        
        # Check for abnormal mechanical resonance / cavitation
        if estimated_hz > self.nominal_hz * 3.5 or thd > 2.5:
            tamper_type = "HIGH_FREQUENCY_CAVITATION_OR_TAMPER" if estimated_hz > self.nominal_hz * 3.5 else "EXCESSIVE_HARMONIC_DISTORTION"
            return AcousticTamperAlert(
                device_id=device_id,
                dominant_frequency_hz=estimated_hz,
                thd_ratio=thd,
                vibration_energy_db=db_energy,
                tamper_type=tamper_type
            )
        return None
