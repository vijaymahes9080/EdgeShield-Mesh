"""
Unit tests for Multi-Modal Agent modules: Vision Tamper Analyzer, Voice Dispatch, Temporal Graph Reasoner, and Self-Healing Playbooks.
"""

import pytest
from services.agent_orchestrator.multimodal_vision import MultiModalVisionAnalyzer
from services.agent_orchestrator.voice_dispatch import VoiceDispatchSynthesizer
from services.agent_orchestrator.temporal_graph_reasoner import TemporalKnowledgeGraphReasoner
from services.agent_orchestrator.self_healing_playbook import SelfHealingPlaybookGenerator


def test_vision_tamper_analyzer():
    # Intact enclosure
    res_clean = MultiModalVisionAnalyzer.analyze_enclosure_frame("box-01", optical_lux=5.0, thermal_delta_c=2.0, seal_intact=True)
    assert res_clean.is_physical_tamper_detected is False
    
    # Broken seal
    res_seal = MultiModalVisionAnalyzer.analyze_enclosure_frame("box-01", optical_lux=5.0, thermal_delta_c=2.0, seal_intact=False)
    assert res_seal.is_physical_tamper_detected is True
    assert res_seal.optical_anomaly_type == "PHYSICAL_TAMPER_SEAL_BROKEN"
    
    # Forced door open (bright light inside)
    res_light = MultiModalVisionAnalyzer.analyze_enclosure_frame("box-01", optical_lux=800.0, thermal_delta_c=2.0, seal_intact=True)
    assert res_light.is_physical_tamper_detected is True
    assert res_light.optical_anomaly_type == "ENCLOSURE_DOOR_FORCED_OPEN"


def test_voice_dispatch_synthesizer():
    dispatch = VoiceDispatchSynthesizer.generate_radio_dispatch(
        incident_id="inc-7788",
        device_id="valve-gamma-01",
        threat_type="REPLAY_ATTACK",
        severity="CRITICAL",
        recommended_sop="Trip solenoid failsafe"
    )
    assert dispatch.callsign == "EDGESHIELD_CONTROL"
    assert dispatch.audio_urgency_cue == "SIREN_3X"
    assert "VALVE DASH GAMMA DASH 01" in dispatch.phonetic_target
    assert "BREAK BREAK BREAK" in dispatch.full_radio_transcript


def test_temporal_knowledge_graph_reasoner():
    reasoner = TemporalKnowledgeGraphReasoner()
    
    # Power inverter feeds solar pump, which feeds valve
    reasoner.add_relationship("inverter-01", "solar-pump-01", "FEEDS_POWER_TO")
    reasoner.add_relationship("solar-pump-01", "valve-01", "CONTROLS_PRESSURE_FOR")
    
    # Inverter and pump and valve all alarmed simultaneously
    diagnosis = reasoner.diagnose_cascade(["valve-01", "inverter-01", "solar-pump-01"])
    assert diagnosis.root_cause_entity == "inverter-01"
    assert "solar-pump-01" in diagnosis.cascading_affected_entities
    assert "valve-01" in diagnosis.cascading_affected_entities


def test_self_healing_playbook_generator():
    playbook_v1 = SelfHealingPlaybookGenerator.generate_refined_playbook("UNAUTHORIZED_TOPIC", operator_rejections=0)
    assert playbook_v1.version == 1
    assert len(playbook_v1.steps) == 1
    
    playbook_v2 = SelfHealingPlaybookGenerator.generate_refined_playbook("UNAUTHORIZED_TOPIC", operator_rejections=2)
    assert playbook_v2.version == 3
    assert len(playbook_v2.steps) == 2
    assert playbook_v2.steps[0].action_name == "CAPTURE_DIAGNOSTIC_FRAME"
