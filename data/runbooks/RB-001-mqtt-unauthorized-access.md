---
document_id: "RB-001"
version: "1.4.0"
title: "MQTT Unauthorized Topic and Rogue Publication Response"
effective_date: "2026-01-15"
source_type: "runbook"
target_systems: ["Mosquitto Broker", "Edge Gateway", "All IoT Endpoints"]
---

# RB-001: MQTT Unauthorized Topic and Rogue Publication Response

## 1. Overview and Threat Context
In agricultural and rural mesh networks, sensor nodes (such as soil moisture probes or weather sensors) should only publish telemetry on designated read-only topics (e.g., `edgeshield/{device_id}/telemetry`). An unauthorized publish event indicates either a firmware compromise, credential leakage, or an adversary attempting command injection into actuator control topics (such as `edgeshield/valve-controller-01/cmd/state`).

## 2. Detection Criteria
- **Detector ID**: `unauthorized_topic`
- **Severity**: HIGH to CRITICAL
- **Trigger Condition**: Any MQTT `PUBLISH` packet originating from a device ID where the topic is outside the device's ACL profile or targets an actuator command topic.

## 3. Immediate Containment Procedure
1. **Never Execute Automated Network Severing Without Operator Review**: Verify if the anomaly is due to a misconfigured deployment or an active exploit.
2. **Propose Remediation Action**:
   - Propose `revoke_topic_permission` or `quarantine_device`.
   - Action scope: `device:{device_id}:network_isolation`
   - Rollback procedure: Re-enable device ACL in gateway rules and restart client TLS session.
3. **Operator Verification Steps**:
   - Check device IP and source MAC address against physical inventory.
   - Inspect the unauthorized payload for injection payloads or shell commands.

## 4. Remediation and Post-Incident Recovery
- Rotate the MQTT client credentials or mTLS certificate for the compromised endpoint.
- Verify gateway firewall rules.
- Review audit logs for subsequent lateral movement attempts.
