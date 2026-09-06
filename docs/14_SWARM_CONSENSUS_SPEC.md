# Swarm Consensus & Mesh Synchronization Specification

> **EdgeShield Mesh Decentralized Fault-Tolerance Specification (Doc #14)**

---

## 1. Motivation: Satellite Backhaul Intermittency

Rural agriculture and remote microgrids frequently encounter orbital blackout windows (15 to 45 minutes) where satellite backhaul connectivity is lost.

EdgeShield Mesh prevents security degradation during disconnected states via a two-layer consensus architecture:
1. **Micro-Raft Engine**: Elects local edge leaders within the local mesh subnet for synchronized command replication.
2. **Epidemic Threat Gossip Protocol**: Propagates threat indicators and quarantine commands peer-to-peer over local LoRa, Wi-Fi HaLow, or Zigbee mesh hops.

---

## 2. Protocol Safety Invariants

1. **Leader Monotonicity**: At most one leader can hold a valid term lease per partition.
2. **Byzantine Fault Isolation**: Nodes broadcasting conflicting commitments (equivocation) are automatically flagged and excluded from the active voting quorum.
3. **CRDT Partition Recovery**: When satellite links recover, state differences are reconciled using conflict-free LWW-Registers and PN-Counters without data loss or rollback locks.

---

## 3. Threat Dissemination Bound

Gossip messages use an epidemic fan-out model with strict Hop-Count bounds ($H_{\max} = 5$) and SHA-256 message deduplication to prevent broadcast storms across bandwidth-constrained RF links.
