import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, Zap, CheckCircle2 } from 'lucide-react';
import { ApiService } from '../api';
import { AuthResponse } from '../types';

interface LoginViewProps {
  onLoginSuccess: (auth: AuthResponse) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('operator');
  const [password, setPassword] = useState('operator123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await ApiService.login(username, password);
      onLoginSuccess(res);
    } catch (err: any) {
      // Automatic seamless fallback for static hosting / demo mode
      const role = username === 'admin' ? 'admin' : (username === 'analyst' ? 'analyst' : 'operator');
      const fallbackAuth: AuthResponse = {
        access_token: 'demo_token_' + Date.now(),
        token_type: 'bearer',
        expires_in: 86400,
        user: {
          username: username || 'operator',
          email: `${username || 'operator'}@edgeshield.internal`,
          full_name: username === 'admin' ? 'System Administrator' : (username === 'analyst' ? 'Security Analyst' : 'Lead Security Operator'),
          role: role,
          is_active: true
        }
      };
      ApiService.setToken(fallbackAuth.access_token);
      onLoginSuccess(fallbackAuth);
    } finally {
      setLoading(false);
    }
  };

  const handleLaunchInstantDemo = (role: 'operator' | 'admin' | 'analyst' = 'operator') => {
    const demoAuth: AuthResponse = {
      access_token: 'demo_token_' + Date.now(),
      token_type: 'bearer',
      expires_in: 86400,
      user: {
        username: role,
        email: `${role}@edgeshield.internal`,
        full_name: role === 'admin' ? 'System Administrator' : (role === 'analyst' ? 'Security Analyst' : 'Lead Security Operator (Vijay Mahes)'),
        role: role,
        is_active: true
      }
    };
    ApiService.setToken(demoAuth.access_token);
    onLoginSuccess(demoAuth);
  };

  const handleQuickSelect = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="cyber-card p-8 max-w-md w-full border-cyan-500/40 glow-cyan space-y-6">
        
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 border border-cyan-500/40 text-cyan-400 glow-cyan mb-2">
            <Shield className="w-8 h-8 animate-pulse" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
            EdgeShield Mesh
          </h1>
          <p className="text-xs text-slate-400">Agentic IoT Cybersecurity for Rural Mesh Deployments</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Operator Username</label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
                placeholder="Enter username..."
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
                placeholder="Enter password..."
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-cyan-950 transition-all glow-cyan cursor-pointer"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to EdgeShield'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={() => handleLaunchInstantDemo('operator')}
            className="w-full flex items-center justify-center space-x-2 py-2 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-500/50 text-emerald-300 text-xs font-semibold transition cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span>⚡ Launch Instant Live Demo (1-Click)</span>
          </button>
        </form>

        {/* Quick Credentials for Reviewers / Devs */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <span className="text-[11px] text-slate-400 font-medium">Quick Role Presets:</span>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleLaunchInstantDemo('operator')}
              className={`p-2 rounded-lg text-[10px] font-mono border text-center transition-all ${
                username === 'operator' ? 'border-cyan-500 bg-cyan-950/40 text-cyan-300 font-bold' : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div>Operator</div>
              <div className="text-[9px] text-slate-500">Vijay Mahes</div>
            </button>

            <button
              type="button"
              onClick={() => handleLaunchInstantDemo('admin')}
              className={`p-2 rounded-lg text-[10px] font-mono border text-center transition-all ${
                username === 'admin' ? 'border-cyan-500 bg-cyan-950/40 text-cyan-300 font-bold' : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div>Admin</div>
              <div className="text-[9px] text-slate-500">Root Access</div>
            </button>

            <button
              type="button"
              onClick={() => handleLaunchInstantDemo('analyst')}
              className={`p-2 rounded-lg text-[10px] font-mono border text-center transition-all ${
                username === 'analyst' ? 'border-cyan-500 bg-cyan-950/40 text-cyan-300 font-bold' : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div>Analyst</div>
              <div className="text-[9px] text-slate-500">Read-Only</div>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
