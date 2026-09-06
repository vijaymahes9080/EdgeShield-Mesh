import React, { useState } from 'react';
import { Activity, RefreshCw, Layers, Database } from 'lucide-react';
import { NormalizedTelemetry, Device } from '../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface TelemetryViewProps {
  telemetry: NormalizedTelemetry[];
  devices: Device[];
  onTickDevices: () => void;
  isTicking: boolean;
}

export const TelemetryView: React.FC<TelemetryViewProps> = ({
  telemetry,
  devices,
  onTickDevices,
  isTicking,
}) => {
  const [selectedDevice, setSelectedDevice] = useState<string>('all');

  const filteredTelemetry = selectedDevice === 'all'
    ? telemetry
    : telemetry.filter((t) => t.device_id === selectedDevice);

  // Prepare chart series from recent records (reverse so oldest -> newest)
  const chartData = [...filteredTelemetry].reverse().slice(-25).map((t) => {
    const timeStr = new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    return {
      time: timeStr,
      soil_moisture: t.measurements?.soil_moisture_pct,
      temp: t.measurements?.ambient_temp_c || t.measurements?.soil_temp_c || t.measurements?.temp_c,
      solar: t.measurements?.solar_irradiance_w_m2,
      pressure: t.measurements?.line_pressure_psi,
      battery: t.battery_level,
      device_id: t.device_id,
    };
  });

  return (
    <div className="space-y-6">
      
      {/* Controls & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 cyber-card p-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h2 className="font-bold text-slate-100 text-sm">Live Ingested Telemetry Feed</h2>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-400 text-[11px]">Filter:</span>
            <button
              onClick={() => setSelectedDevice('all')}
              className={`px-2 py-0.5 rounded text-xs transition-colors ${
                selectedDevice === 'all' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-300 hover:text-white'
              }`}
            >
              All (5)
            </button>
            {devices.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDevice(d.id)}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                  selectedDevice === d.id ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                {d.id.replace('-01', '')}
              </button>
            ))}
          </div>

          <button
            onClick={onTickDevices}
            disabled={isTicking}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTicking ? 'animate-spin' : ''}`} />
            <span>Generate Ingestion Tick</span>
          </button>
        </div>
      </div>

      {/* Real-time Streaming Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        
        {/* Soil Moisture / Pressure Chart */}
        <div className="cyber-card p-5">
          <h3 className="text-xs font-mono uppercase text-slate-400 mb-3 flex items-center justify-between">
            <span>Soil Moisture (%) & Pressure (PSI) Trend</span>
            <span className="text-cyan-400">Live Stream</span>
          </h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Line type="monotone" dataKey="soil_moisture" stroke="#06b6d4" strokeWidth={2} dot={{ r: 2 }} name="Soil Moisture %" />
                <Line type="monotone" dataKey="pressure" stroke="#10b981" strokeWidth={2} dot={{ r: 2 }} name="Pressure PSI" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Temperature & Battery Chart */}
        <div className="cyber-card p-5">
          <h3 className="text-xs font-mono uppercase text-slate-400 mb-3 flex items-center justify-between">
            <span>Environmental Temperature (°C) & Battery (%)</span>
            <span className="text-emerald-400">Live Stream</span>
          </h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Line type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={2} dot={{ r: 2 }} name="Temperature °C" />
                <Line type="monotone" dataKey="battery" stroke="#a855f7" strokeWidth={2} dot={{ r: 2 }} name="Battery %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Recent Telemetry Raw Table */}
      <div className="cyber-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4 text-cyan-400" />
            <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider">Normalized Telemetry Ledger</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">{filteredTelemetry.length} events loaded</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Device ID</th>
                <th className="py-2.5 px-3">Seq / Nonce</th>
                <th className="py-2.5 px-3">Measurements</th>
                <th className="py-2.5 px-3">Payload SHA-256</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filteredTelemetry.slice(0, 15).map((t) => (
                <tr key={t.event_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2 px-3 text-slate-400">
                    {new Date(t.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2 px-3 text-cyan-300 font-semibold">{t.device_id}</td>
                  <td className="py-2 px-3 text-slate-300">
                    #{t.seq} <span className="text-slate-500">({t.nonce ? t.nonce.slice(0, 6) : 'none'})</span>
                  </td>
                  <td className="py-2 px-3 text-slate-200">
                    {Object.entries(t.measurements).map(([k, v]) => `${k}:${v}`).join(', ')}
                  </td>
                  <td className="py-2 px-3 text-slate-500 truncate max-w-[120px]" title={t.payload_hash}>
                    {t.payload_hash ? t.payload_hash.slice(0, 12) + '...' : '-'}
                  </td>
                  <td className="py-2 px-3 text-right">
                    <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]">
                      VALID
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
