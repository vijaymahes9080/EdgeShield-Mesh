"""
Immutable Audit Ledger Query Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from packages.shared.models import AuditEvent, UserPublic
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Ledger"])


@router.get("", response_model=List[AuditEvent])
async def get_audit_log(
    resource_id: Optional[str] = None,
    limit: int = 100,
    current_user: UserPublic = Depends(get_current_user)
):
    return await repo.get_audit_log(resource_id=resource_id, limit=limit)
