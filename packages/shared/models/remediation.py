"""
Remediation Proposals, Approval Gate, and Verification Models
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from .enums import RemediationActionType, ApprovalStatus, UserRole


class RemediationProposal(BaseModel):
    id: str = Field(default_factory=lambda: f"prop-{uuid.uuid4().hex[:8]}")
    incident_id: str
    action_type: RemediationActionType
    target_device_id: str
    scope: str = Field(..., description="Scope string (e.g. device:soil-sensor-01:network_isolation)")
    reason: str = Field(..., description="Evidence-backed explanation for this proposal")
    impact_summary: str = Field(..., description="Operational impact if executed")
    rollback_procedure: str = Field(..., description="Exact steps to revert this action if required")
    requires_approval: bool = True  # strictly True for any disruptive action
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    status: ApprovalStatus = ApprovalStatus.PENDING
    idempotency_key: str = Field(default_factory=lambda: f"idem-{uuid.uuid4().hex[:12]}")
    executed_at: Optional[datetime] = None
    execution_result: Optional[str] = None


class ApprovalRequest(BaseModel):
    proposal_id: str
    reason: str = Field(..., min_length=3, description="Operator justification for approval or rejection")
    idempotency_key: str = Field(..., description="Client idempotency key to prevent double execution")


class Approval(BaseModel):
    id: str = Field(default_factory=lambda: f"appr-{uuid.uuid4().hex[:8]}")
    proposal_id: str
    status: ApprovalStatus
    actor_username: str
    actor_role: UserRole
    reason: str
    idempotency_key: str
    action_taken_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signature_or_token_hash: str = ""
