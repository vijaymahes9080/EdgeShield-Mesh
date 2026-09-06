# EdgeShield Mesh — Quick Start Guide

Welcome to **EdgeShield Mesh**, an open-source agentic cybersecurity platform designed specifically for small and rural IoT deployments (such as smart agriculture, rural water pumping, and remote environmental monitoring).

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** and **npm**
- *(Optional)* **Docker & Docker Compose**

---

## 1. Quick Local Standalone Launch (Zero-Dependency Mode)

EdgeShield Mesh supports instant zero-daemon local execution using embedded SQLite durability and simulated MQTT client streams.

### Step 1: Clone and Set Up Virtual Environment

```bash
git clone https://github.com/vijaymahes9080/EdgeShield-Mesh.git
cd EdgeShield-Mesh

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start the FastAPI Backend

```bash
# In Terminal 1
uvicorn apps.api.main:app --reload --port 8000
```
- Core API: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Prometheus Metrics: `http://localhost:8000/metrics`
- Health Check: `http://localhost:8000/health`

### Step 3: Start the React Dashboard

```bash
# In Terminal 2
cd apps/web
npm install
npm run dev
```
- Dashboard UI: `http://localhost:5173`

---

## 2. Quick Sign-In Credentials

Default accounts pre-configured in the platform:

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Operator** | `operator` | `operator123!` | Remediation approvals, triage, live controls |
| **Administrator** | `admin` | `admin12345!` | Rule threshold tuning, user management, full access |
| **Analyst** | `analyst` | `analyst123!` | Read-only telemetry and incident inspection |

---

## 3. Running Your First Attack Simulation

1. Open the Dashboard at `http://localhost:5173`.
2. Sign in as **Operator**.
3. Click the **Attack Simulator** tab.
4. Click **Inject Attack Vector** on `Replay Attack Vector` or `Sensor Spoofing`.
5. Observe the live detection banner, the **Incident Center** triage cards, and the **Approval Gate** proposal.
6. Review the **Observed Facts vs Derived Findings vs Recommendations** breakdown.
7. Click **Authorize Remediation** with an operator justification note.
8. Inspect the **Audit Ledger** to verify the cryptographic SHA-256 entry.

---

## 4. Running the Automated Evaluation Benchmark

```bash
python tests/evaluation/benchmark_runner.py
```
This runs the 30-scenario test suite and prints detection recall, precision, and compliance metrics.
