"""
EdgeShield Mesh - Model Context Protocol (MCP) Server
Exposes 8 strictly typed, safe, schema-validated IoT cybersecurity tools.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

from packages.shared.models import (
    GetDeviceProfileInput, GetDeviceProfileOutput,
    QueryRecentTelemetryInput, QueryRecentTelemetryOutput,
    CompareBehaviorBaselineInput, CompareBehaviorBaselineOutput,
    InspectMqttPermissionsInput, InspectMqttPermissionsOutput,
    CheckFirmwareRiskInput, CheckFirmwareRiskOutput,
    CreateIncidentReportInput, CreateIncidentReportOutput,
    ProposeSafeRemediationInput, ProposeSafeRemediationOutput,
    GetAuditEventsInput, GetAuditEventsOutput,
    RemediationProposal, RemediationActionType, ApprovalStatus,
    AuditEvent, AuditAction, TopicPermission, DeviceType
)
from apps.api.repository import repo
from services.detection_engine.engine import detection_engine
from services.agent_orchestrator.rag.retriever import rag_retriever

logger = logging.getLogger("edgeshield.mcp")


class EdgeShieldMCPServer:
    def __init__(self):
        self.server_name = "EdgeShield-Mesh-MCP-Server"
        self.version = "1.0.0"

    # Tool 1: get_device_profile
    async def get_device_profile(self, params: GetDeviceProfileInput, actor: str = "mcp_client") -> GetDeviceProfileOutput:
        await repo.log_audit(
            actor=actor,
            actor_role="mcp",
            action=AuditAction.MCP_TOOL_INVOKED,
            resource_type="device",
            resource_id=params.device_id,
            details={"tool": "get_device_profile"}
        )
        device = repo.devices.get(params.device_id)
        if not device:
            return GetDeviceProfileOutput(found=False, error=f"Device {params.device_id} not registered in EdgeShield inventory")
        return GetDeviceProfileOutput(device=device, found=True)

    # Tool 2: query_recent_telemetry
    async def query_recent_telemetry(self, params: QueryRecentTelemetryInput, actor: str = "mcp_client") -> QueryRecentTelemetryOutput:
        await repo.log_audit(
            actor=actor,
            actor_role="mcp",
            action=AuditAction.MCP_TOOL_INVOKED,
            resource_type="telemetry",
            resource_id=params.device_id,
            details={"tool": "query_recent_telemetry", "limit": params.limit}
        )
        events = await repo.get_recent_telemetry(device_id=params.device_id, limit=params.limit)
        return QueryRecentTelemetryOutput(
            device_id=params.device_id,
            telemetry_events=events,
            count=len(events)
        )

    # Tool 3: compare_behavior_baseline
    async def compare_behavior_baseline(self, params: CompareBehaviorBaselineInput, actor: str = "mcp_client") -> CompareBehaviorBaselineOutput:
        device = repo.devices.get(params.device_id)
        if not device:
            return CompareBehaviorBaselineOutput(
                device_id=params.device_id,
                metric_name=params.metric_name,
                details=f"Device {params.device_id} not found."
            )

        events = await repo.get_recent_telemetry(device_id=params.device_id, limit=1)
        current_val = None
        if events and params.metric_name in events[-1].measurements:
            current_val = float(events[-1].measurements[params.metric_name])

        baseline = detection_engine.statistical.get_baseline(device.device_type.value, params.metric_name)
        z_score = None
        is_anomaly = False

        if baseline and current_val is not None and baseline.rolling_std > 0.001:
            z_score = abs(current_val - baseline.rolling_mean) / baseline.rolling_std
            is_anomaly = z_score >= 3.0

        return CompareBehaviorBaselineOutput(
            device_id=params.device_id,
            metric_name=params.metric_name,
            current_value=current_val,
            baseline=baseline,
            z_score=round(z_score, 2) if z_score is not None else None,
            is_anomaly=is_anomaly,
            details=f"Z-score {z_score:.2f}" if z_score is not None else "Insufficient baseline data"
        )

    # Tool 4: inspect_mqtt_permissions
    async def inspect_mqtt_permissions(self, params: InspectMqttPermissionsInput, actor: str = "mcp_client") -> InspectMqttPermissionsOutput:
        device = repo.devices.get(params.device_id)
        if not device:
            return InspectMqttPermissionsOutput(device_id=params.device_id)

        allowed = device.expected_topics
        candidate_allowed = None
        if params.candidate_topic:
            candidate_allowed = any(
                params.candidate_topic == exp or (exp.endswith("#") and params.candidate_topic.startswith(exp[:-1]))
                for exp in allowed
            )

        perms = [
            TopicPermission(
                topic_pattern=t,
                allowed_roles=["device"],
                allowed_device_types=[device.device_type],
                allow_publish=True,
                allow_subscribe=False
            )
            for t in allowed
        ]

        return InspectMqttPermissionsOutput(
            device_id=params.device_id,
            allowed_topics=allowed,
            candidate_topic_allowed=candidate_allowed,
            permissions=perms
        )

    # Tool 5: check_firmware_risk
    async def check_firmware_risk(self, params: CheckFirmwareRiskInput, actor: str = "mcp_client") -> CheckFirmwareRiskOutput:
        device = repo.devices.get(params.device_id)
        if not device:
            return CheckFirmwareRiskOutput(
                device_id=params.device_id,
                current_firmware="unknown",
                is_deprecated=True,
                known_cves=[],
                min_supported_version="1.0.0",
                recommendation="Device not found in inventory."
            )

        cves = device.metadata.get("vulnerabilities", [])
        is_deprecated = device.firmware_version < "1.0.0" or len(cves) > 0
        rec = "Firmware is within safe operating parameters."
        if is_deprecated:
            rec = "Propose scheduling signed OTA firmware update to minimum version 1.0.0."

        return CheckFirmwareRiskOutput(
            device_id=params.device_id,
            current_firmware=device.firmware_version,
            is_deprecated=is_deprecated,
            known_cves=cves,
            min_supported_version="1.0.0",
            recommendation=rec
        )

    # Tool 6: create_incident_report
    async def create_incident_report(self, params: CreateIncidentReportInput, actor: str = "mcp_client") -> CreateIncidentReportOutput:
        incident = await repo.get_incident(params.incident_id)
        if not incident:
            return CreateIncidentReportOutput(
                incident=None,
                markdown_summary=f"### Error\nIncident `{params.incident_id}` not found.",
                citations=[]
            )

        summary = f"""# EdgeShield Incident Report: {incident.id}
**Target Device:** `{incident.device_id}`  
**Detector:** `{incident.detector_id}`  
**Severity:** `{incident.severity.value.upper()}`  
**Status:** `{incident.status.value}`  
**Confidence:** `{incident.confidence * 100:.1f}%`  

## Observed Facts
{chr(10).join([f"- {fact}" for fact in incident.observed_facts])}

## Derived Findings
{chr(10).join([f"- {find}" for find in incident.derived_findings])}

## Recommendations
{chr(10).join([f"- {rec}" for rec in incident.recommendations])}
"""
        return CreateIncidentReportOutput(
            incident=incident,
            markdown_summary=summary,
            citations=incident.citations if params.include_citations else []
        )

    # Tool 7: propose_safe_remediation
    async def propose_safe_remediation(self, params: ProposeSafeRemediationInput, actor: str = "mcp_client") -> ProposeSafeRemediationOutput:
        proposal = RemediationProposal(
            incident_id=params.incident_id,
            action_type=params.action_type,
            target_device_id=params.target_device_id,
            scope=params.scope,
            reason=params.reason,
            impact_summary=f"Applies {params.action_type.value} on {params.target_device_id}",
            rollback_procedure=f"Execute operator rollback on {params.target_device_id}",
            requires_approval=True,  # STRICT: Human in the loop required
            parameters=params.suggested_params,
            status=ApprovalStatus.PENDING
        )
        await repo.save_proposal(proposal)
        await repo.log_audit(
            actor=actor,
            actor_role="mcp",
            action=AuditAction.REMEDIATION_PROPOSED,
            resource_type="proposal",
            resource_id=proposal.id,
            details={"action_type": params.action_type.value, "target": params.target_device_id}
        )
        return ProposeSafeRemediationOutput(
            proposal=proposal,
            status="proposal_registered_pending_approval",
            requires_human_approval=True
        )

    # Tool 8: get_audit_events
    async def get_audit_events(self, params: GetAuditEventsInput, actor: str = "mcp_client") -> GetAuditEventsOutput:
        events = await repo.get_audit_log(resource_id=params.resource_id, limit=params.limit)
        return GetAuditEventsOutput(
            events=events,
            count=len(events)
        )


# Global MCP Server instance
mcp_server = EdgeShieldMCPServer()
