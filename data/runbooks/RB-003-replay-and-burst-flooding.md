---
document_id: "RB-003"
version: "1.1.0"
title: "Replay Attack, Timestamp Rollback, and Burst Rate Flooding"
effective_date: "2026-02-10"
source_type: "runbook"
target_systems: ["MQTT Broker", "Ingestion Gateway", "All Nodes"]
---

# RB-003: Replay Attack, Timestamp Rollback, and Burst Rate Flooding

## 1. Overview and Threat Context
Replay attacks involve re-transmitting previously recorded telemetry messages to maintain a falsified network state. Burst rate flooding attempts to exhaust gateway CPU, memory, or battery power of constrained mesh repeaters (Denial of Service).

## 2. Detection Criteria
- **Detector IDs**: `duplicate_message`, `timestamp_rollback`, `burst_rate`
- **Severity**: MEDIUM to HIGH
- **Trigger Conditions**:
  - `duplicate_message`: Incoming packet SHA-256 payload hash matches an already processed message within the deduplication cache window.
  - `timestamp_rollback`: Incoming telemetry timestamp $t_{new} < t_{max} - \Delta_{tolerance}$ (historical timestamp injection).
  - `burst_rate`: Telemetry frequency exceeds 10 msg/sec or $5\times$ nominal reporting interval for the given device type.

## 3. Mitigation Protocol
1. **Drop and Flag**: Ingestion pipeline drops replayed packets and increments the anomaly counter.
2. **Rate Limiting**: Propose `rate_limit_device` on the edge gateway firewall to throttle rogue publishers to $\le 1$ packet/min.
3. **Nonce / Sequence Validation**: Review whether the device firmware sequence counter was reset or spoofed.
4. **Human Approval**: Any network-level rate limiting or IP banning must be verified by the on-duty farm/security operator.
