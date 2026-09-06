"""
EdgeShield Mesh - Unified State Repository
Maintains fast in-memory state with SQLite durability and default seed data.
"""
import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from packages.shared.models import (
    Device, DeviceType, DeviceStatus, Gateway,
    NormalizedTelemetry, RawTelemetry,
    Incident, IncidentSeverity, IncidentStatus, EvidenceItem, Citation, RiskAssessment, RecommendedActionProposal,
    RemediationProposal, RemediationActionType, Approval, ApprovalStatus, ApprovalRequest,
    AuditEvent, AuditAction,
    User, UserRole, UserPublic,
    DetectionRule, BaselineMetric
)
from packages.shared.security import get_password_hash
from apps.api.db import DB_PATH, init_db
import aiosqlite


class StateRepository:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.devices: Dict[str, Device] = {}
        self.telemetry_history: List[NormalizedTelemetry] = []
        self.incidents: Dict[str, Incident] = {}
        self.proposals: Dict[str, RemediationProposal] = {}
        self.approvals: Dict[str, Approval] = {}
        self.audit_log: List[AuditEvent] = []
        self.users: Dict[str, User] = {}
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.baselines: Dict[str, BaselineMetric] = {}
        self.idempotency_keys: Dict[str, str] = {}
        self.prev_audit_hash: str = "GENESIS_HASH_EDGESHIELD_MESH_2026"

    async def initialize(self):
        await init_db()
        await self._seed_default_users()
        await self._seed_default_devices()
        await self._seed_default_rules()

    async def _seed_default_users(self):
        # Default accounts: admin, operator, analyst
        default_users = [
            User(
                username="admin",
                email="admin@edgeshield.local",
                full_name="EdgeShield Administrator",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin12345!"),
                is_active=True
            ),
            User(
                username="operator",
                email="Vijaypradhap2004@gmail.com",
                full_name="Vijay Mahes (Operator)",
                role=UserRole.OPERATOR,
                hashed_password=get_password_hash("operator123!"),
                is_active=True
            ),
            User(
                username="analyst",
                email="analyst@edgeshield.local",
                full_name="Security Analyst",
                role=UserRole.ANALYST,
                hashed_password=get_password_hash("analyst123!"),
                is_active=True
            ),
        ]
        for u in default_users:
            self.users[u.username] = u

    async def _seed_default_devices(self):
        profile_path = os.path.join("data", "device_profiles", "virtual_devices.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                for item in raw:
                    dev = Device(
                        id=item["id"],
                        name=item["name"],
                        device_type=DeviceType(item["device_type"]),
                        zone=item["zone"],
                        owner=item.get("owner", "Agritech Cooperative"),
                        status=DeviceStatus(item.get("status", "active")),
                        firmware_version=item.get("firmware_version", "1.0.0"),
                        hardware_rev=item.get("hardware_rev", "revA"),
                        ip_address=item.get("ip_address", "192.168.10.100"),
                        mac_address=item.get("mac_address", "00:00:00:00:00:00"),
                        telemetry_interval_sec=item.get("telemetry_interval_sec", 10),
                        expected_topics=item.get("expected_topics", []),
                        allowed_actuators=item.get("allowed_actuators", []),
                        is_virtual=item.get("is_virtual", True),
                        metadata=item.get("metadata", {})
                    )
                    self.devices[dev.id] = dev

    async def _seed_default_rules(self):
        rules = [
            DetectionRule(rule_id="RULE-DUP", name="Duplicate Telemetry Suppression", detector_id="duplicate_message", severity=IncidentSeverity.MEDIUM, parameters={"cache_ttl_sec": 60}),
            DetectionRule(rule_id="RULE-ROLLBACK", name="Timestamp Rollback Guard", detector_id="timestamp_rollback", severity=IncidentSeverity.HIGH, parameters={"tolerance_sec": 5}),
            DetectionRule(rule_id="RULE-BURST", name="Burst Flooding Guard", detector_id="burst_rate", severity=IncidentSeverity.HIGH, parameters={"max_msgs_per_sec": 10}),
            DetectionRule(rule_id="RULE-BOUNDS", name="Physical Bounds Validation", detector_id="impossible_value", severity=IncidentSeverity.HIGH, parameters={}),
            DetectionRule(rule_id="RULE-SILENCE", name="Heartbeat Silence Watchdog", detector_id="device_silence", severity=IncidentSeverity.MEDIUM, parameters={"timeout_multiplier": 3}),
            DetectionRule(rule_id="RULE-ACL", name="Unauthorized Topic Filter", detector_id="unauthorized_topic", severity=IncidentSeverity.CRITICAL, parameters={}),
            DetectionRule(rule_id="RULE-FW", name="Deprecated Firmware Vulnerability", detector_id="firmware_age_risk", severity=IncidentSeverity.HIGH, parameters={"min_version": "1.0.0"}),
            DetectionRule(rule_id="RULE-GW", name="Gateway Keepalive Monitor", detector_id="gateway_disconnect", severity=IncidentSeverity.CRITICAL, parameters={"keepalive_timeout_sec": 45}),
        ]
        for r in rules:
            self.detection_rules[r.rule_id] = r

    # --- Telemetry Operations ---
    async def add_telemetry(self, item: NormalizedTelemetry):
        async with self._lock:
            self.telemetry_history.append(item)
            if len(self.telemetry_history) > 5000:
                self.telemetry_history = self.telemetry_history[-5000:]
            if item.device_id in self.devices:
                self.devices[item.device_id].last_seen = item.timestamp

    async def get_recent_telemetry(self, device_id: Optional[str] = None, limit: int = 50) -> List[NormalizedTelemetry]:
        async with self._lock:
            if device_id:
                events = [t for t in self.telemetry_history if t.device_id == device_id]
            else:
                events = self.telemetry_history
            return events[-limit:]

    # --- Incident Operations ---
    async def save_incident(self, incident: Incident):
        async with self._lock:
            self.incidents[incident.id] = incident

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        async with self._lock:
            return self.incidents.get(incident_id)

    async def list_incidents(self, limit: int = 100) -> List[Incident]:
        async with self._lock:
            return sorted(list(self.incidents.values()), key=lambda x: x.created_at, reverse=True)[:limit]

    # --- Remediation & Approval Operations ---
    async def save_proposal(self, proposal: RemediationProposal):
        async with self._lock:
            self.proposals[proposal.id] = proposal

    async def get_proposal(self, proposal_id: str) -> Optional[RemediationProposal]:
        async with self._lock:
            return self.proposals.get(proposal_id)

    async def list_proposals(self, status: Optional[ApprovalStatus] = None) -> List[RemediationProposal]:
        async with self._lock:
            proposals = list(self.proposals.values())
            if status:
                proposals = [p for p in proposals if p.status == status]
            return sorted(proposals, key=lambda x: x.created_at, reverse=True)

    async def record_approval(self, approval: Approval):
        async with self._lock:
            self.approvals[approval.id] = approval
            self.idempotency_keys[approval.idempotency_key] = approval.id
            if approval.proposal_id in self.proposals:
                prop = self.proposals[approval.proposal_id]
                prop.status = approval.status
                prop.executed_at = approval.action_taken_at
                prop.execution_result = f"Action {prop.action_type.value} applied successfully by {approval.actor_username} ({approval.actor_role.value})."

    # --- Audit Log Operations ---
    async def log_audit(
        self,
        actor: str,
        actor_role: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any],
        status: str = "success"
    ) -> AuditEvent:
        async with self._lock:
            event = AuditEvent(
                actor=actor,
                actor_role=actor_role,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                status=status,
                prev_hash=self.prev_audit_hash
            )
            event.entry_hash = event.compute_hash(self.prev_audit_hash)
            self.prev_audit_hash = event.entry_hash
            self.audit_log.append(event)
            return event

    async def get_audit_log(self, resource_id: Optional[str] = None, limit: int = 100) -> List[AuditEvent]:
        async with self._lock:
            if resource_id:
                events = [e for e in self.audit_log if e.resource_id == resource_id or e.resource_type == resource_id]
            else:
                events = self.audit_log
            return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]


# Global repository instance
repo = StateRepository()
