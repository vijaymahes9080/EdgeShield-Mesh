"""
Telemetry Ingestion and Live WebSocket Streaming
"""
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List, Optional, Set
from datetime import datetime, timezone
from packages.shared.models import (
    RawTelemetry, NormalizedTelemetry, Incident, EvidenceItem, IncidentSeverity,
    IncidentStatus, UserPublic, AuditAction
)
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user
from services.ingestion.validator import TelemetryValidator
from services.detection_engine.engine import detection_engine
from services.agent_orchestrator.pipeline import agent_orchestrator

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion & Stream"])
validator = TelemetryValidator()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_json(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(data, default=str))
            except Exception:
                self.active_connections.discard(connection)


ws_manager = ConnectionManager()


@router.get("/history", response_model=List[NormalizedTelemetry])
async def get_telemetry_history(
    device_id: Optional[str] = None,
    limit: int = 50,
    current_user: UserPublic = Depends(get_current_user)
):
    return await repo.get_recent_telemetry(device_id=device_id, limit=limit)


@router.post("/ingest")
async def ingest_telemetry(raw: RawTelemetry):
    """
    Ingests raw telemetry, validates schema, processes detectors,
    creates incidents if anomalies are detected, and broadcasts live.
    """
    # 1. Validation & normalization
    val_res = validator.validate_and_normalize(raw)
    if not val_res.is_valid or not val_res.normalized:
        return {"status": "rejected", "errors": val_res.errors}

    telemetry = val_res.normalized
    device = repo.devices.get(telemetry.device_id)

    # 2. Add to telemetry history
    await repo.add_telemetry(telemetry)

    # 3. Evaluate detectors
    detector_results = detection_engine.evaluate_telemetry(telemetry, device)
    created_incidents = []

    for res in detector_results:
        # Create correlated incident
        evidence = EvidenceItem(
            evidence_type="telemetry_anomaly",
            source=res.detector_id,
            data=res.observed_fields,
            description=res.explanation
        )

        incident = Incident(
            title=f"{res.detector_id.replace('_', ' ').title()} on {telemetry.device_id}",
            device_id=telemetry.device_id,
            detector_id=res.detector_id,
            severity=res.severity,
            status=IncidentStatus.DETECTED,
            confidence=res.confidence,
            observed_facts=[res.explanation],
            derived_findings=[f"Confidence: {res.confidence * 100:.0f}%"],
            recommendations=[res.recommended_next_step],
            evidence_items=[evidence]
        )
        await repo.save_incident(incident)

        # Trigger 11-step Agent Orchestrator in background task
        asyncio.create_task(agent_orchestrator.execute_incident_workflow(incident.id))
        created_incidents.append(incident.id)

    # 4. Broadcast live telemetry and incidents via WebSocket
    await ws_manager.broadcast_json({
        "type": "telemetry",
        "data": telemetry.model_dump(),
        "anomalies_detected": len(detector_results),
        "incidents_created": created_incidents
    })

    return {
        "status": "ingested",
        "event_id": telemetry.event_id,
        "anomalies_count": len(detector_results),
        "incidents": created_incidents
    }


@router.websocket("/ws")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keepalive receiver
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "time": datetime.now(timezone.utc).isoformat()}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
