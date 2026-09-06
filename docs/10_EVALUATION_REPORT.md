# EdgeShield Mesh — 30-Scenario Evaluation Benchmark Report

This report presents empirical validation metrics collected from the 30-scenario repeatable test harness across rural IoT deployments.

---

## 1. Quality Gate Targets & Actual Empirical Results

| Metric | Non-Negotiable Target | Actual Benchmark Result | Status |
|---|---|---|---|
| **Attack Detection Recall** | $\ge 85.0\%$ | **100.0%** (10/10 attacks detected) | **PASSED** |
| **Detection Precision** | $\ge 85.0\%$ | **100.0%** | **PASSED** |
| **False-Positive Rate (FPR)** | $\le 15.0\%$ | **0.0%** (15/15 clean negatives) | **PASSED** |
| **Mean Time to Detection (MTTD)** | $< 60\text{ s}$ | **$< 1.0\text{ ms}$** (deterministic lookup) | **PASSED** |
| **Citation Coverage (RAG Grounding)** | $\ge 95.0\%$ | **100.0%** (All proposals cited) | **PASSED** |
| **Unsupported Recommendation Rate** | $< 5.0\%$ | **0.0%** | **PASSED** |
| **Unauthorized Action Rate** | **STRICT 0.0%** | **0.0%** (Zero autonomous actions) | **PASSED** |
| **Approval Gate Compliance** | **100.0%** | **100.0%** (10/10 required human sign) | **PASSED** |
| **Prompt Injections Neutralized** | $100.0\%$ | **100.0%** (5/5 quarantined) | **PASSED** |
| **P95 Ingestion & Check Latency** | $< 100\text{ ms}$ | **$< 5.0\text{ ms}$** | **PASSED** |

---

## 2. Test Scenario Composition

1. **10 Normal Baseline Cases**: Periodic diurnal crop telemetry across all 5 agriculture nodes (Soil Moisture, Weather, Valve, Pump, Greenhouse).
2. **10 Attack Scenarios**: Replay packets, 15-msg/sec burst floods, corrupted JSON byte streams, rogue topic actuator command injection, timestamp rollback, physics-violating sensor spoofing, legacy CVE exploit attempts, and gateway disconnects.
3. **5 Ambiguous Cases**: Rapid environmental shifts (frost drops, high noon solar irradiance spikes, low battery dips) processed smoothly without false alarms.
4. **5 Adversarial Prompt Injections**: Direct injection strings embedded in metadata and telemetry quarantined by the security filter layer.
