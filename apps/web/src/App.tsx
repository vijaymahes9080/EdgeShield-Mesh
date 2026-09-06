import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewView } from './components/OverviewView';
import { DevicesView } from './components/DevicesView';
import { TelemetryView } from './components/TelemetryView';
import { IncidentsView } from './components/IncidentsView';
import { ApprovalsView } from './components/ApprovalsView';
import { SimulatorView } from './components/SimulatorView';
import { AuditView } from './components/AuditView';
import { SettingsView } from './components/SettingsView';
import { LoginView } from './components/LoginView';
import { ApiService } from './api';
import {
  UserPublic,
  Device,
  NormalizedTelemetry,
  Incident,
  RemediationProposal,
  AuditEvent,
  HealthSummary,
  DetectionRule
} from './types';

export function App() {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Core domain data state
  const [devices, setDevices] = useState<Device[]>([]);
  const [health, setHealth] = useState<HealthSummary | null>(null);
  const [telemetry, setTelemetry] = useState<NormalizedTelemetry[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [proposals, setProposals] = useState<RemediationProposal[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditEvent[]>([]);
  const [rules, setRules] = useState<DetectionRule[]>([]);

  // Selection states
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [selectedProposal, setSelectedProposal] = useState<RemediationProposal | null>(null);
  const [isTicking, setIsTicking] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);

  // 1. Initial Auth Check & Data Load
  useEffect(() => {
    const initApp = async () => {
      const token = ApiService.getToken();
      if (token) {
        try {
          const me: any = await ApiService.getMe();
          setUser(me);
          await loadAllData();
        } catch {
          ApiService.setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initApp();
  }, []);

  const loadAllData = async () => {
    try {
      const [devs, hlth, telem, incs, props, auds, rls] = await Promise.all([
        ApiService.getDevices().catch(() => []),
        ApiService.getHealthSummary().catch(() => null),
        ApiService.getTelemetryHistory(undefined, 50).catch(() => []),
        ApiService.getIncidents(50).catch(() => []),
        ApiService.getProposals().catch(() => []),
        ApiService.getAuditLogs(100).catch(() => []),
        ApiService.getRules().catch(() => []),
      ]);

      setDevices(devs);
      setHealth(hlth);
      setTelemetry(telem);
      setIncidents(incs);
      setProposals(props);
      setAuditLogs(auds);
      setRules(rls);

      if (incs.length > 0 && !selectedIncident) {
        setSelectedIncident(incs[0]);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  };

  // 2. WebSocket Connection for Real-Time Streaming
  useEffect(() => {
    if (!user) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry/ws`;

    const connectWs = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'telemetry') {
              const newTelem: NormalizedTelemetry = msg.data;
              setTelemetry((prev) => [newTelem, ...prev.slice(0, 99)]);
              
              // If anomalies were detected or incidents created, refresh incidents and proposals
              if (msg.anomalies_detected > 0 || (msg.incidents_created && msg.incidents_created.length > 0)) {
                ApiService.getIncidents(50).then(setIncidents);
                ApiService.getProposals().then(setProposals);
                ApiService.getAuditLogs(100).then(setAuditLogs);
                ApiService.getHealthSummary().then(setHealth);
              }
            }
          } catch (e) {
            console.error('WS parse error:', e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          setTimeout(connectWs, 3000); // Reconnect
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (err) {
        console.error('WS init error:', err);
      }
    };

    connectWs();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user]);

  // Periodic Keepalive poll for data
  useEffect(() => {
    if (!user) return;
    const interval = setInterval(() => {
      ApiService.getHealthSummary().then(setHealth).catch(() => {});
      ApiService.getIncidents(50).then(setIncidents).catch(() => {});
      ApiService.getProposals().then(setProposals).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, [user]);

  // Action Handlers
  const handleTickDevices = async () => {
    setIsTicking(true);
    try {
      await ApiService.tickAllDevices();
      await loadAllData();
    } catch (err) {
      console.error('Tick error:', err);
    } finally {
      setIsTicking(false);
    }
  };

  const handleReanalyzeIncident = async (incidentId: string) => {
    setIsAnalyzing(true);
    try {
      await ApiService.reanalyzeIncident(incidentId);
      const inc = await ApiService.getIncident(incidentId);
      setSelectedIncident(inc);
      await loadAllData();
    } catch (err) {
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleApproveProposal = async (proposalId: string, reason: string, idempotencyKey: string) => {
    await ApiService.approveProposal(proposalId, reason, idempotencyKey);
    await loadAllData();
  };

  const handleRejectProposal = async (proposalId: string, reason: string, idempotencyKey: string) => {
    await ApiService.rejectProposal(proposalId, reason, idempotencyKey);
    await loadAllData();
  };

  const handleLogout = () => {
    ApiService.setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#060a12] text-cyan-400 font-mono text-sm">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span>INITIALIZING EDGESHIELD SECURE MESH CONSOLE...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <LoginView
        onLoginSuccess={(auth) => {
          setUser(auth.user);
          loadAllData();
        }}
      />
    );
  }

  const pendingProposalsCount = proposals.filter((p) => p.status === 'pending').length;

  return (
    <div className="min-h-screen flex flex-col bg-[#060a12] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar
        user={user}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        wsConnected={wsConnected}
        incidentCount={incidents.length}
        pendingApprovalCount={pendingProposalsCount}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
        {activeTab === 'overview' && (
          <OverviewView
            health={health}
            devices={devices}
            incidents={incidents}
            proposals={proposals}
            onSelectIncident={(inc) => {
              setSelectedIncident(inc);
              setActiveTab('incidents');
            }}
            onSelectProposal={(prop) => {
              setSelectedProposal(prop);
              setActiveTab('approvals');
            }}
            onTickDevices={handleTickDevices}
            onNavigateTab={setActiveTab}
            isTicking={isTicking}
          />
        )}

        {activeTab === 'devices' && (
          <DevicesView
            devices={devices}
            onSelectDevice={(d) => {
              setActiveTab('telemetry');
            }}
          />
        )}

        {activeTab === 'telemetry' && (
          <TelemetryView
            telemetry={telemetry}
            devices={devices}
            onTickDevices={handleTickDevices}
            isTicking={isTicking}
          />
        )}

        {activeTab === 'incidents' && (
          <IncidentsView
            incidents={incidents}
            selectedIncident={selectedIncident}
            onSelectIncident={setSelectedIncident}
            onReanalyze={handleReanalyzeIncident}
            isAnalyzing={isAnalyzing}
          />
        )}

        {activeTab === 'approvals' && (
          <ApprovalsView
            proposals={proposals}
            onApprove={handleApproveProposal}
            onReject={handleRejectProposal}
            selectedProposal={selectedProposal}
            onSelectProposal={setSelectedProposal}
          />
        )}

        {activeTab === 'simulator' && (
          <SimulatorView
            onAttackTriggered={loadAllData}
          />
        )}

        {activeTab === 'audit' && (
          <AuditView
            auditLogs={auditLogs}
            onRefresh={loadAllData}
            isLoading={false}
          />
        )}

        {activeTab === 'settings' && (
          <SettingsView
            rules={rules}
            user={user}
            onRefreshRules={loadAllData}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 px-4 py-4 text-center text-[11px] text-slate-500 font-mono">
        EdgeShield Mesh v1.0.0 • Open Source Agentic IoT Cybersecurity for Rural Mesh Networks • Zero Disruptive Autonomous Actions Policy Enforced
      </footer>
    </div>
  );
}
