import React, { useState } from 'react';
import { Shield, Search, Lock, RefreshCw, Hash, FileCode } from 'lucide-react';
import { AuditEvent } from '../types';

interface AuditViewProps {
  auditLogs: AuditEvent[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const AuditView: React.FC<AuditViewProps> = ({ auditLogs, onRefresh, isLoading }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');

  const filtered = auditLogs.filter((log) => {
    const term = searchTerm.toLowerCase();
    return (
      log.actor.toLowerCase().includes(term) ||
      log.action.toLowerCase().includes(term) ||
      log.resource_id.toLowerCase().includes(term) ||
      log.resource_type.toLowerCase().includes(term) ||
      log.entry_hash.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 cyber-card p-4">
        <div className="flex items-center space-x-2">
          <Lock className="w-5 h-5 text-cyan-400" />
          <div>
            <h2 className="font-bold text-slate-100 text-sm">Cryptographic Audit Ledger</h2>
            <p className="text-[11px] text-slate-400">Hash-chained immutable chronological record of all system events and operator decisions</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search actor, action, hash..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 font-mono w-48 sm:w-64"
            />
          </div>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            title="Refresh Ledger"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="cyber-card p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Actor (Role)</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Resource</th>
                <th className="py-2.5 px-3">Details</th>
                <th className="py-2.5 px-3">Entry SHA-256</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filtered.map((log) => (
                <tr key={log.event_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span className="text-cyan-300 font-bold">{log.actor}</span>{' '}
                    <span className="text-[10px] text-slate-500 uppercase">({log.actor_role})</span>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-200">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 whitespace-nowrap">
                    {log.resource_type}:<span className="text-cyan-400">{log.resource_id}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 max-w-[200px] truncate" title={JSON.stringify(log.details)}>
                    {JSON.stringify(log.details)}
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 font-mono text-[10px] truncate max-w-[120px]" title={`Prev: ${log.prev_hash}\nEntry: ${log.entry_hash}`}>
                    {log.entry_hash.slice(0, 12)}...
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]">
                      {log.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
