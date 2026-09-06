"""
Unit tests for the 5 Advanced MCP Tools: Digital Twin, Firmware Fuzzer, Satellite Ephemeris, Quarantine, and Threat Intel.
"""

import pytest
from services.mcp_server.tools.digital_twin_simulator import DigitalTwinSimulatorTool, BlastRadiusSimulationInput
from services.mcp_server.tools.firmware_fuzzer import FirmwareFuzzerTool, FirmwareFuzzInput
from services.mcp_server.tools.satellite_ephemeris_verifier import SatelliteEphemerisVerifierTool, SatelliteEphemerisInput
from services.mcp_server.tools.autonomous_quarantine_recommender import AutonomousQuarantineRecommenderTool, QuarantineRecommendationInput
from services.mcp_server.tools.threat_intel_correlator import ThreatIntelCorrelatorTool, ThreatIntelInput


def test_digital_twin_simulator_water_hammer_risk():
    params = BlastRadiusSimulationInput(
        target_device_id="valve-gamma",
        action="ISOLATE_VALVE",
        current_flow_rate_lps=40.0,
        downstream_pressure_bar=4.5
    )
    res = DigitalTwinSimulatorTool.simulate_action(params)
    assert res.surge_pressure_spike_bar > 5.0
    assert res.is_safe_to_execute is False
    assert res.mitigation_required is not None


def test_firmware_fuzzer_symbolic_analysis():
    params = FirmwareFuzzInput(
        firmware_binary_hex="7F454C460101010000000000000000000200280001000000",
        target_architecture="ARM_Cortex_M4",
        mutation_iterations=25
    )
    res = FirmwareFuzzerTool.run_fuzzing(params)
    assert res.total_mutations_tested == 25
    assert len(res.vulnerabilities_discovered) > 0


def test_satellite_ephemeris_verifier():
    params_spoof = SatelliteEphemerisInput(
        ground_station_lat=34.05,
        ground_station_lon=-118.24,
        observed_satellite_norad_id=25544,
        observed_signal_frequency_mhz=145.8,
        observed_elevation_deg=85.0
    )
    res = SatelliteEphemerisVerifierTool.verify_ephemeris(params_spoof)
    assert res.is_spoofing_suspected is True
    assert res.confidence > 0.9


def test_autonomous_quarantine_recommender():
    params = QuarantineRecommendationInput(
        compromised_device_id="compromised-sensor-01",
        network_topology_edges=[
            ["compromised-sensor-01", "gateway-01"],
            ["healthy-sensor-02", "gateway-01"]
        ]
    )
    res = AutonomousQuarantineRecommenderTool.recommend_quarantine(params)
    assert res.recommended_isolated_node == "compromised-sensor-01"
    assert len(res.severed_links) == 1
    assert "healthy-sensor-02" in res.unaffected_operational_devices


def test_threat_intel_correlator_kev():
    params = ThreatIntelInput(
        device_model="IoT_Router_X",
        firmware_version="v1.0.0",
        active_cves=["CVE-2023-28771"]
    )
    res = ThreatIntelCorrelatorTool.correlate_intel(params)
    assert res.matches_found == 1
    assert res.overall_threat_level == "CRITICAL"
    assert res.kev_vulnerabilities[0].is_actively_exploited_in_wild is True
