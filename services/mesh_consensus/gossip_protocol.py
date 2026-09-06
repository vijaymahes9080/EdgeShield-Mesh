"""
EdgeShield Mesh - Epidemic Threat Gossip Protocol
Facilitates decentralized peer-to-peer threat vector dissemination 
across disconnected or partially meshed rural IoT sensors.
"""

import hashlib
import time
import random
from typing import Dict, List, Set, Optional
from pydantic import BaseModel, Field


class ThreatGossipMessage(BaseModel):
    message_id: str
    origin_node_id: str
    target_device_id: str
    threat_category: str
    severity: str
    details: str
    hop_count: int = 0
    max_hops: int = 5
    timestamp: float = Field(default_factory=time.time)
    signature: str


class GossipMeshNode:
    """
    Simulates a peer in the epidemic gossip protocol mesh.
    """

    def __init__(self, node_id: str, peers: List[str], secret_key: bytes):
        self.node_id = node_id
        self.peers = peers
        self._secret_key = secret_key
        self.seen_messages: Dict[str, ThreatGossipMessage] = {}
        self.peer_states: Dict[str, float] = {p: time.time() for p in peers}

    def create_threat_broadcast(self, target_dev: str, category: str, severity: str, details: str) -> ThreatGossipMessage:
        """Originates a new signed gossip threat report."""
        msg_id = hashlib.sha256(f"{self.node_id}:{target_dev}:{category}:{time.time()}".encode()).hexdigest()[:16]
        sig_data = f"{msg_id}:{self.node_id}:{target_dev}:{category}:{severity}".encode()
        sig = hashlib.sha256(self._secret_key + sig_data).hexdigest()
        
        msg = ThreatGossipMessage(
            message_id=msg_id,
            origin_node_id=self.node_id,
            target_device_id=target_dev,
            threat_category=category,
            severity=severity,
            details=details,
            hop_count=0,
            signature=sig
        )
        self.seen_messages[msg_id] = msg
        return msg

    def receive_gossip(self, msg: ThreatGossipMessage) -> Optional[List[str]]:
        """
        Processes received gossip. If novel and within max hops, returns list of peer IDs to propagate to.
        """
        if msg.message_id in self.seen_messages:
            return None # Already seen
            
        if msg.hop_count >= msg.max_hops:
            return None # TTL exceeded
            
        self.seen_messages[msg.message_id] = msg
        
        # Increment hop count for forwarding
        forward_msg = msg.model_copy(update={"hop_count": msg.hop_count + 1})
        self.seen_messages[msg.message_id] = forward_msg
        
        # Select fan-out peers (excluding origin)
        target_peers = [p for p in self.peers if p != msg.origin_node_id]
        return target_peers
