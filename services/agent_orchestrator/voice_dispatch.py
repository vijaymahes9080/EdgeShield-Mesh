"""
EdgeShield Mesh - Voice Dispatch & Rural Radio Alert Synthesizer
Transforms high-severity incident findings and safety approvals into concise,
phonetic voice radio transcripts formatted for push-to-talk (PTT) UHF/VHF rural radios and operator phone lines.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import time


class VoiceDispatchScript(BaseModel):
    dispatch_id: str
    callsign: str
    severity_level: str
    phonetic_target: str
    spoken_summary: str
    audio_urgency_cue: str  # SIREN_3X, SINGLE_CHIME, ADVISORY_BEEP
    full_radio_transcript: str
    created_at: float = Field(default_factory=time.time)


class VoiceDispatchSynthesizer:
    """
    Synthesizes emergency radio voice broadcast scripts.
    """

    @staticmethod
    def generate_radio_dispatch(incident_id: str, device_id: str, threat_type: str, severity: str, recommended_sop: str) -> VoiceDispatchScript:
        # NATO phonetic formatting
        clean_dev = device_id.upper().replace("-", " DASH ")
        
        urgency = "SIREN_3X" if severity == "CRITICAL" else ("SINGLE_CHIME" if severity == "HIGH" else "ADVISORY_BEEP")
        
        spoken = f"Attention Operator. Security alert on device {clean_dev}. Threat classified as {threat_type} with severity {severity}. Immediate required action: {recommended_sop}."
        
        transcript = f"[AUDIO CUE: {urgency}] BREAK BREAK BREAK. THIS IS EDGESHIELD MESH CONTROL. INCIDENT ID {incident_id.upper()}. DEVICE {clean_dev}. THREAT {threat_type.upper()}. ACTION: {recommended_sop.upper()}. OVER."
        
        return VoiceDispatchScript(
            dispatch_id=f"voice-{incident_id[:8]}",
            callsign="EDGESHIELD_CONTROL",
            severity_level=severity,
            phonetic_target=clean_dev,
            spoken_summary=spoken,
            audio_urgency_cue=urgency,
            full_radio_transcript=transcript
        )
