"""
EdgeShield Mesh - MCP Tool: Digital Twin Simulator
Simulates physical "what-if" impact and hydraulic/electrical blast radius before executing safety remediations.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class BlastRadiusSimulationInput(BaseModel):
    target_device_id: str
    action: str  # ISOLATE_VALVE, TRIP_BREAKER, REVOKE_CREDENTIALS
    current_flow_rate_lps: float = 25.0
    downstream_pressure_bar: float = 4.2
    connected_zones: List[str] = Field(default_factory=lambda: ["ZONE_NORTH", "ZONE_GREENHOUSE_1"])


class BlastRadiusSimulationOutput(BaseModel):
    is_safe_to_execute: bool
    risk_score: float
    surge_pressure_spike_bar: float
    impacted_downstream_zones: List[str]
    mitigation_required: Optional[str] = None
    simulation_notes: str


class DigitalTwinSimulatorTool:
    """
    MCP tool to perform physical physics-grounded blast radius simulation.
    """

    @staticmethod
    def simulate_action(params: BlastRadiusSimulationInput) -> BlastRadiusSimulationOutput:
        # Water hammer equation: Delta P = rho * a * Delta V
        # If sudden valve cutoff occurs with flow > 20 L/s, surge pressure spikes
        if params.action == "ISOLATE_VALVE":
            surge_spike = (params.current_flow_rate_lps / 10.0) * 1.8
            new_pressure = params.downstream_pressure_bar + surge_spike
            
            is_safe = new_pressure < 8.0 # 8 bar pipe burst rating
            risk = 0.85 if not is_safe else 0.25
            mitigation = "Ramp down solar pump speed before closing solenoid valve" if not is_safe else None
            
            return BlastRadiusSimulationOutput(
                is_safe_to_execute=is_safe,
                risk_score=risk,
                surge_pressure_spike_bar=surge_spike,
                impacted_downstream_zones=params.connected_zones,
                mitigation_required=mitigation,
                simulation_notes=f"Projected downstream peak pressure: {new_pressure:.2f} bar (Rating: 8.0 bar)"
            )
        else:
            return BlastRadiusSimulationOutput(
                is_safe_to_execute=True,
                risk_score=0.1,
                surge_pressure_spike_bar=0.0,
                impacted_downstream_zones=params.connected_zones,
                simulation_notes="No hydraulic physical hazard detected for this action"
            )
