import React from "react";
import { ShieldAlert, Crosshair, Terminal, ExternalLink } from "lucide-react";

export const MitreIcsMatrix: React.FC = () => {
  const tactics = [
    {
      name: "Initial Access",
      techniques: [
        { id: "T0812", name: "Default Credentials", active: true, hits: 4 },
        { id: "T0865", name: "Spearphishing Attachment", active: false, hits: 0 }
      ]
    },
    {
      name: "Execution",
      techniques: [
        { id: "T0853", name: "Scripting / Python Ingress", active: false, hits: 0 },
        { id: "T0807", name: "Command-Line Interface", active: true, hits: 2 }
      ]
    },
    {
      name: "Impair Process Control",
      techniques: [
        { id: "T0855", name: "Unauthorized Command Message", active: true, hits: 18 },
        { id: "T0836", name: "Modify Parameter", active: true, hits: 9 }
      ]
    },
    {
      name: "Inhibit Response Function",
      techniques: [
        { id: "T0857", name: "System Firmware Modification", active: false, hits: 0 },
        { id: "T0804", name: "Block Reporting Message", active: true, hits: 6 }
      ]
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Crosshair className="w-6 h-6 text-rose-400" />
          <h2 className="text-xl font-bold text-white">MITRE ATT&CK® for Industrial Control Systems (ICS) Heatmap</h2>
        </div>
        <span className="text-xs font-mono text-slate-400">v14.1 Enterprise ICS Spec</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {tactics.map((tac) => (
          <div key={tac.name} className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 space-y-3">
            <h3 className="text-xs font-bold font-mono text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2">
              {tac.name}
            </h3>
            <div className="space-y-2">
              {tac.techniques.map((tech) => (
                <div
                  key={tech.id}
                  className={`p-2.5 rounded border text-xs transition ${
                    tech.active
                      ? "bg-rose-950/40 border-rose-500/50 text-rose-200"
                      : "bg-slate-900/40 border-slate-800/80 text-slate-500"
                  }`}
                >
                  <div className="flex justify-between items-center font-mono font-bold mb-1">
                    <span>{tech.id}</span>
                    {tech.active && (
                      <span className="px-1.5 py-0.5 bg-rose-600/60 text-white rounded text-[10px]">
                        {tech.hits} ALERTS
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] leading-tight">{tech.name}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
