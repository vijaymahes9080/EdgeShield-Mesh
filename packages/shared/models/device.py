"""
Device and Gateway Schemas
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .enums import DeviceType, DeviceStatus


class FirmwareRecord(BaseModel):
    version: str = Field(..., description="Firmware semantic version (e.g. 1.2.0)")
    device_type: DeviceType
    release_date: str
    is_deprecated: bool = False
    known_cves: List[str] = Field(default_factory=list)
    min_supported_version: str = "1.0.0"


class TopicPermission(BaseModel):
    topic_pattern: str
    allowed_roles: List[str] = Field(default_factory=lambda: ["device"])
    allowed_device_types: List[DeviceType] = Field(default_factory=list)
    allow_publish: bool = True
    allow_subscribe: bool = False


class Device(BaseModel):
    id: str = Field(..., description="Stable device unique identifier (e.g. soil-sensor-01)")
    name: str = Field(..., description="Human-readable device name")
    device_type: DeviceType
    zone: str = Field(..., description="Physical location zone (e.g. zone_a_north_field)")
    owner: str = Field(default="Agritech Co-op")
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    firmware_version: str = Field(default="1.0.0")
    hardware_rev: str = Field(default="revB")
    ip_address: str = Field(default="192.168.10.101")
    mac_address: str = Field(default="00:1B:44:11:3A:B7")
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    telemetry_interval_sec: int = Field(default=10)
    expected_topics: List[str] = Field(default_factory=list)
    allowed_actuators: List[str] = Field(default_factory=list)
    is_virtual: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Gateway(BaseModel):
    id: str = Field(..., description="Edge Gateway ID (e.g. gw-field-alpha)")
    name: str = Field(..., description="Gateway Name")
    zone: str = Field(..., description="Deployment Zone")
    status: str = Field(default="online")
    ip_address: str = Field(default="192.168.10.1")
    connected_device_ids: List[str] = Field(default_factory=list)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    firmware_version: str = Field(default="2.4.1")
