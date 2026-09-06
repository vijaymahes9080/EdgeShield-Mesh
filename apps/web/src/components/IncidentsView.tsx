import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, BookOpen, Clock, Cpu, CheckCircle2, ChevronRight, X, Sparkles, FileText, Lock } from 'lucide-react';
import { Incident, IncidentSeverity, Citation, EvidenceItem } from '../types';

interface IncidentsViewProps {
  incidents: Incident[];
  selectedIncident: Incident | null;
  onSelectIncident: (inc: Incident | null) => void;
  onReanalyze: (incidentId: string) => void;
  isAnalyzing: boolean;
}

export const IncidentsView: React.FC<IncidentsViewProps> = ({
  incidents,
  selectedIncident,
  onSelectIncident,
  onReanalyze,
  isAnalyzing,
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  const filtered = severityFilter === 'all'
    ? incidents
    : incidents.filter((i) => i.severity === severityFilter);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 cyber-card p-4">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h2 className="font-bold text-slate-100 text-sm">Security Incident Management & RAG Evidence Center</h2>
        </div>

        <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 text-[11px] px-1.5">Severity:</span>
          {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2 py-0.5 rounded uppercase text-[10px] font-bold transition-all ${
                severityFilter === sev
                  ? 'bg-cyan-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Incident List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Incidents List */}
        <div className="lg:col-span-1 space-y-3">
          {filtered.length === 0 ? (
            <div className="cyber-card p-8 text-center text-slate-500 text-xs border-dashed">
              No incidents matching filter criteria.
            </div>
          ) : (
            filtered.map((inc) => {
              const isSelected = selectedIncident?.id === inc.id;
              const sevBadge =
                inc.severity === 'critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/50' :
                inc.severity === 'high' ? 'bg-amber-500/20 text-amber-300 border-amber-500/50' :
                inc.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50' :
                'bg-blue-500/20 text-blue-300 border-blue-500/50';

              return (
                <div
                  key={inc.id}
                  onClick={() => onSelectIncident(inc)}
                  className={`cyber-card p-4 cursor-pointer transition-all ${
                    isSelected ? 'border-cyan-400 bg-cyan-950/20 ring-1 ring-cyan-500/30' : 'hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded border ${sevBadge}`}>
                      {inc.severity}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{inc.id}</span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-100 mt-2">{inc.title}</h3>
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-1">
                    <span className="font-mono text-cyan-400">{inc.device_id}</span>
                    <span>•</span>
                    <span>{(inc.confidence * 100).toFixed(0)}% conf</span>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                    <span>{new Date(inc.created_at).toLocaleTimeString()}</span>
                    <span className="flex items-center text-cyan-400 font-semibold">
                      <span>Inspect</span>
                      <ChevronRight className="w-3 h-3 ml-0.5" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Detailed Incident Investigation View */}
        <div className="lg:col-span-2">
          {selectedIncident ? (
            <div className="cyber-card p-6 space-y-6">
              
              {/* Header */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-mono text-cyan-400">{selectedIncident.id}</span>
                    <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                      {selectedIncident.severity}
                    </span>
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
                      STATUS: {selectedIncident.status.toUpperCase()}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-100">{selectedIncident.title}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Target Device: <code className="text-cyan-400">{selectedIncident.device_id}</code> | Detector: <code className="text-slate-300">{selectedIncident.detector_id}</code>
                  </p>
                </div>

                <button
                  onClick={() => onReanalyze(selectedIncident.id)}
                  disabled={isAnalyzing}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 text-white text-xs font-semibold shadow-md shadow-cyan-950 transition-all hover:opacity-90"
                >
                  <Sparkles className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
                  <span>{isAnalyzing ? 'Analyzing...' : 'Re-Run Agent'}</span>
                </button>
              </div>

              {/* NON-NEGOTIABLE SEPARATION: Facts vs Findings vs Recommendations */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* 1. Observed Facts */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>1. Observed Facts</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {selectedIncident.observed_facts.map((fact, idx) => (
                      <li key={idx} className="flex items-start space-x-1.5">
                        <span className="text-cyan-500 mt-0.5">•</span>
                        <span>{fact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 2. Derived Findings */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                    <ShieldAlert className="w-4 h-4" />
                    <span>2. Derived Findings</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {selectedIncident.derived_findings.map((finding, idx) => (
                      <li key={idx} className="flex items-start space-x-1.5">
                        <span className="text-amber-500 mt-0.5">•</span>
                        <span>{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 3. Recommendations */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                    <FileText className="w-4 h-4" />
                    <span>3. Recommendations</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {selectedIncident.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-1.5">
                        <span className="text-emerald-500 mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>

              {/* RAG Runbook Citations Drawer */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <BookOpen className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs font-mono uppercase font-bold tracking-wider text-slate-200">
                    Evidence-Grounded RAG Runbook Citations ({selectedIncident.citations?.length || 0})
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedIncident.citations?.map((cit, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedCitation(cit)}
                      className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 hover:border-cyan-500/60 cursor-pointer transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-cyan-300">{cit.document_id}: {cit.title}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                          v{cit.version}
                        </span>
                      </div>
                      <p className="text-[11px] font-medium text-slate-400 mt-1">Section: <span className="text-slate-200">{cit.section}</span></p>
                      <p className="text-xs text-slate-300 mt-1.5 line-clamp-2 italic bg-slate-900/50 p-2 rounded border border-slate-800/60">
                        "{cit.snippet}"
                      </p>
                      <div className="flex items-center justify-between mt-2 text-[10px] text-slate-500 font-mono">
                        <span>Relevance: {(cit.relevance_score * 100).toFixed(0)}%</span>
                        <span className="text-cyan-400">View Full Snippet →</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Timeline */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs font-mono uppercase font-bold tracking-wider text-slate-200">
                    Correlated Evidence Timeline
                  </h3>
                </div>

                <div className="space-y-2">
                  {selectedIncident.evidence_items?.map((ev) => (
                    <div key={ev.id} className="p-3 rounded-lg bg-slate-950/50 border border-slate-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] font-mono text-cyan-400">{ev.id}</span>
                          <span className="text-[10px] uppercase px-1.5 rounded bg-slate-800 text-slate-300">{ev.evidence_type}</span>
                          <span className="text-slate-400">Source: {ev.source}</span>
                        </div>
                        <p className="text-slate-200 mt-1">{ev.description}</p>
                      </div>
                      <span className="text-[10px] font-mono text-slate-500 shrink-0">
                        {new Date(ev.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strict Zero-Autonomous Disruptive Action Notice */}
              <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-800/40 flex items-center space-x-3 text-xs text-cyan-300">
                <Lock className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>
                  <strong>HITL Policy Enforced:</strong> The agent has proposed a safe containment proposal. Navigate to the <strong>Approval Gate</strong> to authorize or reject execution.
                </span>
              </div>

            </div>
          ) : (
            <div className="cyber-card p-12 text-center text-slate-500 text-xs">
              Select an incident from the left panel to inspect observed facts, derived findings, citations, and evidence timeline.
            </div>
          )}
        </div>

      </div>

      {/* Citation Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="cyber-card p-6 max-w-xl w-full space-y-4 border-cyan-500/50">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">
                  {selectedCitation.document_id}: {selectedCitation.title}
                </h3>
              </div>
              <button onClick={() => setSelectedCitation(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-400">
                <span>Version: <strong className="text-cyan-300">{selectedCitation.version}</strong></span>
                <span>Section: <strong className="text-slate-200">{selectedCitation.section}</strong></span>
                <span>Score: <strong className="text-emerald-400">{(selectedCitation.relevance_score * 100).toFixed(0)}%</strong></span>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap border border-slate-800">
                {selectedCitation.snippet}
              </div>
              <div className="text-[10px] font-mono text-slate-500">
                Document SHA-256: {selectedCitation.doc_hash}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
