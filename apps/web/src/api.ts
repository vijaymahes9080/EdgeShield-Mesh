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

const API_BASE = (import.meta as any).env?.VITE_API_URL || '/api/v1';

// Initial Mock Dataset for GitHub Pages and Offline Demo Mode
const MOCK_DEVICES: Device[] = [
  {
    id: "soil-moisture-alpha",
    name: "Soil Moisture Sensor Alpha",
    device_type: "soil_moisture",
    zone: "North Farm - Sector 4",
    owner: "agri_ops",
    status: "active",
    firmware_version: "v1.2.0",
    hardware_rev: "ESP32-REV3",
    ip_address: "192.168.10.45",
    mac_address: "AA:BB:CC:11:22:33",
    last_seen: new Date().toISOString(),
    telemetry_interval_sec: 10,
    expected_topics: ["agri/soil/alpha/telemetry"],
    allowed_actuators: [],
    is_virtual: true
  },
  {
    id: "weather-beta",
    name: "Weather Station Beta",
    device_type: "weather_station",
    zone: "Ridge Station 2",
    owner: "agri_ops",
    status: "active",
    firmware_version: "v2.0.1",
    hardware_rev: "STM32F4-LEO",
    ip_address: "192.168.10.46",
    mac_address: "AA:BB:CC:44:55:66",
    last_seen: new Date().toISOString(),
    telemetry_interval_sec: 30,
    expected_topics: ["agri/weather/beta/telemetry"],
    allowed_actuators: [],
    is_virtual: true
  },
  {
    id: "valve-gamma",
    name: "Main Irrigation Valve Gamma",
    device_type: "irrigation_valve",
    zone: "Pumping Station East",
    owner: "irrigation_control",
    status: "warning",
    firmware_version: "v1.1.0",
    hardware_rev: "RP2040-CAN",
    ip_address: "192.168.10.47",
    mac_address: "AA:BB:CC:77:88:99",
    last_seen: new Date().toISOString(),
    telemetry_interval_sec: 5,
    expected_topics: ["agri/irrigation/valve/status"],
    allowed_actuators: ["VALVE_CUTOFF", "PRESSURE_RELIEF"],
    is_virtual: true
  },
  {
    id: "solar-pump-delta",
    name: "Solar VFD Pump Delta",
    device_type: "solar_pump",
    zone: "Solar Field B",
    owner: "energy_ops",
    status: "active",
    firmware_version: "v1.0.4",
    hardware_rev: "TI-C2000-VFD",
    ip_address: "192.168.10.48",
    mac_address: "AA:BB:CC:AA:BB:CC",
    last_seen: new Date().toISOString(),
    telemetry_interval_sec: 15,
    expected_topics: ["agri/solar/pump/telemetry"],
    allowed_actuators: ["VFD_SPEED_REGULATOR"],
    is_virtual: true
  },
  {
    id: "greenhouse-epsilon",
    name: "Greenhouse Climate Epsilon",
    device_type: "greenhouse_env",
    zone: "Greenhouse Complex 1",
    owner: "horticulture",
    status: "active",
    firmware_version: "v0.9.1",
    hardware_rev: "ESP32-S3-CAM",
    ip_address: "192.168.10.49",
    mac_address: "AA:BB:CC:DD:EE:FF",
    last_seen: new Date().toISOString(),
    telemetry_interval_sec: 10,
    expected_topics: ["agri/greenhouse/env/telemetry"],
    allowed_actuators: ["MIST_FAN_CONTROL"],
    is_virtual: true
  }
];

const MOCK_INCIDENTS: Incident[] = [
  {
    id: "inc-778899",
    title: "Replay Attack & Desynchronized Frame Counter",
    device_id: "valve-gamma",
    detector_id: "DET_REPLAY_FRAME_COUNTER",
    severity: "critical",
    status: "pending_approval",
    confidence: 0.98,
    observed_facts: [
      "Duplicate 32-bit Frame Counter (FCnt: 1042) observed from DevAddr 78563412",
      "HMAC signature mismatch on repeated payload envelope",
      "Burst rate anomaly: 14 packets/sec (Baseline threshold: 2 packets/sec)"
    ],
    derived_findings: [
      "LoRaWAN MAC Layer Replay attack with injected actuator override",
      "Attacker attempting unauthorized solenoid cycle without physical sensor trigger",
      "Correlated with MITRE ATT&CK for ICS T0855 (Unauthorized Command Message)"
    ],
    recommendations: [
      "Enforce network quarantine on valve-gamma ingress port",
      "Ramp down solar pump speed before hydraulic valve closure",
      "Rotate LoRaWAN AppSessionKey via OTA re-keying"
    ],
    evidence_items: [
      {
        id: "ev-01",
        evidence_type: "TELEMETRY_LOG",
        source: "edge_gateway",
        timestamp: new Date().toISOString(),
        data: { fcnt: 1042, topic: "agri/irrigation/valve/status" },
        description: "Replayed frame packet captured by edge gateway"
      }
    ],
    citations: [
      {
        document_id: "DOC-SOP-IRRIGATION-04",
        version: "v2.1",
        title: "Standard Operating Procedure: Irrigation Solenoid Quarantine",
        section: "Section 3.2 - Replay Defense",
        snippet: "When frame counter replay is detected on solenoid valve gamma, isolate network ingress before hydraulic cutoff.",
        relevance_score: 0.98,
        doc_hash: "a4f8e7...",
        source_type: "runbook"
      }
    ],
    limitations: ["Satellite backhaul latency 1.4s during pass"],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const MOCK_PROPOSALS: RemediationProposal[] = [
  {
    id: "prop-001",
    incident_id: "inc-778899",
    action_type: "ISOLATE_DEVICE",
    target_device_id: "valve-gamma",
    scope: "valve-gamma",
    reason: "Prevent unauthorized solenoid actuation without disrupting upstream solar pump",
    impact_summary: "Will isolate valve-gamma from network. Downstream pressure estimated at 4.2 Bar (Safe under 8.0 Bar limit).",
    rollback_procedure: "Restore normal ebtables rule and reconnect MQTT session token.",
    requires_approval: true,
    status: "pending",
    idempotency_key: "idemp-prop-001-9988",
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 86400000).toISOString(),
    parameters: {
      isolation_mode: "ebtables_drop_ingress",
      fallback_failsafe: "mechanical_spring_return"
    }
  }
];

export class ApiService {
  private static token: string | null = localStorage.getItem('edgeshield_token') || 'demo_jwt_token';

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

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        // Fallback for static servers like GitHub Pages returning 404/405
        console.warn(`[EdgeShield] Remote API returned status ${response.status} for ${endpoint}. Falling back to client demo mode.`);
        return this.getMockFallback<T>(endpoint, options);
      }

      return await response.json();
    } catch (networkError) {
      // Network unreachable or static host -> graceful mock fallback
      console.warn(`[EdgeShield] Network error fetching ${endpoint}. Falling back to client demo mode.`, networkError);
      return this.getMockFallback<T>(endpoint, options);
    }
  }

  // Internal Mock Fallback Provider for Static Hosting (GitHub Pages) & Offline Demos
  private static getMockFallback<T>(endpoint: string, options: RequestInit): T {
    if (endpoint.includes('/auth/login') || endpoint.includes('/auth/me')) {
      const username = options.body ? JSON.parse(options.body as string).username : 'operator';
      return {
        access_token: 'mock_demo_jwt_token_valid',
        token_type: 'bearer',
        expires_in: 86400,
        user: {
          username: username || 'operator',
          email: `${username || 'operator'}@edgeshield.internal`,
          full_name: 'Lead Security Operator',
          role: (username === 'admin' ? 'admin' : (username === 'analyst' ? 'analyst' : 'operator')),
          is_active: true
        }
      } as unknown as T;
    }

    if (endpoint.includes('/devices/health-summary')) {
      return {
        total_devices: MOCK_DEVICES.length,
        active: 4,
        warning: 1,
        isolated: 0,
        offline: 0,
        healthy_percentage: 94.5,
        last_updated: new Date().toISOString()
      } as unknown as T;
    }

    if (endpoint.includes('/devices')) {
      return MOCK_DEVICES as unknown as T;
    }

    if (endpoint.includes('/telemetry/history')) {
      const history: NormalizedTelemetry[] = [];
      const now = Date.now();
      for (let i = 20; i >= 0; i--) {
        history.push({
          event_id: `evt-${i}`,
          device_id: 'soil-moisture-alpha',
          device_type: 'soil_moisture',
          zone: 'North Farm - Sector 4',
          timestamp: new Date(now - i * 15000).toISOString(),
          seq: 100 - i,
          nonce: `nonce-${100 - i}`,
          payload_hash: 'e3b0c442...',
          battery_level: 98 - (i * 0.1),
          signal_rssi: -65 + (i % 3),
          measurements: {
            soil_moisture: 42.5 + Math.sin(i) * 2.0,
            soil_temp: 21.4,
            ph_level: 6.8
          },
          is_valid: true,
          validation_errors: []
        });
      }
      return history as unknown as T;
    }

    if (endpoint.includes('/incidents')) {
      return MOCK_INCIDENTS as unknown as T;
    }

    if (endpoint.includes('/approvals/proposals')) {
      return MOCK_PROPOSALS as unknown as T;
    }

    if (endpoint.includes('/approvals/approve') || endpoint.includes('/approvals/reject')) {
      const isApproved = endpoint.includes('/approve');
      return {
        id: 'app-998811',
        proposal_id: 'prop-001',
        actor_username: 'operator',
        actor_role: 'operator',
        status: isApproved ? 'approved' : 'rejected',
        reason: 'Authorized by security operator via verified runbook',
        action_taken_at: new Date().toISOString(),
        idempotency_key: 'idemp-123'
      } as unknown as T;
    }

    if (endpoint.includes('/audit')) {
      const audits: AuditEvent[] = [
        {
          event_id: 'audit-001',
          timestamp: new Date().toISOString(),
          actor: 'operator',
          actor_role: 'operator',
          action: 'INCIDENT_TRIAGED',
          resource_type: 'incident',
          resource_id: 'inc-778899',
          details: { action: 'Verified SOP runbook & blast radius' },
          status: 'SUCCESS',
          entry_hash: 'sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
          prev_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000'
        }
      ];
      return audits as unknown as T;
    }

    if (endpoint.includes('/simulations/')) {
      return {
        status: 'SIMULATION_TRIGGERED',
        vector: 'LoRaWAN_Replay',
        simulated_packets_injected: 5,
        target_device: 'valve-gamma'
      } as unknown as T;
    }

    if (endpoint.includes('/settings/rules')) {
      const rules: DetectionRule[] = [
        {
          rule_id: 'DET_REPLAY',
          name: 'LoRaWAN Anti-Replay Gate',
          detector_id: 'DET_REPLAY_FRAME_COUNTER',
          description: 'Enforces 32-bit frame counter monotonicity',
          severity: 'critical',
          enabled: true,
          parameters: { max_seq_gap: 16384 }
        },
        {
          rule_id: 'DET_SNN_BURST',
          name: 'Neuromorphic LIF Pulse Detector',
          detector_id: 'DET_NEUROMORPHIC_SNN',
          description: 'Spiking neural model for rapid sensor deltas',
          severity: 'high',
          enabled: true,
          parameters: { membrane_threshold: 5.0, decay_rate: 0.5 }
        }
      ];
      return rules as unknown as T;
    }

    return {} as unknown as T;
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

  public static async getMe(): Promise<any> {
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

  public static async reanalyzeIncident(id: string): Promise<any> {
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
  public static async triggerAttack(vector: string): Promise<any> {
    return this.request(`/simulations/attack/${vector}`, { method: 'POST' });
  }

  public static async tickAllDevices(): Promise<any> {
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
