import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Radio, Activity, ArrowRight, Zap, RefreshCw } from 'lucide-react';
import { Device, Incident, RemediationProposal, HealthSummary } from '../types';
import { CyberGlobe3D } from './CyberGlobe3D';
import { DigitalTwinViewer } from './DigitalTwinViewer';
import { MitreIcsMatrix } from './MitreIcsMatrix';
import { SwarmConsensusView } from './SwarmConsensusView';
import { VoiceOperatorAssistant } from './VoiceOperatorAssistant';
import { ZeroKnowledgeVerifier } from './ZeroKnowledgeVerifier';

interface OverviewViewProps {
  health: HealthSummary | null;
  devices: Device[];
  incidents: Incident[];
  proposals: RemediationProposal[];
  onSelectIncident: (inc: Incident) => void;
  onSelectProposal: (prop: RemediationProposal) => void;
  onTickDevices: () => void;
  onNavigateTab: (tab: string) => void;
  isTicking: boolean;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  health,
  devices,
  incidents,
  proposals,
  onSelectIncident,
  onSelectProposal,
  onTickDevices,
  onNavigateTab,
  isTicking,
}) => {
  const pendingProposals = proposals.filter((p) => p.status === 'pending');
  const criticalIncidents = incidents.filter((i) => i.severity === 'critical' || i.severity === 'high');

  const threatLevel = criticalIncidents.length > 0 ? 'CRITICAL' : incidents.length > 0 ? 'ELEVATED' : 'NOMINAL';
  const threatColor =
    threatLevel === 'CRITICAL'
      ? 'border-rose-500/50 bg-rose-950/20 text-rose-400'
      : threatLevel === 'ELEVATED'
      ? 'border-amber-500/50 bg-amber-950/20 text-amber-400'
      : 'border-emerald-500/50 bg-emerald-950/20 text-emerald-400';

  return (
    <div className="space-y-8">
      
      {/* Top Threat Banner */}
      <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${threatColor}`}>
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-black/40">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold tracking-widest uppercase">Global Threat Level:</span>
              <span className="font-black text-sm px-2 py-0.5 rounded bg-black/50 border border-current">{threatLevel}</span>
            </div>
            <p className="text-xs opacity-90 mt-0.5">
              {threatLevel === 'CRITICAL'
                ? 'High-impact anomalies detected across mesh. Human review required for proposed containment.'
                : threatLevel === 'ELEVATED'
                ? 'Minor behavioral anomalies detected in farm telemetry. Monitoring closely.'
                : 'All 5 Smart Agriculture virtual nodes are reporting nominal telemetry.'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <button
            onClick={onTickDevices}
            disabled={isTicking}
            className="flex items-center justify-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 transition-all flex-1 sm:flex-none cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTicking ? 'animate-spin' : ''}`} />
            <span>Generate Farm Telemetry</span>
          </button>
          <button
            onClick={() => onNavigateTab('simulator')}
            className="flex items-center justify-center space-x-1.5 px-3 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-cyan-950 transition-all flex-1 sm:flex-none cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Attack Simulator</span>
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="cyber-card p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Active Devices</span>
            <Radio className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {health?.active ?? 5} <span className="text-sm font-normal text-slate-400">/ {health?.total_devices || 5}</span>
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5" />
            {health?.healthy_percentage || 100}% Operational
          </div>
        </div>

        <div className="cyber-card p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Open Incidents</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {incidents.length}
          </div>
          <div className="text-[11px] text-amber-400 mt-1">
            {criticalIncidents.length} High/Critical Severity
          </div>
        </div>

        <div className="cyber-card p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Pending Approvals</span>
            <Shield className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {pendingProposals.length}
          </div>
          <div className="text-[11px] text-purple-300 mt-1">
            Human-In-The-Loop Gate
          </div>
        </div>

        <div className="cyber-card p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Satellite Link</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            ACTIVE
          </div>
          <div className="text-[11px] text-emerald-400 mt-1">
            SNR: 18.2 dB (LEO Locked)
          </div>
        </div>
      </div>

      {/* 3D Cyber Globe Satellite Radar */}
      <CyberGlobe3D />

      {/* Digital Twin Physics & Swarm Consensus */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DigitalTwinViewer />
        <SwarmConsensusView />
      </div>

      {/* MITRE ICS Matrix & ZKP Verifier */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MitreIcsMatrix />
        <ZeroKnowledgeVerifier />
      </div>

      {/* Rural Voice Copilot */}
      <VoiceOperatorAssistant />

      {/* Operational Triage Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Pending Approvals */}
        <div className="cyber-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-amber-400" />
              <h3 className="font-semibold text-slate-100 text-sm">Pending Action Proposals (HITL Gate)</h3>
            </div>
            <button
              onClick={() => onNavigateTab('approvals')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
            >
              <span>View All ({pendingProposals.length})</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {pendingProposals.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
              No pending remediation actions. All nodes operating normally.
            </div>
          ) : (
            <div className="space-y-3">
              {pendingProposals.slice(0, 3).map((prop) => (
                <div
                  key={prop.id}
                  onClick={() => onSelectProposal(prop)}
                  className="p-3.5 rounded-lg bg-slate-950/80 border border-amber-500/30 hover:border-cyan-500/60 transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      {prop.action_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{prop.id}</span>
                  </div>
                  <p className="text-xs text-slate-200 mt-2 font-medium">Target: <code className="text-cyan-400">{prop.target_device_id}</code></p>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{prop.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Latest Incidents */}
        <div className="cyber-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <h3 className="font-semibold text-slate-100 text-sm">Recent Threat Detections</h3>
            </div>
            <button
              onClick={() => onNavigateTab('incidents')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
            >
              <span>Incident Center</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {incidents.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
              No anomalies detected. Network is quiet.
            </div>
          ) : (
            <div className="space-y-3">
              {incidents.slice(0, 3).map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => onSelectIncident(inc)}
                  className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-cyan-500/60 transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded ${
                        inc.severity === 'critical' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                        inc.severity === 'high' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                        'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                      }`}>
                        {inc.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-200">{inc.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-cyan-400">
                      {(inc.confidence * 100).toFixed(0)}% conf
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1.5 line-clamp-1">{inc.observed_facts[0] || 'Anomaly reported'}</p>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
