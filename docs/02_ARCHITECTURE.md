# EdgeShield Mesh — Architecture & Deep Technical Design

EdgeShield Mesh is structured into decoupled, loosely-coupled layers designed for low-bandwidth rural operations, offline edge resilience, and high-assurance AI governance.

---

## 1. High-Level Architectural Diagram

```
+---------------------------------------------------------------------------------+
|                                Rural IoT Edge                                   |
|  [Soil Probes]  [Weather Tower]  [Valve Actuators]  [Solar MPPT]  [Greenhouse]  |
|                                         |                                       |
|                                 (MQTT / LoRa Link)                              |
|                                         v                                       |
|                              [Mosquitto Broker + ACLs]                          |
+-----------------------------------------+---------------------------------------+
                                          |
                                          v
+---------------------------------------------------------------------------------+
|                             Edge Gateway & Ingestion                            |
|   - 64KB Payload Size Boundary                                                  |
|   - Deduplication & Nonce Window Cache (SHA-256)                                |
|   - Timestamp Rollback Guard                                                    |
|   - Physical Sensor Bounds & Range Checker                                      |
+-----------------------------------------+---------------------------------------+
                                          |
                                          v
+---------------------------------------------------------------------------------+
|                        Deterministic & Statistical Detectors                    |
|   [Dup Msg] [Rollback] [Burst Rate] [Impossible Value] [Silence] [Topic ACL]    |
|   [Firmware CVE Risk] [Gateway Disconnect] [Rolling EWMA Multi-Sigma Drift]     |
+-----------------------------------------+---------------------------------------+
                                          |
                               (Incident Triggered)
                                          v
+---------------------------------------------------------------------------------+
|                     11-Step Evidence-Grounded Agent Orchestrator                |
|   - Incident Context Assembly                                                   |
|   - RAG Semantic Chunk Retrieval (Local Vector Store / Qdrant)                  |
|   - Prompt Injection Isolation & PII Redaction Layer                            |
|   - Structured Breakdown: Facts | Findings | Recommendations                    |
|   - Safe Remediation Proposal Generation (Strict requires_approval: true)       |
+-----------------------------------------+---------------------------------------+
                                          |
                                          v
+---------------------------------------------------------------------------------+
|                    Control Plane & Human-In-The-Loop Approval Gate              |
|   - FastAPI REST & Live Streaming WebSocket Server                              |
|   - JWT Authentication & RBAC (Admin, Operator, Analyst)                        |
|   - Idempotent Approval Ledger (Cryptographic SHA-256 Hash Chained)             |
|   - Official Python MCP Server (8 Strictly Typed Schema Tools)                  |
|   - n8n Webhook & Notification Engine                                           |
+---------------------------------------------------------------------------------+
```

---

## 2. Layer Specifications

### Ingestion Tier (`services/ingestion`)
- **Message Size Limits**: Drops any packet exceeding 64KB before parsing.
- **Deduplication**: Hashes `(device_id, seq, nonce, measurements)` via SHA-256 and checks sliding 60s TTL memory cache.
- **Normalization**: Standardizes timestamps to ISO 8601 UTC and separates `RawTelemetry` from `NormalizedTelemetry`.

### Detection Tier (`services/detection_engine`)
- **Deterministic**: 8 specialized detectors providing machine-readable explanations with $O(1)$ lookup complexity.
- **Statistical Baseline**: Computes rolling mean, standard deviation, and Exponentially Weighted Moving Average (EWMA) with smoothing factor $\alpha=0.2$ and flags deviations where $Z \ge 3.0$.

### RAG & Evidence Grounding Tier (`services/agent_orchestrator/rag`)
- **Corpus**: Indexes markdown runbooks, IoT manuals, and operating procedures with SHA-256 chunk integrity hashing.
- **Citation Extraction**: Emits exact text snippets, document IDs, semantic versions, sections, and relevance scores.

### Agent Orchestrator (`services/agent_orchestrator`)
- Strictly enforces **Rule #3**: Separates *Observed Facts*, *Derived Findings*, and *Recommendations*.
- Strictly enforces **Rule #4**: Zero autonomous disruptive actions. All high-impact remediations register with the **Approval Gate** as `PENDING`.

### MCP Server (`services/mcp_server`)
- Official Python MCP SDK implementation exposing 8 strictly typed schemas.
- Rejects unbounded shell execution, arbitrary URL fetching, and unsanitized parameters.
