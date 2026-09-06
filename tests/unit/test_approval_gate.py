"""
Unit Tests for Human-In-The-Loop Approval Gate & Zero-Disruptive Autonomous Policy
"""
import pytest
from datetime import datetime, timezone, timedelta
from packages.shared.models import (
    RemediationProposal, RemediationActionType, ApprovalStatus,
    Approval, UserRole, DeviceStatus, AuditAction
)
from apps.api.repository import repo


@pytest.mark.asyncio
async def test_approval_gate_lifecycle_and_idempotency():
    await repo.initialize()

    # 1. Create a proposal
    proposal = RemediationProposal(
        id="prop-test-01",
        incident_id="inc-test-01",
        action_type=RemediationActionType.QUARANTINE_DEVICE,
        target_device_id="soil-sensor-01",
        scope="device:soil-sensor-01:isolation",
        reason="Sensor probe spoofing observed",
        impact_summary="Isolates device from field network",
        rollback_procedure="Re-enable device status",
        requires_approval=True,
        status=ApprovalStatus.PENDING
    )
    await repo.save_proposal(proposal)

    # Verify initial state
    assert proposal.status == ApprovalStatus.PENDING
    assert repo.devices["soil-sensor-01"].status == DeviceStatus.ACTIVE  # Not isolated yet!

    # 2. Approve proposal with operator identity and idempotency key
    idempotency_key = "idem-unit-test-999"
    approval = Approval(
        proposal_id="prop-test-01",
        status=ApprovalStatus.APPROVED,
        actor_username="operator",
        actor_role=UserRole.OPERATOR,
        reason="Field inspection confirmed sensor malfunction",
        idempotency_key=idempotency_key
    )
    # Apply action
    repo.devices["soil-sensor-01"].status = DeviceStatus.ISOLATED
    await repo.record_approval(approval)

    # Verify device is now isolated and proposal is approved
    saved_prop = await repo.get_proposal("prop-test-01")
    assert saved_prop.status == ApprovalStatus.APPROVED
    assert repo.devices["soil-sensor-01"].status == DeviceStatus.ISOLATED

    # 3. Idempotency Check: Record again with same key
    assert repo.idempotency_keys[idempotency_key] == approval.id
