"""
EdgeShield Mesh - Core Enums and Shared Types
"""
from enum import Enum


class DeviceType(str, Enum):
    SOIL_SENSOR = "soil_sensor"
    WEATHER_STATION = "weather_station"
    VALVE_CONTROLLER = "valve_controller"
    POWER_SUBSYSTEM = "power_subsystem"
    GREENHOUSE_MONITOR = "greenhouse_monitor"


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    ISOLATED = "isolated"
    OFFLINE = "offline"
    UNAUTHORIZED = "unauthorized"


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    MITIGATED = "mitigated"
    DISMISSED = "dismissed"


class RemediationActionType(str, Enum):
    QUARANTINE_DEVICE = "quarantine_device"
    REVOKE_TOPIC_PERMISSION = "revoke_topic_permission"
    RATE_LIMIT_DEVICE = "rate_limit_device"
    SCHEDULE_OTA_FIRMWARE = "schedule_ota_firmware"
    EMERGENCY_VALVE_FAILSAFE = "emergency_valve_failsafe"
    RECALIBRATE_SENSOR = "recalibrate_sensor"
    RESET_GATEWAY_SESSION = "reset_gateway_session"
    BLOCK_IP = "block_ip"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    ROLLED_BACK = "rolled_back"


class UserRole(str, Enum):
    OPERATOR = "operator"
    ANALYST = "analyst"
    ADMIN = "admin"


class AuditAction(str, Enum):
    USER_LOGIN = "user_login"
    TELEMETRY_INGESTED = "telemetry_ingested"
    ANOMALY_DETECTED = "anomaly_detected"
    INCIDENT_CREATED = "incident_created"
    AGENT_ANALYSIS_COMPLETED = "agent_analysis_completed"
    REMEDIATION_PROPOSED = "remediation_proposed"
    REMEDIATION_APPROVED = "remediation_approved"
    REMEDIATION_REJECTED = "remediation_rejected"
    REMEDIATION_EXECUTED = "remediation_executed"
    MCP_TOOL_INVOKED = "mcp_tool_invoked"
    SETTINGS_UPDATED = "settings_updated"
    ATTACK_SIMULATION_STARTED = "attack_simulation_started"
