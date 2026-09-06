"""
Unit tests for MicroRaft, Gossip Protocol, Byzantine Fault Detector, and CRDTs.
"""

import pytest
import time
from services.mesh_consensus.raft_node import MicroRaftNode, NodeRole
from services.mesh_consensus.gossip_protocol import GossipMeshNode
from services.mesh_consensus.byzantine_fault_detector import ByzantineFaultDetector
from services.mesh_consensus.state_sync import LWWRegister, PNCounter


def test_micro_raft_election_and_log():
    peers = ["node-2", "node-3"]
    node1 = MicroRaftNode(node_id="node-1", peers=peers)
    
    # Start election
    req = node1.start_election()
    assert node1.role == NodeRole.CANDIDATE
    
    # Receive vote from node-2
    from services.mesh_consensus.raft_node import VoteResponse
    became_leader = node1.handle_vote_response("node-2", VoteResponse(term=1, vote_granted=True))
    assert became_leader is True
    assert node1.role == NodeRole.LEADER
    
    # Leader appends command
    entry = node1.append_command("ISOLATE_VALVE_01")
    assert entry.index == 1
    assert entry.command == "ISOLATE_VALVE_01"


def test_gossip_protocol_dissemination():
    secret = b"test_gossip_secret"
    node_a = GossipMeshNode("node-a", ["node-b", "node-c"], secret)
    node_b = GossipMeshNode("node-b", ["node-a", "node-c"], secret)
    
    msg = node_a.create_threat_broadcast(
        target_dev="soil-01",
        category="REPLAY_ATTACK",
        severity="HIGH",
        details="Repeated frame counter detected"
    )
    
    fwd_peers = node_b.receive_gossip(msg)
    assert fwd_peers is not None
    assert "node-c" in fwd_peers
    
    # Duplicate gossip is dropped
    assert node_b.receive_gossip(msg) is None


def test_byzantine_fault_detector_equivocation():
    bft = ByzantineFaultDetector()
    
    # Node X reports hash1 to Peer A
    res1 = bft.record_node_commitment(epoch="epoch-10", node_id="node-x", peer_id="peer-a", claim_hash="hash_111")
    assert res1 is None
    assert bft.is_node_trusted("node-x") is True
    
    # Node X reports conflicting hash2 to Peer B in same epoch -> Equivocation!
    res2 = bft.record_node_commitment(epoch="epoch-10", node_id="node-x", peer_id="peer-b", claim_hash="hash_222")
    assert res2 is not None
    assert res2.anomaly_type == "EQUIVOCATION_DETECTED"
    assert bft.is_node_trusted("node-x") is False


def test_crdt_pn_counter_and_lww():
    # Test PN-Counter
    cnt_a = PNCounter()
    cnt_b = PNCounter()
    
    cnt_a.increment("node-a", 10)
    cnt_b.decrement("node-b", 3)
    
    merged = cnt_a.merge(cnt_b)
    assert merged.value == 7
    
    # Test LWW-Register
    reg1 = LWWRegister(value="status_normal", timestamp=100.0, author_node_id="node-1")
    reg2 = LWWRegister(value="status_alarm", timestamp=105.0, author_node_id="node-2")
    
    assert reg1.merge(reg2).value == "status_alarm"
