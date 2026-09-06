"""
EdgeShield Mesh - Byzantine Fault Detector
Identifies nodes broadcasting contradictory claims to different peers (equivocation),
or persistently falsifying sensory telemetry to poison edge aggregation consensus.
"""

from typing import Dict, List, Set, Tuple, Optional
from pydantic import BaseModel, Field
import time


class ByzantineAnomaly(BaseModel):
    culprit_node_id: str
    anomaly_type: str
    confidence_score: float
    evidence: Dict[str, str]
    detected_at: float = Field(default_factory=time.time)


class ByzantineFaultDetector:
    """
    Analyzes multi-peer vote commitments and telemetry attestations to identify Byzantine actors.
    """

    def __init__(self, tolerance_threshold: float = 0.67):
        self.tolerance_threshold = tolerance_threshold
        # Stores map of (epoch, round) -> Dict[node_id, claim_hash]
        self._epoch_commitments: Dict[str, Dict[str, str]] = {}
        self.flagged_nodes: Set[str] = set()

    def record_node_commitment(self, epoch: str, node_id: str, peer_id: str, claim_hash: str) -> Optional[ByzantineAnomaly]:
        """
        Records what node_id reported to peer_id during epoch.
        If node_id gave conflicting claim hashes to different peers in the same epoch, it is an Equivocation Byzantine fault.
        """
        epoch_key = f"{epoch}:{node_id}"
        if epoch_key not in self._epoch_commitments:
            self._epoch_commitments[epoch_key] = {}
            
        commitments = self._epoch_commitments[epoch_key]
        
        # Check for equivocation
        for existing_peer, existing_hash in commitments.items():
            if existing_hash != claim_hash:
                self.flagged_nodes.add(node_id)
                return ByzantineAnomaly(
                    culprit_node_id=node_id,
                    anomaly_type="EQUIVOCATION_DETECTED",
                    confidence_score=0.99,
                    evidence={
                        "epoch": epoch,
                        "peer_a": existing_peer,
                        "hash_a": existing_hash,
                        "peer_b": peer_id,
                        "hash_b": claim_hash
                    }
                )
                
        commitments[peer_id] = claim_hash
        return None

    def is_node_trusted(self, node_id: str) -> bool:
        return node_id not in self.flagged_nodes
