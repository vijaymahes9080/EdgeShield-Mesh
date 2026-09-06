import React, { useState, useEffect } from "react";
import { Globe, Satellite, ShieldAlert, Wifi, Activity } from "lucide-react";

export const CyberGlobe3D: React.FC = () => {
  const [orbitAngle, setOrbitAngle] = useState(0);
  const [activeSatellites] = useState([
    { id: "LEO-SAT-ALPHA", norad: 25544, elevation: "42.5°", snr: "18.2 dB", status: "TRACKING_NOMINAL" },
    { id: "LEO-SAT-BETA", norad: 48274, elevation: "68.1°", snr: "16.9 dB", status: "BEAM_LOCKED" },
    { id: "ORBIT-IRIDIUM-7", norad: 39512, elevation: "12.4°", snr: "9.4 dB", status: "DOPPLER_VERIFIED" }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setOrbitAngle((prev) => (prev + 1) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl relative overflow-hidden">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <Globe className="w-6 h-6 text-cyan-400 animate-pulse" />
          <h2 className="text-xl font-bold text-white tracking-wide">3D Orbital Satellite & Mesh Link Radar</h2>
        </div>
        <span className="px-3 py-1 bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 rounded-full text-xs font-mono flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5" /> NORAD TLE REAL-TIME SYNC
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Radar Canvas Simulation */}
        <div className="lg:col-span-2 relative h-72 bg-radial from-slate-800 to-slate-950 rounded-lg border border-cyan-500/20 flex items-center justify-center overflow-hidden">
          {/* Concentric orbital rings */}
          <div className="absolute w-60 h-60 border border-cyan-500/20 rounded-full animate-ping opacity-25"></div>
          <div className="absolute w-48 h-48 border border-cyan-400/30 rounded-full"></div>
          <div className="absolute w-32 h-32 border border-dashed border-cyan-300/40 rounded-full"></div>
          <div className="absolute w-16 h-16 bg-cyan-500/10 border border-cyan-400 rounded-full flex items-center justify-center">
            <span className="text-[10px] font-mono text-cyan-300 font-bold">EDGE-GW</span>
          </div>

          {/* Orbiting Satellite Indicator */}
          <div
            className="absolute flex items-center gap-1 transition-all duration-75"
            style={{
              transform: `rotate(${orbitAngle}deg) translate(95px) rotate(-${orbitAngle}deg)`
            }}
          >
            <Satellite className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span className="text-[10px] font-mono text-emerald-300 bg-slate-900/90 px-1 py-0.5 rounded border border-emerald-500/30">LEO-SAT</span>
          </div>
        </div>

        {/* Live Ephemeris Telemetry Table */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Wifi className="w-4 h-4 text-emerald-400" /> Active Uplink Constellations
          </h3>
          {activeSatellites.map((sat) => (
            <div key={sat.id} className="p-3 bg-slate-800/60 border border-slate-700/60 rounded-lg text-xs space-y-1">
              <div className="flex justify-between items-center text-slate-200 font-semibold font-mono">
                <span>{sat.id}</span>
                <span className="text-emerald-400 text-[10px] font-normal">{sat.status}</span>
              </div>
              <div className="flex justify-between text-slate-400 font-mono text-[11px]">
                <span>NORAD: #{sat.norad}</span>
                <span>Elev: {sat.elevation}</span>
                <span>SNR: {sat.snr}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
