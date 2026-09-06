import React from 'react';
import { Shield, Radio, Activity, AlertTriangle, CheckCircle, User, LogOut } from 'lucide-react';
import { UserPublic } from '../types';

interface NavbarProps {
  user: UserPublic | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  wsConnected: boolean;
  incidentCount: number;
  pendingApprovalCount: number;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  activeTab,
  setActiveTab,
  wsConnected,
  incidentCount,
  pendingApprovalCount,
  onLogout
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'devices', label: 'Devices', icon: Radio },
    { id: 'telemetry', label: 'Live Telemetry', icon: Activity },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle, badge: incidentCount },
    { id: 'approvals', label: 'Approval Gate', icon: CheckCircle, badge: pendingApprovalCount, highlight: pendingApprovalCount > 0 },
    { id: 'simulator', label: 'Attack Simulator', icon: Shield },
    { id: 'audit', label: 'Audit Ledger', icon: Shield },
    { id: 'settings', label: 'Rules & Settings', icon: Shield },
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#070d18]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 border border-cyan-500/40 text-cyan-400 glow-cyan">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
                EdgeShield Mesh
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-mono uppercase rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800">
                v1.0.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Agentic IoT Cybersecurity for Rural Mesh</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-950'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className={`ml-1 px-1.5 py-0.2 text-[10px] font-bold rounded-full ${
                    item.highlight ? 'bg-rose-500 text-white animate-bounce' : 'bg-slate-800 text-cyan-400 border border-slate-700'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Status & User */}
        <div className="flex items-center space-x-3">
          {/* WS status */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-rose-500'}`} />
            <span className="text-[11px] text-slate-400 hidden sm:inline">{wsConnected ? 'LIVE WS' : 'OFFLINE'}</span>
          </div>

          {/* User Profile */}
          {user && (
            <div className="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg">
              <User className="w-3.5 h-3.5 text-cyan-400" />
              <div className="text-left hidden sm:block">
                <div className="text-xs font-semibold text-slate-200 leading-none">{user.full_name || user.username}</div>
                <div className="text-[10px] text-cyan-400 uppercase font-mono mt-0.5">{user.role}</div>
              </div>
              <button
                onClick={onLogout}
                title="Logout"
                className="ml-2 text-slate-400 hover:text-rose-400 transition-colors p-1"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};
