# EdgeShield Mesh

> **Agentic Cybersecurity Platform for Small, Rural, and Satellite-Linked IoT Deployments**

[![CI & Security Scanning](https://github.com/vijaymahes9080/EdgeShield-Mesh/actions/workflows/ci.yml/badge.svg)](https://github.com/vijaymahes9080/EdgeShield-Mesh/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-cyan.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18.2+-blue.svg)](https://react.dev/)
[![Quality Gate: PASSED](https://img.shields.io/badge/Quality%20Gate-PASSED-brightgreen.svg)](docs/10_EVALUATION_REPORT.md)

---

## Mission & Problem Statement

Rural farms, irrigation networks, community microgrids, and remote environmental sensor arrays frequently operate with weak security controls, outdated microcode, poor connectivity, and no dedicated Security Operations Center (SOC) team.

**EdgeShield Mesh** provides an open-source, agentic cybersecurity copilot that:
1. Ingests and inspects MQTT telemetry streams at the edge with strict 64KB bounds.
2. Detects anomalous, replayed, spoofed, and unauthorized topic publications in real-time.
3. Explains incidents using evidence-grounded Retrieval-Augmented Generation (RAG) over verified IoT runbooks.
4. Exposes 8 secure Model Context Protocol (MCP) tools for agentic investigation.
5. **Enforces a strict Human-In-The-Loop (HITL) approval gate** before executing any high-impact remediation action.

---

## Architectural Overview

```mermaid
flowchart TD
    subgraph IoT_Edge ["Smart Agriculture Edge Network"]
        D1["Soil Moisture Alpha (v1.2.0)"]
        D2["Weather Station Beta (v2.0.1)"]
        D3["Irrigation Valve Gamma (v1.1.0)"]
        D4["Solar Pump Delta (v1.0.4)"]
        D5["Greenhouse Env Epsilon (v0.9.1)"]
        ATK["Attack Simulator (7 vectors)"]
    end

    subgraph Gateway_Ingestion ["Ingestion & Edge Gateway"]
        BROKER["Mosquitto MQTT Broker"]
        GATEWAY["Edge Gateway & Ingestion Worker"]
        VAL["Validation & Normalization Engine\n(Dedup, Replay, Rate, Range)"]
    end

    subgraph Data_Tier ["Persistence & Vector Tier"]
        DB[("PostgreSQL / SQLite Database\n(Telemetry, Incidents, Audits, Approvals)")]
        VDB[("Qdrant / Vector Store\n(Runbooks, Device Manuals, CVEs)")]
    end

    subgraph Detection_Engine ["Detection Engine"]
        DET_DET["8 Deterministic Detectors\n(Dup, Rollback, Burst, Impossible, Silence,\nUnauthorized Topic, Firmware Risk, Disconnect)"]
        STAT_DET["Statistical Baseline Detector\n(Rolling Mean, StdDev, EWMA Thresholds)"]
    end

    subgraph Agentic_Core ["Agent Orchestrator & MCP"]
        ORCH["Incident Response Agent (11-Step Pipeline)"]
        RAG["Evidence-Grounded RAG Engine"]
        MCP["Model Context Protocol (MCP) Server\n(8 Strict-Schema IoT Security Tools)"]
    end

    subgraph Control_Plane ["API & Human-In-The-Loop"]
        API["FastAPI REST & WebSocket Server"]
        AUTH["JWT Authentication & RBAC"]
        GATE["Approval Gate & Audit Ledger"]
    end

    subgraph Frontends ["UI & Notifications"]
        WEB["React + Vite + Tailwind Cyber Dashboard"]
        N8N["n8n Alert & Webhook Automation"]
    end

    D1 & D2 & D3 & D4 & D5 & ATK -->|MQTT Pub/Sub| BROKER
    BROKER --> GATEWAY --> VAL
    VAL --> DB
    VAL --> DET_DET & STAT_DET
    DET_DET & STAT_DET -->|Trigger Incident| ORCH
    ORCH <--> RAG <--> VDB
    ORCH <--> MCP
    ORCH -->|Propose Remediation| GATE
    GATE --> DB
    API <--> DB & GATE & VDB
    WEB <-->|REST + Live WS| API
    API -->|High Severity Webhook| N8N
```

---

## Non-Negotiable AI Safety Controls

1. **Zero Disruptive Autonomous Actions**: The AI agent is strictly an **advisor**. Disruptive actions (e.g. device isolation, topic revocation, failsafe valve trips) can **never** execute without explicit, authenticated operator approval.
2. **Untrusted Data Isolation**: Telemetry payloads, device metadata, topic names, and log streams are quarantined and never executed as prompt instructions.
3. **Structured Explanation**: Every incident report strictly separates:
   - **Observed Facts** (Raw empirical data)
   - **Derived Findings** (Logical conclusions & threat vectors)
   - **Recommendations** (Actionable SOP steps)
4. **Cryptographic Audit Ledger**: All decisions, approvals, and tool invocations are committed to an immutable SHA-256 hash-chained ledger.

---

## 30-Scenario Evaluation Benchmark Results

| Metric | Target | Benchmark Result | Status |
|---|---|---|---|
| **Attack Detection Recall** | $\ge 85.0\%$ | **100.0%** (10/10 attacks detected) | **PASSED** |
| **Detection Precision** | $\ge 85.0\%$ | **100.0%** | **PASSED** |
| **False-Positive Rate (FPR)** | $\le 15.0\%$ | **0.0%** (15/15 clean negatives) | **PASSED** |
| **Mean Time to Detection (MTTD)** | $< 60\text{ s}$ | **$< 1.0\text{ ms}$** | **PASSED** |
| **Citation Coverage (RAG Grounding)** | $\ge 95.0\%$ | **100.0%** | **PASSED** |
| **Unsupported Recommendation Rate** | $< 5.0\%$ | **0.0%** | **PASSED** |
| **Unauthorized Action Rate** | **STRICT 0.0%** | **0.0%** | **PASSED** |
| **Approval Gate Compliance** | **100.0%** | **100.0%** | **PASSED** |
| **Prompt Injections Quarantined** | $100.0\%$ | **100.0%** (5/5 neutralized) | **PASSED** |
| **P95 Ingestion & Check Latency** | $< 100\text{ ms}$ | **$< 5.0\text{ ms}$** | **PASSED** |

---

## Quick Start Guide

### 1. Install & Launch Backend

```bash
# Clone the repository
git clone https://github.com/vijaymahes9080/EdgeShield-Mesh.git
cd EdgeShield-Mesh

# Install Python requirements
pip install -r requirements.txt

# Start FastAPI Backend Server
uvicorn apps.api.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Prometheus Metrics: `http://localhost:8000/metrics`
- Health Check: `http://localhost:8000/health`

### 2. Launch Web Dashboard

```bash
cd apps/web
npm install
npm run dev
```
- Dashboard UI: `http://localhost:5173`

### 3. Run Test Suite & Benchmark

```bash
# Run all unit and integration tests (29 tests)
pytest tests/ -v

# Run 30-scenario evaluation benchmark
python tests/evaluation/benchmark_runner.py
```

---

## Documentation Index

- [01. Quick Start Guide](docs/01_QUICKSTART.md)
- [02. Architecture & Deep Technical Design](docs/02_ARCHITECTURE.md)
- [03. STRIDE Threat Model](docs/03_THREAT_MODEL.md)
- [04. Data Model & Entity Dictionary](docs/04_DATA_MODEL.md)
- [05. MQTT Topic Security & ACL Model](docs/05_MQTT_SECURITY.md)
- [06. MCP Tool Catalog](docs/06_MCP_TOOLS.md)
- [07. Incident Response Playbook](docs/07_INCIDENT_PLAYBOOK.md)
- [08. Local & Container Deployment Guide](docs/08_LOCAL_DEPLOYMENT.md)
- [09. CI/CD & Security Tooling Guide](docs/09_CI_CD_GUIDE.md)
- [10. Evaluation Benchmark Report](docs/10_EVALUATION_REPORT.md)
- [11. Responsible AI Use & Safety Controls](docs/11_RESPONSIBLE_USE.md)
- [12. Contributing Guidelines](docs/12_CONTRIBUTING.md)

---

## Author & Developer

- **Lead Architect:** Vijay Mahes ([@vijaymahes9080](https://github.com/vijaymahes9080))
- **Email:** `Vijaypradhap2004@gmail.com`
- **License:** [MIT License](LICENSE)
