"""
Human-In-The-Loop Approval Gate Routes
Enforces mandatory human authorization for any disruptive remediation proposal.
Requires idempotency key, actor identity, rationale, and emits immutable audit logs.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timezone
from packages.shared.models import (
    RemediationProposal, Approval, ApprovalRequest, ApprovalStatus,
    UserRole, UserPublic, AuditAction, DeviceStatus
)
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user, require_role

router = APIRouter(prefix="/approvals", tags=["Approval Gate"])


@router.get("/proposals", response_model=List[RemediationProposal])
async def list_proposals(
    status_filter: Optional[ApprovalStatus] = None,
    current_user: UserPublic = Depends(get_current_user)
):
    return await repo.list_proposals(status=status_filter)


@router.get("/proposals/{proposal_id}", response_model=RemediationProposal)
async def get_proposal(proposal_id: str, current_user: UserPublic = Depends(get_current_user)):
    proposal = await repo.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal '{proposal_id}' not found")
    return proposal


@router.post("/approve", response_model=Approval)
async def approve_proposal(
    req: ApprovalRequest,
    current_user: UserPublic = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """
    Approves and applies a pending remediation proposal with idempotency guarantees.
    """
    # 1. Idempotency Check
    if req.idempotency_key in repo.idempotency_keys:
        approval_id = repo.idempotency_keys[req.idempotency_key]
        return repo.approvals[approval_id]

    proposal = await repo.get_proposal(req.proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal '{req.proposal_id}' not found")

    if proposal.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal '{req.proposal_id}' is in status '{proposal.status.value}' and cannot be approved"
        )

    # 2. Check Expiration
    now = datetime.now(timezone.utc)
    if proposal.expires_at < now:
        proposal.status = ApprovalStatus.EXPIRED
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal '{req.proposal_id}' expired at {proposal.expires_at.isoformat()}"
        )

    # 3. Apply remediation action safely to state
    target_dev = repo.devices.get(proposal.target_device_id)
    if target_dev:
        if proposal.action_type.value == "quarantine_device":
            target_dev.status = DeviceStatus.ISOLATED
        elif proposal.action_type.value == "revoke_topic_permission":
            target_dev.expected_topics = [f"edgeshield/{target_dev.id}/status"]  # restricted
        elif proposal.action_type.value == "recalibrate_sensor":
            target_dev.status = DeviceStatus.ACTIVE

    # 4. Create Approval Record
    approval = Approval(
        proposal_id=proposal.id,
        status=ApprovalStatus.APPROVED,
        actor_username=current_user.username,
        actor_role=current_user.role,
        reason=req.reason,
        idempotency_key=req.idempotency_key,
        action_taken_at=now,
        signature_or_token_hash=f"sig-{req.idempotency_key[:8]}"
    )
    await repo.record_approval(approval)

    # 5. Log Immutable Audit Event
    await repo.log_audit(
        actor=current_user.username,
        actor_role=current_user.role.value,
        action=AuditAction.REMEDIATION_APPROVED,
        resource_type="proposal",
        resource_id=proposal.id,
        details={
            "action_type": proposal.action_type.value,
            "target_device": proposal.target_device_id,
            "reason": req.reason,
            "idempotency_key": req.idempotency_key
        }
    )

    return approval


@router.post("/reject", response_model=Approval)
async def reject_proposal(
    req: ApprovalRequest,
    current_user: UserPublic = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """
    Rejects a pending remediation proposal.
    """
    if req.idempotency_key in repo.idempotency_keys:
        approval_id = repo.idempotency_keys[req.idempotency_key]
        return repo.approvals[approval_id]

    proposal = await repo.get_proposal(req.proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal '{req.proposal_id}' not found")

    approval = Approval(
        proposal_id=proposal.id,
        status=ApprovalStatus.REJECTED,
        actor_username=current_user.username,
        actor_role=current_user.role,
        reason=req.reason,
        idempotency_key=req.idempotency_key,
        action_taken_at=datetime.now(timezone.utc)
    )
    await repo.record_approval(approval)

    await repo.log_audit(
        actor=current_user.username,
        actor_role=current_user.role.value,
        action=AuditAction.REMEDIATION_REJECTED,
        resource_type="proposal",
        resource_id=proposal.id,
        details={
            "reason": req.reason,
            "idempotency_key": req.idempotency_key
        }
    )

    return approval
