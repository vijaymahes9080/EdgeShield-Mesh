"""
EdgeShield Mesh - Attack Scenario: Satellite RF Jamming & Orbital Desynchronization
Simulates broad-spectrum RF carrier noise jamming on the uplink frequency band (1616-1626 MHz)
causing packet dropouts, burst retransmissions, and gateway desynchronization.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
import time


class JammingSimulationStep(BaseModel):
    step_number: int
    jamming_power_dbm: float
    carrier_snr_db: float
    packet_loss_percentage: float
    network_state: str


class SatelliteJammingDoSScenario:
    """
    Simulates RF jamming progression against rural satellite uplinks.
    """

    @staticmethod
    def simulate_jamming_ramp(initial_snr: float = 18.0) -> List[JammingSimulationStep]:
        steps = []
        powers = [0.0, 10.0, 25.0, 45.0, 60.0]
        
        for i, p in enumerate(powers):
            snr = max(-10.0, initial_snr - (p * 0.45))
            loss = min(100.0, max(0.0, (15.0 - snr) * 6.5)) if snr < 12.0 else 0.0
            state = "NOMINAL" if loss < 5.0 else ("DEGRADED" if loss < 50.0 else "TOTAL_OUTAGE_ISOLATED")
            
            steps.append(JammingSimulationStep(
                step_number=i+1,
                jamming_power_dbm=p,
                carrier_snr_db=snr,
                packet_loss_percentage=loss,
                network_state=state
            ))
        return steps
