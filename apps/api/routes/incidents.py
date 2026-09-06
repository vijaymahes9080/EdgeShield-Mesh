"""
Incident Management & Evidence Grounding Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from packages.shared.models import Incident, IncidentSeverity, IncidentStatus, UserPublic
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user
from services.agent_orchestrator.pipeline import agent_orchestrator

router = APIRouter(prefix="/incidents", tags=["Incident Management"])


@router.get("", response_model=List[Incident])
async def list_incidents(
    severity: Optional[IncidentSeverity] = None,
    status: Optional[IncidentStatus] = None,
    device_id: Optional[str] = None,
    limit: int = 50,
    current_user: UserPublic = Depends(get_current_user)
):
    incidents = await repo.list_incidents(limit=limit)
    if severity:
        incidents = [i for i in incidents if i.severity == severity]
    if status:
        incidents = [i for i in incidents if i.status == status]
    if device_id:
        incidents = [i for i in incidents if i.device_id == device_id]
    return incidents


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str, current_user: UserPublic = Depends(get_current_user)):
    incident = await repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return incident


@router.post("/{incident_id}/analyze")
async def trigger_agent_analysis(incident_id: str, current_user: UserPublic = Depends(get_current_user)):
    try:
        result = await agent_orchestrator.execute_incident_workflow(incident_id)
        return {"status": "analysis_completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")
