import {
  AuthResponse,
  Device,
  NormalizedTelemetry,
  Incident,
  RemediationProposal,
  Approval,
  AuditEvent,
  HealthSummary,
  DetectionRule
} from './types';

const API_BASE = '/api/v1';

export class ApiService {
  private static token: string | null = localStorage.getItem('edgeshield_token');

  public static setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('edgeshield_token', token);
    } else {
      localStorage.removeItem('edgeshield_token');
    }
  }

  public static getToken(): string | null {
    return this.token;
  }

  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  }

  // Auth
  public static async login(username: string, password: string): Promise<AuthResponse> {
    const data = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  public static async getMe() {
    return this.request('/auth/me');
  }

  // Devices
  public static async getDevices(): Promise<Device[]> {
    return this.request<Device[]>('/devices');
  }

  public static async getHealthSummary(): Promise<HealthSummary> {
    return this.request<HealthSummary>('/devices/health-summary');
  }

  // Telemetry
  public static async getTelemetryHistory(deviceId?: string, limit = 50): Promise<NormalizedTelemetry[]> {
    const query = deviceId ? `?device_id=${deviceId}&limit=${limit}` : `?limit=${limit}`;
    return this.request<NormalizedTelemetry[]>(`/telemetry/history${query}`);
  }

  // Incidents
  public static async getIncidents(limit = 50): Promise<Incident[]> {
    return this.request<Incident[]>(`/incidents?limit=${limit}`);
  }

  public static async getIncident(id: string): Promise<Incident> {
    return this.request<Incident>(`/incidents/${id}`);
  }

  public static async reanalyzeIncident(id: string) {
    return this.request(`/incidents/${id}/analyze`, { method: 'POST' });
  }

  // Approvals & Proposals
  public static async getProposals(): Promise<RemediationProposal[]> {
    return this.request<RemediationProposal[]>('/approvals/proposals');
  }

  public static async approveProposal(proposalId: string, reason: string, idempotencyKey: string): Promise<Approval> {
    return this.request<Approval>('/approvals/approve', {
      method: 'POST',
      body: JSON.stringify({
        proposal_id: proposalId,
        reason,
        idempotency_key: idempotencyKey,
      }),
    });
  }

  public static async rejectProposal(proposalId: string, reason: string, idempotencyKey: string): Promise<Approval> {
    return this.request<Approval>('/approvals/reject', {
      method: 'POST',
      body: JSON.stringify({
        proposal_id: proposalId,
        reason,
        idempotency_key: idempotencyKey,
      }),
    });
  }

  // Audit
  public static async getAuditLogs(limit = 100): Promise<AuditEvent[]> {
    return this.request<AuditEvent[]>(`/audit?limit=${limit}`);
  }

  // Simulations
  public static async triggerAttack(vector: string) {
    return this.request(`/simulations/attack/${vector}`, { method: 'POST' });
  }

  public static async tickAllDevices() {
    return this.request('/simulations/tick-all-devices', { method: 'POST' });
  }

  // Settings
  public static async getRules(): Promise<DetectionRule[]> {
    return this.request<DetectionRule[]>('/settings/rules');
  }

  public static async updateRule(ruleId: string, updateData: any): Promise<DetectionRule> {
    return this.request<DetectionRule>(`/settings/rules/${ruleId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }
}
