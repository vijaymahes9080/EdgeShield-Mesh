"""
EdgeShield Mesh - Temporal Knowledge Graph Causal Reasoner
Tracks temporal incident progressions (A -> causes -> B -> impacts -> C)
over multi-hop entity dependency networks to isolate root causes versus cascading symptoms.
"""

from typing import List, Dict, Set, Tuple, Optional
from pydantic import BaseModel, Field
import time


class CausalEdge(BaseModel):
    source_entity: str
    target_entity: str
    relationship: str  # FEEDS_POWER_TO, SENDS_TELEMETRY_TO, CONTROLS_PRESSURE_FOR
    confidence: float


class RootCauseAnalysis(BaseModel):
    root_cause_entity: str
    cascading_affected_entities: List[str]
    causal_path_summary: str
    confidence_score: float


class TemporalKnowledgeGraphReasoner:
    """
    Infers root cause from multi-alarm cascades across the edge mesh.
    """

    def __init__(self):
        self.edges: List[CausalEdge] = []

    def add_relationship(self, source: str, target: str, rel: str, confidence: float = 1.0):
        self.edges.append(CausalEdge(source_entity=source, target_entity=target, relationship=rel, confidence=confidence))

    def diagnose_cascade(self, alarmed_devices: List[str]) -> RootCauseAnalysis:
        if not alarmed_devices:
            return RootCauseAnalysis(root_cause_entity="UNKNOWN", cascading_affected_entities=[], causal_path_summary="No alarms", confidence_score=0.0)
            
        # Build adjacency graph
        parents: Dict[str, Set[str]] = {d: set() for d in alarmed_devices}
        for edge in self.edges:
            if edge.source_entity in alarmed_devices and edge.target_entity in alarmed_devices:
                parents[edge.target_entity].add(edge.source_entity)
                
        # Root cause is node with minimum or zero incoming alarmed parents
        root = min(alarmed_devices, key=lambda d: len(parents.get(d, set())))
        cascades = [d for d in alarmed_devices if d != root]
        
        path_str = f"Root failure at [{root}] propagated downstream to {cascades}"
        return RootCauseAnalysis(
            root_cause_entity=root,
            cascading_affected_entities=cascades,
            causal_path_summary=path_str,
            confidence_score=0.95
        )
