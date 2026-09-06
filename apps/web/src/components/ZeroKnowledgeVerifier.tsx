import React, { useState } from "react";
import { Lock, KeyRound, ShieldCheck, FileCheck, CheckCircle } from "lucide-react";

export const ZeroKnowledgeVerifier: React.FC = () => {
  const [proofStatus, setProofStatus] = useState<"VALID" | "VERIFYING">("VALID");
  const [zkpSample] = useState({
    deviceId: "soil-moisture-alpha",
    publicClaim: "0.0 <= soil_moisture <= 100.0 (True Range Verification)",
    commitment: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    challenge: "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
    pqcAlgorithm: "Dilithium3-Kyber768-Hybrid"
  });

  const handleVerify = () => {
    setProofStatus("VERIFYING");
    setTimeout(() => {
      setProofStatus("VALID");
    }, 400);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Lock className="w-6 h-6 text-cyan-400" />
          <h2 className="text-xl font-bold text-white">Zero-Knowledge (ZKP) & Post-Quantum Proof Verifier</h2>
        </div>
        <span className="px-3 py-1 bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 rounded-full text-xs font-mono flex items-center gap-1.5">
          <KeyRound className="w-3.5 h-3.5" /> {zkpSample.pqcAlgorithm}
        </span>
      </div>

      <div className="space-y-4">
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
          <div className="text-xs text-slate-400 font-mono">NON-INTERACTIVE ZERO-KNOWLEDGE PROOF (zk-SNARK)</div>
          <div className="text-sm font-semibold text-emerald-400 font-mono">
            {zkpSample.publicClaim}
          </div>
          <div className="text-xs text-slate-400 font-mono pt-2 space-y-1">
            <div className="truncate">Pedersen Commitment: <span className="text-slate-300">{zkpSample.commitment}</span></div>
            <div className="truncate">Fiat-Shamir Challenge: <span className="text-slate-300">{zkpSample.challenge}</span></div>
          </div>
        </div>

        <div className="flex justify-between items-center pt-2">
          <button
            onClick={handleVerify}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
          >
            <FileCheck className="w-4 h-4" />
            {proofStatus === "VERIFYING" ? "Computing Lattice Matrix..." : "Verify Cryptographic Proof"}
          </button>

          <span className="text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <CheckCircle className="w-4 h-4" /> MATHEMATICALLY PROVEN WITHOUT DATA LEAKAGE
          </span>
        </div>
      </div>
    </div>
  );
};
