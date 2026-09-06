"""
Strict Pydantic Input/Output Schemas for MCP Tools
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .enums import IncidentSeverity, RemediationActionType
from .device import Device, TopicPermission, FirmwareRecord
from .telemetry import NormalizedTelemetry
from .detection import BaselineMetric
from .incident import Incident, Citation
from .remediation import RemediationProposal
from .audit import AuditEvent


# 1. get_device_profile
class GetDeviceProfileInput(BaseModel):
    device_id: str = Field(..., max_length=64, description="Target device ID")


class GetDeviceProfileOutput(BaseModel):
    device: Optional[Device] = None
    found: bool
    error: Optional[str] = None


# 2. query_recent_telemetry
class QueryRecentTelemetryInput(BaseModel):
    device_id: str = Field(..., max_length=64, description="Target device ID")
    limit: int = Field(default=20, ge=1, le=100, description="Number of recent telemetry records")


class QueryRecentTelemetryOutput(BaseModel):
    device_id: str
    telemetry_events: List[NormalizedTelemetry] = Field(default_factory=list)
    count: int = 0


# 3. compare_behavior_baseline
class CompareBehaviorBaselineInput(BaseModel):
    device_id: str = Field(..., max_length=64, description="Target device ID")
    metric_name: str = Field(..., max_length=64, description="Metric to compare, e.g. soil_moisture_pct, temperature_c")


class CompareBehaviorBaselineOutput(BaseModel):
    device_id: str
    metric_name: str
    current_value: Optional[float] = None
    baseline: Optional[BaselineMetric] = None
    z_score: Optional[float] = None
    is_anomaly: bool = False
    details: str = ""


# 4. inspect_mqtt_permissions
class InspectMqttPermissionsInput(BaseModel):
    device_id: str = Field(..., max_length=64, description="Target device ID")
    candidate_topic: Optional[str] = Field(None, max_length=256, description="Candidate topic to check access for")


class InspectMqttPermissionsOutput(BaseModel):
    device_id: str
    allowed_topics: List[str] = Field(default_factory=list)
    candidate_topic_allowed: Optional[bool] = None
    permissions: List[TopicPermission] = Field(default_factory=list)


# 5. check_firmware_risk
class CheckFirmwareRiskInput(BaseModel):
    device_id: str = Field(..., max_length=64, description="Target device ID")


class CheckFirmwareRiskOutput(BaseModel):
    device_id: str
    current_firmware: str
    is_deprecated: bool
    known_cves: List[str] = Field(default_factory=list)
    min_supported_version: str
    recommendation: str


# 6. create_incident_report
class CreateIncidentReportInput(BaseModel):
    incident_id: str = Field(..., max_length=64, description="Incident ID to report")
    include_citations: bool = Field(default=True)


class CreateIncidentReportOutput(BaseModel):
    incident: Optional[Incident] = None
    markdown_summary: str
    citations: List[Citation] = Field(default_factory=list)


# 7. propose_safe_remediation
class ProposeSafeRemediationInput(BaseModel):
    incident_id: str = Field(..., max_length=64)
    action_type: RemediationActionType
    target_device_id: str = Field(..., max_length=64)
    reason: str = Field(..., max_length=1000)
    scope: str = Field(..., max_length=256)
    suggested_params: Dict[str, Any] = Field(default_factory=dict)


class ProposeSafeRemediationOutput(BaseModel):
    proposal: RemediationProposal
    status: str = "proposal_registered_pending_approval"
    requires_human_approval: bool = True
    notice: str = "Disruptive actions are never executed autonomously. A human operator must approve this proposal."


# 8. get_audit_events
class GetAuditEventsInput(BaseModel):
    resource_id: Optional[str] = Field(None, max_length=64)
    limit: int = Field(default=50, ge=1, le=200)


class GetAuditEventsOutput(BaseModel):
    events: List[AuditEvent] = Field(default_factory=list)
    count: int = 0
