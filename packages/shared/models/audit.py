"""
Immutable Audit Event Models
"""
import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from .enums import AuditAction


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"aud-{uuid.uuid4().hex[:10]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = Field(..., description="Username, agent ID, or subsystem name")
    actor_role: str = Field(default="system")
    action: AuditAction
    resource_type: str = Field(..., description="e.g. device, incident, proposal, telemetry, mcp_tool")
    resource_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="success", description="success | failure | blocked")
    prev_hash: str = "GENESIS"
    entry_hash: str = ""

    def compute_hash(self, prev_hash: Optional[str] = None) -> str:
        if prev_hash:
            self.prev_hash = prev_hash
        data_to_hash = {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "actor_role": self.actor_role,
            "action": self.action.value if hasattr(self.action, "value") else str(self.action),
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "status": self.status,
            "prev_hash": self.prev_hash
        }
        serialized = json.dumps(data_to_hash, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
