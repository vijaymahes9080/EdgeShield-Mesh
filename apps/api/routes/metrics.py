"""
Prometheus Metrics and Health Check Routes
"""
from fastapi import APIRouter, Response
from datetime import datetime, timezone
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from apps.api.repository import repo

router = APIRouter(tags=["Observability & Health"])

# Prometheus Metrics definitions
TELEMETRY_INGESTED_TOTAL = Counter(
    "edgeshield_telemetry_ingested_total",
    "Total count of telemetry events ingested",
    ["device_type", "zone"]
)
ANOMALIES_DETECTED_TOTAL = Counter(
    "edgeshield_anomalies_detected_total",
    "Total count of anomalies detected",
    ["detector_id", "severity"]
)
INCIDENTS_ACTIVE = Gauge(
    "edgeshield_incidents_active",
    "Current active incidents in the system"
)
PROPOSALS_PENDING = Gauge(
    "edgeshield_proposals_pending",
    "Current remediation proposals awaiting human approval"
)


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "EdgeShield Mesh Core API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "devices_online": len(repo.devices),
        "incidents_count": len(repo.incidents)
    }


@router.get("/metrics")
async def get_metrics():
    # Update gauge values
    active_inc = sum(1 for i in repo.incidents.values() if i.status.value in ["detected", "investigating", "pending_approval"])
    INCIDENTS_ACTIVE.set(active_inc)
    pending_prop = sum(1 for p in repo.proposals.values() if p.status.value == "pending")
    PROPOSALS_PENDING.set(pending_prop)

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
