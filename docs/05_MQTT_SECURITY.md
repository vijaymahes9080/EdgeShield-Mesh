# EdgeShield Mesh — MQTT Topic Security Model & ACL Architecture

EdgeShield Mesh uses a strict hierarchical topic structure and deny-by-default Access Control Lists (ACLs) to isolate device roles and prevent lateral movement across the mesh.

---

## 1. Topic Hierarchy Taxonomy

```
edgeshield/
  +-- {device_id}/
        +-- telemetry      (Sensors publish periodic measurements)
        +-- status         (Online/offline heartbeat and battery status)
        +-- cmd/           (Restricted command topic for actuators only)
              +-- state    (Valve Open/Close, Pump Inverter Start/Stop)
```

---

## 2. Principle of Least Privilege

- **Sensor Endpoints** (e.g. `soil-sensor-01`, `weather-station-01`):
  - `PUBLISH`: `edgeshield/{device_id}/telemetry`, `edgeshield/{device_id}/status`
  - `SUBSCRIBE`: None (Read-only sensors)
- **Actuator Endpoints** (e.g. `valve-controller-01`, `solar-pump-01`):
  - `PUBLISH`: `edgeshield/{device_id}/telemetry`, `edgeshield/{device_id}/status`
  - `SUBSCRIBE`: `edgeshield/{device_id}/cmd/#` (Authorized commands only)
- **Edge Gateway / Ingestion Pipeline**:
  - `SUBSCRIBE`: `edgeshield/+/telemetry`, `edgeshield/+/status`
  - `PUBLISH`: Restricted to approved command dispatches

---

## 3. Mosquitto ACL Configuration Example

```properties
# Topic ACL for Soil Moisture Sensors
pattern readwrite edgeshield/soil-sensor-01/telemetry
pattern readwrite edgeshield/soil-sensor-01/status

# Actuator commands are explicitly restricted
pattern readwrite edgeshield/valve-controller-01/telemetry
pattern read edgeshield/valve-controller-01/cmd/#
```
Attempts by non-actuator devices to publish to `edgeshield/valve-controller-01/cmd/state` immediately trigger the `unauthorized_topic` detector with **CRITICAL** severity.
