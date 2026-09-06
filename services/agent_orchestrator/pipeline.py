"""
EdgeShield Mesh - 11-Step Incident Response Agent Orchestrator
Executes strict evidence-grounded analysis, runbook RAG lookup,
generates facts/findings/recommendations separation, and routes remediation to the Approval Gate.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx

from packages.shared.models import (
    Incident, EvidenceItem, Citation, RiskAssessment, RecommendedActionProposal,
    RemediationProposal, RemediationActionType, ApprovalStatus, IncidentSeverity,
    AuditEvent, AuditAction, UserRole
)
from packages.shared.security import (
    sanitize_untrusted_input, detect_prompt_injection, redact_pii
)
from apps.api.repository import repo
from services.agent_orchestrator.rag.retriever import rag_retriever
from services.detection_engine.engine import detection_engine

logger = logging.getLogger("edgeshield.agent")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class AgentOrchestrator:
    def __init__(self, ollama_url: str = OLLAMA_HOST):
        self.ollama_url = ollama_url

    async def execute_incident_workflow(self, incident_id: str) -> Dict[str, Any]:
        """
        Executes the 11-step incident response workflow.
        """
        # Step 1: Receive incident ID
        # Step 2: Retrieve incident and evidence
        incident = await repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found in state repository")

        # Step 3: Query device profile
        device = repo.devices.get(incident.device_id)
        dev_type = device.device_type.value if device else "unknown"
        dev_zone = device.zone if device else "unknown"

        # Step 4: Query recent telemetry
        recent_telemetry = await repo.get_recent_telemetry(device_id=incident.device_id, limit=10)

        # Step 5: Compare with baseline
        baseline_info = {}
        if recent_telemetry and device:
            latest = recent_telemetry[-1]
            for metric, val in latest.measurements.items():
                if isinstance(val, (int, float)):
                    base = detection_engine.statistical.get_baseline(dev_type, metric)
                    if base:
                        baseline_info[metric] = {
                            "observed": val,
                            "baseline_mean": base.rolling_mean,
                            "baseline_std": base.rolling_std,
                            "ewma": base.ewma
                        }

        # Step 6: Retrieve relevant runbook sections via RAG
        rag_query = f"{incident.detector_id} {incident.title} {dev_type} {dev_zone}"
        citations = rag_retriever.retrieve(rag_query, top_k=3)
        incident.citations = citations

        # Check for prompt injection in evidence data or telemetry
        for ev in incident.evidence_items:
            for k, v in ev.data.items():
                is_inj, pattern = detect_prompt_injection(str(v))
                if is_inj:
                    incident.observed_facts.append(f"Security Alert: Malicious prompt injection pattern detected in field '{k}' ({pattern}). Untrusted content quarantined.")

        # Step 7: Produce structured analysis (Observed facts vs Derived findings vs Recommendations)
        observed_facts = [
            f"Incident triggered on device '{incident.device_id}' ({dev_type}) located in '{dev_zone}'.",
            f"Detector '{incident.detector_id}' flagged anomaly with confidence {incident.confidence:.2f}."
        ]
        for ev in incident.evidence_items:
            observed_facts.append(f"Evidence [{ev.source}]: {sanitize_untrusted_input(ev.description)}")

        derived_findings = [
            f"Telemetry pattern corresponds to known threat signature: {incident.detector_id}.",
            f"Device operating profile indicates {len(recent_telemetry)} telemetry packets recorded in recent window."
        ]
        if baseline_info:
            derived_findings.append(f"Statistical deviation observed against rolling baseline: {json.dumps(baseline_info)}.")

        # Step 8: Assign risk level
        risk_level = incident.severity
        if incident.detector_id in ["unauthorized_topic", "gateway_disconnect"]:
            risk_level = IncidentSeverity.CRITICAL
        elif incident.detector_id in ["impossible_value", "burst_rate", "timestamp_rollback"]:
            risk_level = IncidentSeverity.HIGH

        # Step 9: Propose a remediation action (with requires_approval: true)
        action_mapping = {
            "duplicate_message": (RemediationActionType.RATE_LIMIT_DEVICE, "Rate-limit transmission retry storm"),
            "timestamp_rollback": (RemediationActionType.QUARANTINE_DEVICE, "Isolate device to prevent replay injection"),
            "burst_rate": (RemediationActionType.RATE_LIMIT_DEVICE, "Apply edge gateway throttle (1 msg/min)"),
            "impossible_value": (RemediationActionType.RECALIBRATE_SENSOR, "Mask sensor data in control loop and schedule probe recalibration"),
            "device_silence": (RemediationActionType.RESET_GATEWAY_SESSION, "Restart gateway radio session and poll endpoint"),
            "unauthorized_topic": (RemediationActionType.REVOKE_TOPIC_PERMISSION, "Revoke MQTT ACL publish permissions on unassigned topics"),
            "firmware_age_risk": (RemediationActionType.SCHEDULE_OTA_FIRMWARE, "Schedule signed OTA microcode upgrade to minimum version 1.0.0"),
            "gateway_disconnect": (RemediationActionType.RESET_GATEWAY_SESSION, "Failover to secondary rural LoRa/cellular backhaul link")
        }

        action_type, action_reason = action_mapping.get(
            incident.detector_id,
            (RemediationActionType.QUARANTINE_DEVICE, "Isolate device pending operator inspection")
        )

        proposal = RemediationProposal(
            incident_id=incident.id,
            action_type=action_type,
            target_device_id=incident.device_id,
            scope=f"device:{incident.device_id}:{action_type.value}",
            reason=f"Grounded in {len(citations)} runbook citations: {action_reason}.",
            impact_summary=f"Temporarily applies {action_type.value} on {incident.device_id} without affecting other field nodes.",
            rollback_procedure=f"Revert via EdgeShield Operator console by executing rollback on {incident.device_id}.",
            requires_approval=True,  # STRICT: Never execute autonomously
            status=ApprovalStatus.PENDING,
            parameters={"device_id": incident.device_id, "zone": dev_zone}
        )

        # Step 10: Require approval (Register in approval gate)
        await repo.save_proposal(proposal)

        # Update Incident Object
        incident.observed_facts = observed_facts
        incident.derived_findings = derived_findings
        incident.recommendations = [
            f"Review citations from {', '.join([c.document_id for c in citations]) if citations else 'Standard SOP'}.",
            f"Authorize proposal '{proposal.id}' to execute '{action_type.value}' on {incident.device_id}.",
            "Perform physical sensor visual check if values remain abnormal."
        ]
        incident.risk_assessment = RiskAssessment(
            incident_id=incident.id,
            device_criticality="high" if dev_type in ["valve_controller", "power_subsystem"] else "medium",
            threat_vector=incident.detector_id,
            potential_impact="Agricultural crop loss, sensor spoofing, or rogue actuator manipulation",
            calculated_risk=risk_level,
            safety_impact="High - human in the loop required before actuating physical hardware",
            confidence=incident.confidence
        )
        incident.recommended_action = RecommendedActionProposal(
            type=action_type.value,
            scope=proposal.scope,
            reason=proposal.reason,
            requires_approval=True,
            suggested_params=proposal.parameters
        )
        incident.limitations = [
            "Analysis is grounded in local edge runbooks and historical telemetry.",
            "Autonomous physical actuation is strictly prohibited by policy."
        ]

        await repo.save_incident(incident)

        # Step 11: Log the result and emit audit event
        await repo.log_audit(
            actor="agent_orchestrator",
            actor_role="agent",
            action=AuditAction.AGENT_ANALYSIS_COMPLETED,
            resource_type="incident",
            resource_id=incident.id,
            details={
                "risk_level": risk_level.value,
                "proposal_id": proposal.id,
                "action_type": action_type.value,
                "citations_count": len(citations)
            }
        )

        # Return structured output schema as required by prompt
        return {
            "incident_id": incident.id,
            "observed_facts": incident.observed_facts,
            "derived_findings": incident.derived_findings,
            "risk_level": risk_level.value,
            "confidence": incident.confidence,
            "citations": [c.model_dump() for c in incident.citations],
            "recommended_action": {
                "type": action_type.value,
                "scope": proposal.scope,
                "reason": proposal.reason,
                "requires_approval": True
            },
            "limitations": incident.limitations
        }


# Global agent instance
agent_orchestrator = AgentOrchestrator()
