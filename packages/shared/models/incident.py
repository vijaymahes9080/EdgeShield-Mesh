"""
Incident, Evidence, Citation, and Risk Assessment Models
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .enums import IncidentSeverity, IncidentStatus


class Citation(BaseModel):
    document_id: str
    version: str
    title: str
    section: str
    page: Optional[int] = None
    snippet: str
    relevance_score: float
    doc_hash: str
    source_type: str = "runbook"  # runbook, manual, iot_guideline, cve_database


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:8]}")
    incident_id: Optional[str] = None
    evidence_type: str = Field(..., description="e.g. telemetry_anomaly, duplicate_hash, timestamp_jump, acl_violation, cve_match, baseline_drift")
    source: str = Field(..., description="Detector ID or component name")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = Field(default_factory=dict)
    description: str
    hash: str = ""


class RiskAssessment(BaseModel):
    incident_id: str
    device_criticality: str = "medium"  # low, medium, high, critical
    threat_vector: str = "Unknown"
    potential_impact: str = "Unknown"
    calculated_risk: IncidentSeverity = IncidentSeverity.MEDIUM
    safety_impact: str = "None"
    confidence: float = 0.85


class RecommendedActionProposal(BaseModel):
    type: str = Field(..., description="Action type, e.g. isolate_device, recalibrate_sensor")
    scope: str = Field(..., description="Target scope, e.g. device:soil-sensor-01")
    reason: str = Field(..., description="Justification grounded in evidence")
    requires_approval: bool = True
    suggested_params: Dict[str, Any] = Field(default_factory=dict)


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: f"inc-{uuid.uuid4().hex[:8]}")
    title: str
    device_id: str
    detector_id: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.DETECTED
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    observed_facts: List[str] = Field(default_factory=list, description="Strictly observed raw data and facts")
    derived_findings: List[str] = Field(default_factory=list, description="Logical conclusions and detections")
    recommendations: List[str] = Field(default_factory=list, description="Actionable operator recommendations")
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
    recommended_action: Optional[RecommendedActionProposal] = None
    limitations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
