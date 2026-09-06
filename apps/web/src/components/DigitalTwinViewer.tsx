import React, { useState } from "react";
import { Gauge, AlertTriangle, ShieldCheck, Zap, Layers } from "lucide-react";

export const DigitalTwinViewer: React.FC = () => {
  const [valveState, setValveState] = useState<"OPEN" | "CLOSED">("OPEN");
  const [flowRate, setFlowRate] = useState(32.4);
  const [surgePressure, setSurgePressure] = useState(4.2);

  const handleSimulateCutoff = () => {
    setValveState("CLOSED");
    // Water hammer physics simulation: sudden closure spikes pressure
    const spike = (flowRate / 10.0) * 1.8;
    setSurgePressure(4.2 + spike);
  };

  const handleResetSimulation = () => {
    setValveState("OPEN");
    setSurgePressure(4.2);
  };

  const isOverpressure = surgePressure > 8.0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Layers className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-bold text-white">Digital Twin: Hydraulic & Blast Radius Simulator</h2>
        </div>
        <span className={`px-3 py-1 text-xs font-mono rounded-full border ${isOverpressure ? 'bg-rose-950/80 text-rose-300 border-rose-500/40 animate-pulse' : 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'}`}>
          {isOverpressure ? "OVERPRESSURE PIPE RUPTURE RISK" : "PHYSICS STABILITY: NOMINAL"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-mono mb-1">CURRENT FLOW RATE</div>
          <div className="text-2xl font-bold font-mono text-cyan-400">{flowRate.toFixed(1)} L/s</div>
          <input
            type="range"
            min="10"
            max="60"
            value={flowRate}
            onChange={(e) => setFlowRate(parseFloat(e.target.value))}
            className="w-full mt-3 accent-cyan-400"
          />
        </div>

        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-mono mb-1">SOLENOID VALVE STATE</div>
          <div className="text-2xl font-bold font-mono text-white flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${valveState === 'OPEN' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
            {valveState}
          </div>
          <div className="mt-3 flex gap-2">
            <button
              onClick={handleSimulateCutoff}
              className="px-3 py-1.5 bg-rose-600/80 hover:bg-rose-600 text-white rounded text-xs font-semibold"
            >
              Simulate Instant Cutoff
            </button>
            <button
              onClick={handleResetSimulation}
              className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs"
            >
              Reset
            </button>
          </div>
        </div>

        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="text-xs text-slate-400 font-mono mb-1">DOWNSTREAM SURGE PRESSURE</div>
          <div className={`text-2xl font-bold font-mono ${isOverpressure ? 'text-rose-400 font-black' : 'text-purple-300'}`}>
            {surgePressure.toFixed(2)} Bar
          </div>
          <div className="text-[11px] text-slate-400 mt-2">
            Pipe Rating: 8.0 Bar (AS-Schedule-40)
          </div>
        </div>
      </div>
    </div>
  );
};
