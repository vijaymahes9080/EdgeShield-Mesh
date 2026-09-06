"""
EdgeShield Mesh - FastAPI Core Application Entrypoint
Production-ready cybersecurity server with secure headers, CORS, metrics,
live WebSockets, and background virtual IoT network generator.
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api.repository import repo
from services.agent_orchestrator.rag.retriever import rag_retriever
from apps.api.routes.auth import router as auth_router
from apps.api.routes.devices import router as devices_router
from apps.api.routes.telemetry import router as telemetry_router, ingest_telemetry
from apps.api.routes.incidents import router as incidents_router
from apps.api.routes.approvals import router as approvals_router
from apps.api.routes.audit import router as audit_router
from apps.api.routes.simulations import router as sim_router
from apps.api.routes.settings import router as settings_router
from apps.api.routes.metrics import router as metrics_router
from services.attack_simulator.virtual_devices import ag_simulator
from packages.shared.models import RawTelemetry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("edgeshield.api")


# Background worker for continuous Smart Ag simulated network
async def background_virtual_iot_worker():
    logger.info("Starting background Smart Ag virtual IoT telemetry loop...")
    await asyncio.sleep(2)
    while True:
        try:
            for dev_id in list(repo.devices.keys()):
                norm = ag_simulator.generate_telemetry_for_device(dev_id)
                raw = RawTelemetry(
                    topic=f"edgeshield/{dev_id}/telemetry",
                    payload_raw=norm.model_dump_json(),
                    source_ip="192.168.10.100"
                )
                await ingest_telemetry(raw)
            await asyncio.sleep(12)  # Tick every 12 seconds
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in virtual IoT worker: {e}")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing EdgeShield Mesh Repository & RAG Index...")
    await repo.initialize()
    rag_retriever.reload()
    logger.info(f"Loaded {len(rag_retriever.chunks)} runbook chunks into RAG index.")

    worker_task = asyncio.create_task(background_virtual_iot_worker())
    yield
    # Shutdown
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("EdgeShield Mesh shutdown complete.")


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app = FastAPI(
    title="EdgeShield Mesh API",
    description="Agentic cybersecurity platform for small and rural IoT deployments.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for local dev & dashboard access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

# Include Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(devices_router, prefix="/api/v1")
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(approvals_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(sim_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(metrics_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to EdgeShield Mesh Agentic IoT Security Platform",
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics"
    }
