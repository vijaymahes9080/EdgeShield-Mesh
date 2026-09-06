---
document_id: "RB-002"
version: "1.2.0"
title: "Sensor Spoofing and Physically Impossible Telemetry Values"
effective_date: "2026-02-01"
source_type: "runbook"
target_systems: ["Soil Probes", "Weather Stations", "Greenhouse Sensors"]
---

# RB-002: Sensor Spoofing and Physically Impossible Telemetry Values

## 1. Overview and Threat Context
Sensor spoofing occurs when an attacker manipulates physical inputs or injects forged telemetry values to deceive automated control systems (e.g. injecting 0% soil moisture to trigger constant over-irrigation, or reporting 500°C in a greenhouse to trip emergency shutoffs).

## 2. Detection Criteria
- **Detector ID**: `impossible_value`
- **Severity**: HIGH
- **Trigger Condition**: Measurement exceeds physical sensor bounds (e.g., Soil Moisture > 100% or < 0%, Solar Irradiance > 1500 W/m², Battery Level > 100% or < 0%, Temperature < -50°C or > 80°C).

## 3. Investigation Protocol
1. **Fact vs Finding Separation**:
   - Fact: Observed sensor measurement $X$ outside known physical range $[\min, \max]$.
   - Finding: Sensor probe hardware fault, open-circuit voltage spike, or deliberate packet forgery.
2. **Telemetry Cross-Reference**:
   - Compare with neighboring nodes in the same physical zone (e.g. Zone A soil probes).
   - Check if battery voltage or RSSI dropped sharply, indicating sensor brownout.

## 4. Recommended Remediation
- Propose `recalibrate_sensor` or temporary sensor data masking in downstream control loops.
- Avoid automatic valve closures if agricultural crop survival depends on irrigation; human verification is mandatory.
- Dispatch field technician to inspect physical sensor wiring and probe resistance.
