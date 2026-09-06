"""
Unit tests for extended attack scenarios: Stuxnet, Supply Chain, Satellite Jamming, OTA Tamper, and ICS Ransomware.
"""

import pytest
from services.attack_simulator.scenarios.stuxnet_frequency_spoof import StuxnetFrequencySpoofScenario
from services.attack_simulator.scenarios.shadow_broker_zero_day import ShadowBrokerZeroDayScenario
from services.attack_simulator.scenarios.satellite_jamming_dos import SatelliteJammingDoSScenario
from services.attack_simulator.scenarios.solarwinds_ota_tamper import SolarWindsOTATamperScenario
from services.attack_simulator.scenarios.ransomware_actuator_lock import RansomwareActuatorLockScenario


def test_stuxnet_frequency_spoof_generation():
    events = StuxnetFrequencySpoofScenario.generate_attack_stream(num_steps=3)
    assert len(events) == 3
    assert events[0].injected_payload["override_safety_interlock"] is True
    assert events[0].spoofed_status_payload["status"] == "NOMINAL_SMOOTH"


def test_shadow_broker_zero_day_progression():
    stages = ShadowBrokerZeroDayScenario.generate_attack_progression()
    assert len(stages) == 3
    assert stages[0].stage_name == "DORMANT_INITIALIZATION"
    assert stages[2].stage_name == "FIRMWARE_MODIFICATION"


def test_satellite_jamming_ramp():
    steps = SatelliteJammingDoSScenario.simulate_jamming_ramp(initial_snr=18.0)
    assert len(steps) == 5
    assert steps[0].network_state == "NOMINAL"
    assert steps[-1].network_state == "TOTAL_OUTAGE_ISOLATED"
    assert steps[-1].packet_loss_percentage > 80.0


def test_solarwinds_ota_tamper():
    payload = SolarWindsOTATamperScenario.construct_tampered_update()
    assert payload.original_sha256 != payload.tampered_sha256
    assert payload.is_signature_forged is True
    assert "REVERSE_SHELL" in payload.injected_exploit_vector or "hooked" in payload.injected_exploit_vector


def test_ransomware_actuator_lock():
    res = RansomwareActuatorLockScenario.trigger_actuator_lock()
    assert res.attack_name == "AGRI_LOCK_ICS_RANSOMWARE"
    assert len(res.target_actuators) >= 2
    assert res.locked_state == "PERMANENTLY_CLOSED"
