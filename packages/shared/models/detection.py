"""
Detection Rule and Detector Result Models
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .enums import IncidentSeverity


class DetectionRule(BaseModel):
    rule_id: str
    name: str
    detector_id: str
    enabled: bool = True
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class DetectorResult(BaseModel):
    detector_id: str = Field(..., description="ID of the detector that triggered (e.g. duplicate_message)")
    severity: IncidentSeverity
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    observed_fields: Dict[str, Any] = Field(default_factory=dict, description="Observed raw and computed fields")
    explanation: str = Field(..., description="Deterministic human-readable explanation of why detection triggered")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of correlated evidence items")
    recommended_next_step: str = Field(..., description="Actionable triage recommendation")
    triggered: bool = True
    device_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaselineMetric(BaseModel):
    device_type: str
    metric_name: str
    rolling_mean: float
    rolling_std: float
    min_observed: float
    max_observed: float
    ewma: float
    sample_count: int
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
