import React from 'react';
import { Radio, ShieldAlert, Cpu, Wifi, MapPin, Tag, CheckCircle2 } from 'lucide-react';
import { Device } from '../types';

interface DevicesViewProps {
  devices: Device[];
  onSelectDevice?: (device: Device) => void;
}

export const DevicesView: React.FC<DevicesViewProps> = ({ devices }) => {
  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Radio className="w-5 h-5 text-cyan-400" />
            <span>Smart Agriculture Edge Device Inventory</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            5 registered virtual IoT endpoints deployed in rural field mesh network
          </p>
        </div>
        <div className="text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/60 px-3 py-1.5 rounded-lg">
          ACL Mode: ENFORCED
        </div>
      </div>

      {/* Device Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {devices.map((device) => {
          const isWarning = device.status === 'warning';
          const isIsolated = device.status === 'isolated';
          const cves = device.metadata?.vulnerabilities || [];

          return (
            <div
              key={device.id}
              className={`cyber-card p-5 relative overflow-hidden flex flex-col justify-between ${
                isIsolated ? 'border-rose-500/50 bg-rose-950/10' :
                isWarning ? 'border-amber-500/50 bg-amber-950/10' : ''
              }`}
            >
              {/* Status Header */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="p-1.5 rounded-md bg-slate-800 border border-slate-700 text-cyan-400">
                      <Cpu className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-bold text-slate-100 text-sm">{device.name}</h3>
                      <p className="text-[10px] font-mono text-cyan-400">{device.id}</p>
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded ${
                      isIsolated ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50' :
                      isWarning ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50' :
                      'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50'
                    }`}
                  >
                    {device.status}
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-2 text-xs text-slate-300 my-3">
                  <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span>Zone</span>
                    </span>
                    <span className="font-medium text-slate-200">{device.zone}</span>
                  </div>

                  <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Cpu className="w-3 h-3 text-slate-500" />
                      <span>Firmware / Rev</span>
                    </span>
                    <span className="font-mono text-cyan-300">{device.firmware_version} ({device.hardware_rev})</span>
                  </div>

                  <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Wifi className="w-3 h-3 text-slate-500" />
                      <span>IP / MAC</span>
                    </span>
                    <span className="font-mono text-[11px] text-slate-300">{device.ip_address}</span>
                  </div>

                  <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Report Interval</span>
                    <span className="font-mono text-slate-200">{device.telemetry_interval_sec}s</span>
                  </div>
                </div>

                {/* Vulnerability Warnings */}
                {cves.length > 0 && (
                  <div className="mt-3 p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/50">
                    <div className="flex items-center space-x-1.5 text-amber-400 text-[11px] font-semibold">
                      <ShieldAlert className="w-3.5 h-3.5" />
                      <span>Known Vulnerabilities:</span>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {cves.map((cve: string) => (
                        <span key={cve} className="px-1.5 py-0.5 rounded bg-amber-900/60 text-amber-200 text-[10px] font-mono">
                          {cve}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Topics / Actuator Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800/80">
                <div className="text-[10px] text-slate-400 uppercase font-mono tracking-wider mb-1">Expected Topics</div>
                <div className="space-y-0.5">
                  {device.expected_topics.map((t) => (
                    <div key={t} className="text-[10px] font-mono text-slate-400 truncate">
                      • {t}
                    </div>
                  ))}
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
