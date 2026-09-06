"""
EdgeShield Mesh - CRDT State Synchronization Engine
Provides conflict-free replicated data types (LWW-Register and PN-Counter)
for peer-to-peer telemetry state reconciliation after network partitions.
"""

import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LWWRegister(BaseModel):
    """Last-Write-Wins Register CRDT."""
    value: Any
    timestamp: float
    author_node_id: str

    def merge(self, other: 'LWWRegister') -> 'LWWRegister':
        if other.timestamp > self.timestamp:
            return other
        elif other.timestamp == self.timestamp and other.author_node_id > self.author_node_id:
            return other
        return self


class PNCounter(BaseModel):
    """Positive-Negative Counter CRDT."""
    pos_increments: Dict[str, int] = Field(default_factory=dict)
    neg_decrements: Dict[str, int] = Field(default_factory=dict)

    def increment(self, node_id: str, amount: int = 1):
        self.pos_increments[node_id] = self.pos_increments.get(node_id, 0) + amount

    def decrement(self, node_id: str, amount: int = 1):
        self.neg_decrements[node_id] = self.neg_decrements.get(node_id, 0) + amount

    @property
    def value(self) -> int:
        p = sum(self.pos_increments.values())
        n = sum(self.neg_decrements.values())
        return p - n

    def merge(self, other: 'PNCounter') -> 'PNCounter':
        new_pos = {}
        for k in set(self.pos_increments.keys()).union(other.pos_increments.keys()):
            new_pos[k] = max(self.pos_increments.get(k, 0), other.pos_increments.get(k, 0))
            
        new_neg = {}
        for k in set(self.neg_decrements.keys()).union(other.neg_decrements.keys()):
            new_neg[k] = max(self.neg_decrements.get(k, 0), other.neg_decrements.get(k, 0))
            
        return PNCounter(pos_increments=new_pos, neg_decrements=new_neg)
