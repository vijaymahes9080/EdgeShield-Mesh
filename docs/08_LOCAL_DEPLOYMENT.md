# EdgeShield Mesh — Local & Container Deployment Guide

EdgeShield Mesh supports both zero-daemon standalone Python/Node mode and full containerized deployment with Docker Compose.

---

## 1. Containerized Deployment (Docker Compose)

### Launching All Services

```bash
cd infra/docker
docker compose up --build -d
```

### Container Architecture & Ports

| Service | Container Name | Port Mapping | Function |
|---|---|---|---|
| **Mosquitto** | `edgeshield-mosquitto` | `1883`, `9001` | MQTT Broker with ACL rules |
| **PostgreSQL** | `edgeshield-postgres` | `5432` | Relational & Time-Series store |
| **Qdrant** | `edgeshield-qdrant` | `6333` | Vector Database for RAG embeddings |
| **Ollama** | `edgeshield-ollama` | `11434` | Local LLM inference engine |
| **API** | `edgeshield-api` | `8000` | FastAPI Backend & WebSocket |
| **Web** | `edgeshield-web` | `5173` | React Dashboard |
| **n8n** | `edgeshield-n8n` | `5678` | Incident Notification Automation |

---

## 2. Standalone Zero-Daemon Local Run

If running on developer machines without Docker:

```bash
# Terminal 1: Backend
uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Web Dashboard
cd apps/web
npm run dev
```
The platform automatically falls back to embedded SQLite persistence and fast cosine vector search!
