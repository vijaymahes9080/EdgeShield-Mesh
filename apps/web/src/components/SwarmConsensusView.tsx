import React, { useState } from "react";
import { GitMerge, Cpu, CheckCircle2, Shield, Network } from "lucide-react";

export const SwarmConsensusView: React.FC = () => {
  const [leaderNode, setLeaderNode] = useState("NODE-1-GATEWAY");
  const [currentTerm, setCurrentTerm] = useState(14);
  const [gossipMessages, setGossipMessages] = useState([
    { id: "g-01", topic: "REPLAY_ATTACK_SOIL_01", hops: 2, status: "COMMITTED_QUORUM" },
    { id: "g-02", topic: "GPS_TELEPORT_TRACTOR_03", hops: 1, status: "CONSENSUS_VERIFIED" },
    { id: "g-03", topic: "PQC_KEY_ROTATION_BROADCAST", hops: 3, status: "SYNCED" }
  ]);

  const handleSimulateElection = () => {
    setCurrentTerm((prev) => prev + 1);
    setLeaderNode("NODE-3-BACKUP-GATEWAY");
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Network className="w-6 h-6 text-amber-400" />
          <h2 className="text-xl font-bold text-white">Edge Swarm Consensus & CRDT State Sync</h2>
        </div>
        <button
          onClick={handleSimulateElection}
          className="px-3 py-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-lg text-xs font-mono hover:bg-amber-500/30 transition"
        >
          Trigger Micro-Raft Re-election
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Raft State Card */}
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50 space-y-3">
          <div className="text-xs font-mono text-slate-400">CURRENT RAFT CONSENSUS LEADER</div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-amber-400" />
            <span className="text-lg font-bold font-mono text-white">{leaderNode}</span>
          </div>
          <div className="flex justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-700/60">
            <span>Raft Term: #{currentTerm}</span>
            <span>Quorum Status: 5/5 Nodes Healthy</span>
          </div>
        </div>

        {/* Epidemic Gossip Feed */}
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50 space-y-2">
          <div className="text-xs font-mono text-slate-400 mb-2">LIVE THREAT GOSSIP DISSEMINATION</div>
          {gossipMessages.map((g) => (
            <div key={g.id} className="flex justify-between items-center text-xs font-mono p-2 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-300">{g.topic}</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> {g.status} (Hop: {g.hops})
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
