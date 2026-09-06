import React, { useState } from 'react';
import { Shield, Sliders, CheckCircle2, AlertCircle } from 'lucide-react';
import { DetectionRule, UserPublic } from '../types';
import { ApiService } from '../api';

interface SettingsViewProps {
  rules: DetectionRule[];
  user: UserPublic | null;
  onRefreshRules: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ rules, user, onRefreshRules }) => {
  const [updatingRuleId, setUpdatingRuleId] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleToggleRule = async (rule: DetectionRule) => {
    setUpdatingRuleId(rule.rule_id);
    setStatusMsg(null);
    try {
      await ApiService.updateRule(rule.rule_id, { enabled: !rule.enabled });
      setStatusMsg(`Rule '${rule.name}' updated successfully.`);
      onRefreshRules();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setUpdatingRuleId(null);
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="cyber-card p-5 border-cyan-500/30">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-cyan-400">
            <Sliders className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100">Detection Engine Rules & Thresholds</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Configure active deterministic detectors and sensitivity envelopes across the rural IoT mesh network.
            </p>
          </div>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-lg bg-cyan-950/50 border border-cyan-800 text-xs text-cyan-300">
          {statusMsg}
        </div>
      )}

      {!isAdmin && (
        <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 text-xs text-amber-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>You are viewing rule thresholds in read-only mode. Administrator privileges required to modify rules.</span>
        </div>
      )}

      {/* Rules List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {rules.map((rule) => {
          const isUpdating = updatingRuleId === rule.rule_id;
          return (
            <div
              key={rule.rule_id}
              className={`cyber-card p-4 flex flex-col justify-between space-y-3 ${
                rule.enabled ? 'border-slate-800' : 'border-slate-800/40 opacity-60'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded ${
                      rule.severity === 'critical' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                      rule.severity === 'high' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                      'bg-blue-950 text-blue-300 border border-blue-800'
                    }`}>
                      {rule.severity}
                    </span>
                    <span className="text-xs font-mono text-slate-400">{rule.rule_id}</span>
                  </div>

                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rule.enabled}
                      disabled={!isAdmin || isUpdating}
                      onChange={() => handleToggleRule(rule)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-500"></div>
                  </label>
                </div>

                <h3 className="font-bold text-slate-100 text-sm mt-2">{rule.name}</h3>
                <p className="text-xs text-slate-400 mt-1 font-mono text-[11px]">Detector: {rule.detector_id}</p>

                <div className="mt-2.5 p-2 rounded bg-slate-950 text-[11px] font-mono text-slate-300 border border-slate-800/80">
                  Parameters: {JSON.stringify(rule.parameters)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
