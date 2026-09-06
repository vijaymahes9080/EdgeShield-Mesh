"""
Attack Simulator and Smart Ag Network Simulation Routes
"""
import json
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from packages.shared.models import (
    UserPublic, AuditAction, RawTelemetry, NormalizedTelemetry,
    Incident, EvidenceItem, IncidentSeverity, IncidentStatus
)
from apps.api.repository import repo
from apps.api.routes.auth import get_current_user
from apps.api.routes.telemetry import ingest_telemetry
from services.attack_simulator.virtual_devices import ag_simulator
from services.attack_simulator.manager import attack_manager

router = APIRouter(prefix="/simulations", tags=["Attack Simulator"])


@router.post("/tick-all-devices")
async def tick_all_devices(current_user: UserPublic = Depends(get_current_user)):
    """
    Generates one realistic normal telemetry reading for each of the 5 virtual agriculture devices.
    """
    results = []
    for dev_id in repo.devices.keys():
        norm = ag_simulator.generate_telemetry_for_device(dev_id)
        raw = RawTelemetry(
            topic=f"edgeshield/{dev_id}/telemetry",
            payload_raw=json.dumps({
                "device_id": norm.device_id,
                "device_type": norm.device_type,
                "zone": norm.zone,
                "seq": norm.seq,
                "nonce": norm.nonce,
                "measurements": norm.measurements,
                "battery_level": norm.battery_level,
                "signal_rssi": norm.signal_rssi,
                "timestamp": norm.timestamp.isoformat()
            })
        )
        res = await ingest_telemetry(raw)
        results.append(res)
    return {"status": "success", "devices_ticked": len(results), "ingestion_results": results}


@router.post("/attack/{vector_name}")
async def trigger_attack(vector_name: str, current_user: UserPublic = Depends(get_current_user)):
    """
    Triggers a reproducible attack vector:
    - replay
    - burst
    - invalid_payload
    - unauthorized_topic
    - timestamp_rollback
    - sensor_spoofing
    - gateway_disconnect
    """
    await repo.log_audit(
        actor=current_user.username,
        actor_role=current_user.role.value,
        action=AuditAction.ATTACK_SIMULATION_STARTED,
        resource_type="attack_vector",
        resource_id=vector_name,
        details={"vector": vector_name}
    )

    if vector_name == "replay":
        p1, p2 = attack_manager.generate_replay_attack()
        r1 = await ingest_telemetry(p1)
        # Small delay to ensure order
        await asyncio.sleep(0.05)
        r2 = await ingest_telemetry(p2)
        return {"vector": vector_name, "packets_sent": 2, "results": [r1, r2]}

    elif vector_name == "burst":
        packets = attack_manager.generate_burst_flood(count=15)
        results = []
        for p in packets:
            results.append(await ingest_telemetry(p))
        return {"vector": vector_name, "packets_sent": len(packets), "results": results}

    elif vector_name == "invalid_payload":
        packet = attack_manager.generate_invalid_payload()
        res = await ingest_telemetry(packet)
        return {"vector": vector_name, "packet": packet.payload_raw, "result": res}

    elif vector_name == "unauthorized_topic":
        dev, topic, packet = attack_manager.generate_unauthorized_topic_attack()
        # Direct detector check
        res = await ingest_telemetry(packet)
        return {"vector": vector_name, "topic": topic, "result": res}

    elif vector_name == "timestamp_rollback":
        packet = attack_manager.generate_timestamp_rollback()
        res = await ingest_telemetry(packet)
        return {"vector": vector_name, "result": res}

    elif vector_name == "sensor_spoofing":
        packet = attack_manager.generate_sensor_spoofing()
        res = await ingest_telemetry(packet)
        return {"vector": vector_name, "result": res}

    elif vector_name == "gateway_disconnect":
        gw_id, last_hb, cur_t = attack_manager.generate_gateway_disconnect()
        return {"vector": vector_name, "gateway_id": gw_id, "status": "simulated_disconnect"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown attack vector '{vector_name}'")
