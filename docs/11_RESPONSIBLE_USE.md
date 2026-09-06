# EdgeShield Mesh — Responsible AI Use, Safety Controls, and System Limitations

EdgeShield Mesh is engineered for critical agricultural and rural cyber-physical infrastructure where erroneous autonomous actions can lead to physical equipment damage, flooding, or crop loss.

---

## 1. Non-Negotiable AI Safety Principles

1. **Zero Disruptive Autonomous Actions**: The AI agent is strictly an **advisor and copilot**. It can generate analyses, explain threat contexts, and correlate evidence, but it is architecturally prohibited from actuating physical valves, power switches, or network firewalls without human approval.
2. **Untrusted Data Isolation**: All telemetry, device names, topic strings, and log messages are treated as untrusted data and never interpreted as prompt instructions.
3. **Evidence Grounding Requirement**: Every claim made in an incident summary must cite an observed telemetry data point, detector rule, or verified RAG runbook chunk.
4. **Privacy & PII Protection**: Telemetry payloads are scrubbed of personal identification (farmer emails, non-local MACs) before storage and retrieval.

---

## 2. Known Limitations & Edge Constraints

- **Connectivity Outages**: While edge gateways continue logging and evaluating deterministic rules offline, LLM re-analysis requiring cloud models pauses until connectivity is restored.
- **Physical Sensor Brownouts**: Extreme battery drops can induce sensor voltage instabilities that appear similar to spoofing attacks; field operators should visually inspect probes before replacing hardware.
