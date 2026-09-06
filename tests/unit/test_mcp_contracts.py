"""
Contract and Schema Tests for all 8 MCP Tools
"""
import pytest
from packages.shared.models import (
    GetDeviceProfileInput, QueryRecentTelemetryInput,
    CompareBehaviorBaselineInput, InspectMqttPermissionsInput,
    CheckFirmwareRiskInput, CreateIncidentReportInput,
    ProposeSafeRemediationInput, GetAuditEventsInput,
    RemediationActionType, Incident, IncidentSeverity, IncidentStatus
)
from services.mcp_server.server import mcp_server
from apps.api.repository import repo


@pytest.mark.asyncio
async def test_mcp_all_eight_tools():
    await repo.initialize()

    # Tool 1: get_device_profile
    p1 = GetDeviceProfileInput(device_id="soil-sensor-01")
    o1 = await mcp_server.get_device_profile(p1)
    assert o1.found is True
    assert o1.device is not None
    assert o1.device.id == "soil-sensor-01"

    # Tool 2: query_recent_telemetry
    p2 = QueryRecentTelemetryInput(device_id="soil-sensor-01", limit=10)
    o2 = await mcp_server.query_recent_telemetry(p2)
    assert o2.device_id == "soil-sensor-01"
    assert isinstance(o2.telemetry_events, list)

    # Tool 3: compare_behavior_baseline
    p3 = CompareBehaviorBaselineInput(device_id="soil-sensor-01", metric_name="soil_moisture_pct")
    o3 = await mcp_server.compare_behavior_baseline(p3)
    assert o3.device_id == "soil-sensor-01"

    # Tool 4: inspect_mqtt_permissions
    p4 = InspectMqttPermissionsInput(device_id="soil-sensor-01", candidate_topic="edgeshield/valve-controller-01/cmd")
    o4 = await mcp_server.inspect_mqtt_permissions(p4)
    assert o4.candidate_topic_allowed is False

    # Tool 5: check_firmware_risk
    p5 = CheckFirmwareRiskInput(device_id="greenhouse-env-01")
    o5 = await mcp_server.check_firmware_risk(p5)
    assert o5.is_deprecated is True
    assert len(o5.known_cves) > 0

    # Tool 6: create_incident_report
    inc = Incident(
        id="inc-test-01",
        title="Test Incident",
        device_id="soil-sensor-01",
        detector_id="impossible_value",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        observed_facts=["Observed moisture 450%"],
        derived_findings=["Physical violation"],
        recommendations=["Recalibrate probe"]
    )
    await repo.save_incident(inc)
    p6 = CreateIncidentReportInput(incident_id="inc-test-01")
    o6 = await mcp_server.create_incident_report(p6)
    assert o6.incident is not None
    assert "Observed Facts" in o6.markdown_summary

    # Tool 7: propose_safe_remediation
    p7 = ProposeSafeRemediationInput(
        incident_id="inc-test-01",
        action_type=RemediationActionType.QUARANTINE_DEVICE,
        target_device_id="soil-sensor-01",
        reason="Isolate faulty sensor",
        scope="device:soil-sensor-01:network"
    )
    o7 = await mcp_server.propose_safe_remediation(p7)
    assert o7.requires_human_approval is True
    assert o7.proposal.requires_approval is True

    # Tool 8: get_audit_events
    p8 = GetAuditEventsInput(limit=10)
    o8 = await mcp_server.get_audit_events(p8)
    assert isinstance(o8.events, list)
    assert o8.count >= 1
