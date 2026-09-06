import React, { useState } from 'react';
import { Shield, Zap, AlertTriangle, Play, CheckCircle2, RotateCcw, Activity } from 'lucide-react';
import { ApiService } from '../api';

interface SimulatorViewProps {
  onAttackTriggered?: () => void;
}

export const SimulatorView: React.FC<SimulatorViewProps> = ({ onAttackTriggered }) => {
  const [runningVector, setRunningVector] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);

  const attackVectors = [
    {
      id: 'replay',
      name: 'Replay Attack Vector',
      desc: 'Re-transmits previously recorded telemetry packet with identical nonce & signature.',
      expectedDetector: 'duplicate_message',
      target: 'soil-sensor-01',
      severity: 'MEDIUM',
      color: 'border-yellow-500/40 text-yellow-400'
    },
    {
      id: 'burst',
      name: 'Burst Publish Flood',
      desc: 'Floods broker with 15 rapid messages within <0.5s to test mesh rate-limiting.',
      expectedDetector: 'burst_rate',
      target: 'soil-sensor-01',
      severity: 'HIGH',
      color: 'border-amber-500/40 text-amber-400'
    },
    {
      id: 'invalid_payload',
      name: 'Invalid / Corrupted Payload',
      desc: 'Injects non-JSON binary junk and malformed UTF-8 byte sequences.',
      expectedDetector: 'payload_syntax_error',
      target: 'greenhouse-env-01',
      severity: 'LOW',
      color: 'border-slate-500/40 text-slate-400'
    },
    {
      id: 'unauthorized_topic',
      name: 'Unauthorized Topic Publish',
      desc: 'Soil probe attempts command injection into valve controller state topic.',
      expectedDetector: 'unauthorized_topic',
      target: 'valve-controller-01/cmd',
      severity: 'CRITICAL',
      color: 'border-rose-500/40 text-rose-400'
    },
    {
      id: 'timestamp_rollback',
      name: 'Timestamp Rollback / Stale Packet',
      desc: 'Publishes telemetry packet with timestamp 4 hours in the past.',
      expectedDetector: 'timestamp_rollback',
      target: 'weather-station-01',
      severity: 'HIGH',
      color: 'border-amber-500/40 text-amber-400'
    },
    {
      id: 'sensor_spoofing',
      name: 'Sensor Spoofing (Physics Violation)',
      desc: 'Injects physically impossible telemetry (Soil Moisture 450%, Temp 850°C).',
      expectedDetector: 'impossible_value',
      target: 'soil-sensor-01',
      severity: 'HIGH',
      color: 'border-rose-500/40 text-rose-400'
    },
    {
      id: 'gateway_disconnect',
      name: 'Gateway Disconnect & Silence',
      desc: 'Simulates edge link loss and unannounced device silence.',
      expectedDetector: 'gateway_disconnect',
      target: 'gw-field-alpha',
      severity: 'CRITICAL',
      color: 'border-rose-500/40 text-rose-400'
    },
  ];

  const handleRunAttack = async (vectorId: string) => {
    setRunningVector(vectorId);
    setLastResult(null);
    try {
      const res = await ApiService.triggerAttack(vectorId);
      setLastResult({ vector: vectorId, res, timestamp: new Date().toLocaleTimeString() });
      if (onAttackTriggered) {
        onAttackTriggered();
      }
    } catch (err: any) {
      setLastResult({ vector: vectorId, error: err.message, timestamp: new Date().toLocaleTimeString() });
    } finally {
      setRunningVector(null);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="cyber-card p-5 border-cyan-500/30">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-cyan-400 glow-cyan">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100">Safe Local Attack Simulator</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Generates reproducible IoT attack vectors strictly within the local mock environment. Never touches external networks.
            </p>
          </div>
        </div>
      </div>

      {/* Attack Vectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {attackVectors.map((v) => {
          const isRunning = runningVector === v.id;
          return (
            <div key={v.id} className={`cyber-card p-5 border ${v.color} flex flex-col justify-between space-y-4`}>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-slate-950 border border-current">
                    {v.severity}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">ID: {v.id}</span>
                </div>

                <h3 className="font-bold text-slate-100 text-sm">{v.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{v.desc}</p>

                <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] space-y-1">
                  <p><span className="text-slate-500">Target:</span> <code className="text-cyan-300">{v.target}</code></p>
                  <p><span className="text-slate-500">Expected Detector:</span> <code className="text-emerald-400">{v.expectedDetector}</code></p>
                </div>
              </div>

              <button
                onClick={() => handleRunAttack(v.id)}
                disabled={isRunning}
                className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-slate-950 hover:bg-slate-900 border border-slate-700 hover:border-cyan-500/50 text-xs font-bold text-slate-200 transition-all glow-cyan"
              >
                <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
                <span>{isRunning ? 'Injecting Attack...' : 'Inject Attack Vector'}</span>
              </button>
            </div>
          );
        })}
      </div>

      {/* Live Result Output */}
      {lastResult && (
        <div className="cyber-card p-5 space-y-2 border-cyan-500/40">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-cyan-400 font-bold flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Attack Simulation Output [{lastResult.vector}]</span>
            </span>
            <span className="text-slate-500">{lastResult.timestamp}</span>
          </div>
          <pre className="p-3.5 rounded-lg bg-slate-950 text-xs font-mono text-slate-300 overflow-x-auto border border-slate-800">
            {JSON.stringify(lastResult.res || lastResult.error, null, 2)}
          </pre>
        </div>
      )}

    </div>
  );
};
