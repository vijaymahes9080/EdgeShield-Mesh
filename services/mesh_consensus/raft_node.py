"""
EdgeShield Mesh - Micro-Raft Consensus Node
Provides decentralized, fault-tolerant edge leader election and log replication
when remote satellite backhaul connections are degraded or disconnected.
"""

import time
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class NodeRole(str, Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class LogEntry(BaseModel):
    term: int
    index: int
    command: str
    timestamp: float = Field(default_factory=time.time)


class VoteRequest(BaseModel):
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int


class VoteResponse(BaseModel):
    term: int
    vote_granted: bool


class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry] = Field(default_factory=list)
    leader_commit: int


class AppendEntriesResponse(BaseModel):
    term: int
    success: bool
    match_index: int


class MicroRaftNode:
    """
    Lightweight Raft Consensus State Machine for IoT Microgrids and Edge Gateways.
    """

    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        self.role = NodeRole.FOLLOWER
        self.leader_id: Optional[str] = None
        self.votes_received: set = set()

    def start_election(self) -> VoteRequest:
        """Transitions node to candidate and requests votes."""
        self.role = NodeRole.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        
        last_log_index = len(self.log)
        last_log_term = self.log[-1].term if self.log else 0
        
        return VoteRequest(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=last_log_index,
            last_log_term=last_log_term
        )

    def handle_vote_request(self, req: VoteRequest) -> VoteResponse:
        """Processes vote request according to Raft safety rules."""
        if req.term > self.current_term:
            self.current_term = req.term
            self.role = NodeRole.FOLLOWER
            self.voted_for = None

        can_vote = (
            req.term == self.current_term and
            (self.voted_for is None or self.voted_for == req.candidate_id)
        )
        
        if can_vote:
            self.voted_for = req.candidate_id
            return VoteResponse(term=self.current_term, vote_granted=True)
            
        return VoteResponse(term=self.current_term, vote_granted=False)

    def handle_vote_response(self, voter_id: str, resp: VoteResponse) -> bool:
        """Handles response to election. Returns True if became leader."""
        if self.role != NodeRole.CANDIDATE or resp.term != self.current_term:
            return False
            
        if resp.vote_granted:
            self.votes_received.add(voter_id)
            # Majority quorum check
            total_nodes = len(self.peers) + 1
            if len(self.votes_received) > total_nodes // 2:
                self.role = NodeRole.LEADER
                self.leader_id = self.node_id
                return True
        return False

    def append_command(self, command: str) -> LogEntry:
        """Leader appends a new command to its replicated log."""
        if self.role != NodeRole.LEADER:
            raise RuntimeError("Only leader can append commands")
            
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command=command
        )
        self.log.append(entry)
        return entry

    def handle_append_entries(self, req: AppendEntriesRequest) -> AppendEntriesResponse:
        """Follower handles log replication / heartbeat from leader."""
        if req.term < self.current_term:
            return AppendEntriesResponse(term=self.current_term, success=False, match_index=len(self.log))
            
        self.current_term = req.term
        self.role = NodeRole.FOLLOWER
        self.leader_id = req.leader_id
        
        # Append any new entries
        for entry in req.entries:
            if entry.index > len(self.log):
                self.log.append(entry)
                
        if req.leader_commit > self.commit_index:
            self.commit_index = min(req.leader_commit, len(self.log))
            
        return AppendEntriesResponse(term=self.current_term, success=True, match_index=len(self.log))
