"""
Integration Tests for FastAPI Endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.repository import repo


@pytest.mark.asyncio
async def test_api_full_flow():
    await repo.initialize()
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

        # 2. Login as Operator
        res_login = await client.post("/api/v1/auth/login", json={
            "username": "operator",
            "password": "operator123!"
        })
        assert res_login.status_code == 200
        token_data = res_login.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Check /me
        res_me = await client.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["username"] == "operator"

        # 4. List Devices
        res_devs = await client.get("/api/v1/devices", headers=headers)
        assert res_devs.status_code == 200
        assert len(res_devs.json()) >= 5

        # 5. Ingest normal telemetry
        res_ingest = await client.post("/api/v1/telemetry/ingest", json={
            "topic": "edgeshield/soil-sensor-01/telemetry",
            "payload_raw": '{"device_id":"soil-sensor-01","measurements":{"soil_moisture_pct":32.0}}'
        })
        assert res_ingest.status_code == 200
        assert res_ingest.json()["status"] == "ingested"

        # 6. Trigger attack simulation (replay)
        res_atk = await client.post("/api/v1/simulations/attack/replay", headers=headers)
        assert res_atk.status_code == 200
        assert res_atk.json()["vector"] == "replay"

        # 7. Query Incidents
        res_inc = await client.get("/api/v1/incidents", headers=headers)
        assert res_inc.status_code == 200
        incidents = res_inc.json()
        assert len(incidents) >= 1

        # 8. Query Prometheus Metrics
        res_metrics = await client.get("/metrics")
        assert res_metrics.status_code == 200
        assert "edgeshield_" in res_metrics.text
