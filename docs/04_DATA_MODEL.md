# EdgeShield Mesh — Data Model & Entity Schema Dictionary

This document details the core data entities, relationships, and persistence schemas used across EdgeShield Mesh.

---

## 1. Entity-Relationship Diagram

```
+-------------------+             +-----------------------+
|      Device       | 1         * |  NormalizedTelemetry  |
+-------------------+-------------+-----------------------+
| id (PK)           |             | event_id (PK)         |
| name              |             | device_id (FK)        |
| device_type       |             | timestamp             |
| zone              |             | seq                   |
| status            |             | nonce                 |
| firmware_version  |             | payload_hash          |
| last_seen         |             | measurements (JSON)   |
+-------------------+             +-----------------------+
          |
          | 1
          |
          | *
+-------------------+ 1         * +-----------------------+
|     Incident      |-------------|     EvidenceItem      |
+-------------------+             +-----------------------+
| id (PK)           |             | id (PK)               |
| device_id (FK)    |             | incident_id (FK)      |
| detector_id       |             | evidence_type         |
| severity          |             | source                |
| confidence        |             | data (JSON)           |
| observed_facts    |             | description           |
| derived_findings  |             +-----------------------+
| recommendations   |
+-------------------+
          | 1
          |
          | 1
+-------------------+ 1         1 +-----------------------+
|RemediationProposal|-------------|       Approval        |
+-------------------+             +-----------------------+
| id (PK)           |             | id (PK)               |
| incident_id (FK)  |             | proposal_id (FK)      |
| action_type       |             | status                |
| target_device_id  |             | actor_username        |
| scope             |             | reason (Mandatory)    |
| rollback_procedure|             | idempotency_key (UQ)  |
| requires_approval |             | action_taken_at       |
+-------------------+             +-----------------------+

+-------------------+
|    AuditEvent     | (Hash-Chained)
+-------------------+
| event_id (PK)     |
| timestamp         |
| actor             |
| actor_role        |
| action            |
| resource_id       |
| prev_hash         |
| entry_hash (SHA)  |
+-------------------+
```

---

## 2. Entity Descriptions

- **Device**: Physical or virtual IoT node identity, firmware baseline, zone, and allowed MQTT topics.
- **NormalizedTelemetry**: Scrubbed, validated, and timestamp-normalized time-series sensor readings.
- **Incident**: Correlated threat detection with Observed Facts, Derived Findings, and Recommendations.
- **EvidenceItem**: Specific data points, hashes, or metric readings supporting an incident claim.
- **RemediationProposal**: Structured containment proposal requiring human authorization.
- **Approval**: Immutable record of operator authorization or rejection with justification rationale.
- **AuditEvent**: SHA-256 hash-chained immutable security event ledger.
