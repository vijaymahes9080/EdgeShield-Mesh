"""
Telemetry Models (Raw vs Normalized)
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field


class RawTelemetry(BaseModel):
    raw_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    payload_raw: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_ip: Optional[str] = "127.0.0.1"
    byte_size: int = 0


class SensorMeasurement(BaseModel):
    name: str
    value: float | int | bool | str
    unit: Optional[str] = None


class NormalizedTelemetry(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    device_type: str
    zone: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    seq: int = 0
    nonce: str = ""
    payload_hash: str = ""
    battery_level: Optional[float] = None
    signal_rssi: Optional[int] = None
    measurements: Dict[str, Any] = Field(default_factory=dict)
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_id: Optional[str] = None


class TelemetryValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    normalized: Optional[NormalizedTelemetry] = None
