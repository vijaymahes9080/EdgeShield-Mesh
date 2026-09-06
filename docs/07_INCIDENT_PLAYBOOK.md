# EdgeShield Mesh — Incident Response Playbook & Standard Operating Procedures

This playbook guides agricultural operations managers and cybersecurity analysts through evaluating, verifying, and authorizing remediation proposals.

---

## 1. Incident Triage Workflow

```
[Threat Detected] ---> [Agent RAG Analysis] ---> [Proposal Generated] ---> [Operator Review] ---> [Sign / Execute]
```

### Step 1: Review Incident Card
- Check **Severity** (CRITICAL, HIGH, MEDIUM, LOW) and **Confidence Score**.
- Verify the **Target Device** and physical **Location Zone**.

### Step 2: Inspect Observed Facts vs Derived Findings
- Ensure the **Observed Facts** are backed by physical telemetry readings or packet logs.
- Review **Derived Findings** to understand the suspected threat vector (e.g. Replay attack, sensor spoofing, burst rate).

### Step 3: Verify RAG Citations
- Click citation cards to inspect the underlying Standard Operating Procedure (e.g. `RB-001: MQTT Unauthorized Topic Response`, `RB-002: Sensor Spoofing Response`).

### Step 4: Authorize Remediation via Approval Gate
- Navigate to the **Approval Gate**.
- Review the proposed action (e.g. `quarantine_device`, `revoke_topic_permission`, `rate_limit_device`).
- Enter a mandatory **Justification Rationale**.
- Click **Authorize Remediation** or **Reject Proposal**.
- Verify the cryptographic signature in the **Audit Ledger**.
