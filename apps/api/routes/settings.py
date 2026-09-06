"""
Detection Rules and Threshold Settings Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from packages.shared.models import DetectionRule, UserPublic, UserRole, AuditAction
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user, require_role

router = APIRouter(prefix="/settings", tags=["Settings & Detection Rules"])


@router.get("/rules", response_model=List[DetectionRule])
async def list_rules(current_user: UserPublic = Depends(get_current_user)):
    return list(repo.detection_rules.values())


@router.put("/rules/{rule_id}", response_model=DetectionRule)
async def update_rule(
    rule_id: str,
    update_data: Dict[str, Any],
    current_user: UserPublic = Depends(require_role([UserRole.ADMIN]))
):
    rule = repo.detection_rules.get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")

    if "enabled" in update_data:
        rule.enabled = bool(update_data["enabled"])
    if "parameters" in update_data:
        rule.parameters.update(update_data["parameters"])

    await repo.log_audit(
        actor=current_user.username,
        actor_role=current_user.role.value,
        action=AuditAction.SETTINGS_UPDATED,
        resource_type="detection_rule",
        resource_id=rule_id,
        details=update_data
    )
    return rule
