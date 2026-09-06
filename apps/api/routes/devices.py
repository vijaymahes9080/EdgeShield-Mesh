"""
Device Inventory and Health Summary Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from packages.shared.models import Device, DeviceStatus, UserRole, UserPublic
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user, require_role

router = APIRouter(prefix="/devices", tags=["Device Inventory"])


@router.get("", response_model=List[Device])
async def list_devices(current_user: UserPublic = Depends(get_current_user)):
    return list(repo.devices.values())


@router.get("/health-summary")
async def get_health_summary(current_user: UserPublic = Depends(get_current_user)):
    devices = list(repo.devices.values())
    total = len(devices)
    active = sum(1 for d in devices if d.status == DeviceStatus.ACTIVE)
    warning = sum(1 for d in devices if d.status == DeviceStatus.WARNING)
    isolated = sum(1 for d in devices if d.status == DeviceStatus.ISOLATED)
    offline = sum(1 for d in devices if d.status == DeviceStatus.OFFLINE)

    return {
        "total_devices": total,
        "active": active,
        "warning": warning,
        "isolated": isolated,
        "offline": offline,
        "healthy_percentage": round((active / total * 100), 1) if total > 0 else 100.0,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str, current_user: UserPublic = Depends(get_current_user)):
    dev = repo.devices.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")
    return dev


@router.post("", response_model=Device)
async def register_device(
    device: Device,
    current_user: UserPublic = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    repo.devices[device.id] = device
    return device
