"""
Unit Tests for Cryptographic Audit Ledger and Hash-Chaining
"""
import pytest
from packages.shared.models import AuditEvent, AuditAction
from apps.api.repository import repo


@pytest.mark.asyncio
async def test_audit_ledger_hash_chain():
    await repo.initialize()

    # Log 3 consecutive events
    e1 = await repo.log_audit(
        actor="operator",
        actor_role="operator",
        action=AuditAction.USER_LOGIN,
        resource_type="auth",
        resource_id="operator",
        details={"ip": "192.168.10.50"}
    )

    e2 = await repo.log_audit(
        actor="operator",
        actor_role="operator",
        action=AuditAction.REMEDIATION_APPROVED,
        resource_type="proposal",
        resource_id="prop-01",
        details={"action": "quarantine"}
    )

    e3 = await repo.log_audit(
        actor="agent_orchestrator",
        actor_role="agent",
        action=AuditAction.AGENT_ANALYSIS_COMPLETED,
        resource_type="incident",
        resource_id="inc-01",
        details={"risk": "high"}
    )

    # Verify hashes exist and are 64-character SHA-256 strings
    assert len(e1.entry_hash) == 64
    assert len(e2.entry_hash) == 64
    assert len(e3.entry_hash) == 64

    # Verify Hash-Chain link: e2's prev_hash must match e1's entry_hash
    assert e2.prev_hash == e1.entry_hash
    assert e3.prev_hash == e2.entry_hash
