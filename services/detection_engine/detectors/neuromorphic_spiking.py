"""
EdgeShield Mesh - Neuromorphic Spiking Neural Network (SNN) Detector
Uses a Leaky Integrate-and-Fire (LIF) neuron model to detect high-frequency anomalous pulse
bursts and inter-spike interval disruptions in sensor signals using minimal edge computation.
"""

import time
import math
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SNNAnomalyAlert(BaseModel):
    device_id: str
    metric_name: str
    membrane_potential: float
    threshold: float
    spike_rate: float
    confidence: float
    detected_at: float = Field(default_factory=time.time)


class LeakyIntegrateFireDetector:
    """
    Simulates a neuromorphic LIF neuron that integrates sensor delta spikes over time with exponential decay.
    """

    def __init__(self, decay_rate: float = 0.9, threshold: float = 5.0, min_refractory_period: float = 0.05):
        self.decay_rate = decay_rate
        self.threshold = threshold
        self.min_refractory_period = min_refractory_period
        
        # State per (device_id, metric)
        self._membrane_voltages: Dict[str, float] = {}
        self._last_spike_times: Dict[str, float] = {}
        self._spike_counts: Dict[str, int] = {}
        self._last_input_times: Dict[str, float] = {}
        self._last_values: Dict[str, float] = {}

    def process_sample(self, device_id: str, metric_name: str, value: float, timestamp: Optional[float] = None) -> Optional[SNNAnomalyAlert]:
        key = f"{device_id}:{metric_name}"
        now = timestamp or time.time()
        
        last_t = self._last_input_times.get(key, now)
        dt = max(0.001, now - last_t)
        self._last_input_times[key] = now
        
        last_val = self._last_values.get(key, value)
        self._last_values[key] = value
        
        # Input current is proportional to rate of change |dv/dt|
        delta = abs(value - last_val)
        input_current = delta / dt if dt > 0 else 0.0
        
        # Leaky integration: V(t) = V(t-1) * exp(-decay * dt) + I(t)
        current_v = self._membrane_voltages.get(key, 0.0)
        decay_factor = math.exp(-self.decay_rate * dt)
        new_v = (current_v * decay_factor) + input_current
        
        # Refractory period check
        last_spike_t = self._last_spike_times.get(key, 0.0)
        is_refractory = (now - last_spike_t) < self.min_refractory_period
        
        if new_v >= self.threshold and not is_refractory:
            # Neuron fires an action potential / spike
            self._membrane_voltages[key] = 0.0 # Reset potential
            self._last_spike_times[key] = now
            self._spike_counts[key] = self._spike_counts.get(key, 0) + 1
            
            spike_rate = self._spike_counts[key] / max(1.0, (now - last_spike_t))
            return SNNAnomalyAlert(
                device_id=device_id,
                metric_name=metric_name,
                membrane_potential=new_v,
                threshold=self.threshold,
                spike_rate=spike_rate,
                confidence=min(1.0, new_v / (self.threshold * 1.5))
            )
        else:
            self._membrane_voltages[key] = new_v
            return None
