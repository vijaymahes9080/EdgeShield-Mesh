---
document_id: "RB-005"
version: "1.0.1"
title: "Agricultural Actuator & Irrigation Valve Safety Override"
effective_date: "2026-03-05"
source_type: "runbook"
target_systems: ["Irrigation Valves", "Pump Controllers", "Water Main Solenoids"]
---

# RB-005: Agricultural Actuator & Irrigation Valve Safety Override

## 1. Overview and Threat Context
Actuators in smart agriculture regulate water flow, nutrient injection, and high-voltage power. Erroneous or malicious commands (e.g. rapid cycling of latching solenoids or overpressure pump activation) can cause water hammer damage, pipeline rupture, or crop loss.

## 2. Detection Criteria
- **Detector IDs**: `unauthorized_topic`, `impossible_value`, `gateway_disconnect`
- **Severity**: CRITICAL
- **Trigger Condition**: Valve command received without matching scheduled agronomy recipe, or line pressure exceeds 90 PSI.

## 3. Safe Failsafe Protocol
1. **Safety Interlock**: If anomalous behavior is detected, set valve to safe-state (closed) via hardware failsafe timer if pressure exceeds 100 PSI.
2. **Remediation Proposal**: Propose `emergency_valve_failsafe` or `quarantine_device`.
3. **Mandatory Human Verification**: Operator must visually or sensor-verify pipe pressure before resetting safety lockouts.
