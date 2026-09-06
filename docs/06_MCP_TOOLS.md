# EdgeShield Mesh — Model Context Protocol (MCP) Tool Catalog

EdgeShield Mesh implements the official Model Context Protocol (MCP) Python SDK, allowing AI agents to query contextual IoT telemetry, verify behavior baselines, and propose safe remediation actions with strict schema boundaries.

---

## 1. Tool Catalog Summary

| Tool Name | Type | Access Level | Description |
|---|---|---|---|
| `get_device_profile` | Read-Only | Public / Agent | Queries hardware specs, firmware version, and allowed topic ACLs |
| `query_recent_telemetry` | Read-Only | Public / Agent | Fetches normalized time-series telemetry events for a device |
| `compare_behavior_baseline` | Read-Only | Public / Agent | Computes multi-sigma statistical Z-score against rolling EWMA |
| `inspect_mqtt_permissions` | Read-Only | Public / Agent | Evaluates whether a candidate MQTT topic violates device ACLs |
| `check_firmware_risk` | Read-Only | Public / Agent | Cross-references firmware version against known CVE database |
| `create_incident_report` | Read-Only | Public / Agent | Generates markdown summary with citations and evidence |
| `propose_safe_remediation` | Write / Proposal | **HITL Protected** | Registers containment proposal with Approval Gate |
| `get_audit_events` | Read-Only | Analyst / Admin | Fetches immutable audit logs and cryptographic hashes |

---

## 2. Safety Boundaries & Non-Negotiable Controls

1. **No Arbitrary Execution**: Tools have strictly validated Pydantic models. Shell execution, file creation outside repository, and URL fetching are blocked.
2. **Read-Only / Proposal Separation**: The agent can inspect telemetry and compare baselines autonomously, but any disruptive remediation action is registered as `requires_approval: true` and routed to the Human Approval Gate.
3. **Audit Logging**: Every invocation of an MCP tool produces an `AuditEvent` in the cryptographic ledger.
