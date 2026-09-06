export type UserRole = 'operator' | 'analyst' | 'admin';

export interface UserPublic {
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserPublic;
}

export type DeviceStatus = 'active' | 'warning' | 'isolated' | 'offline' | 'unauthorized';

export interface Device {
  id: string;
  name: string;
  device_type: string;
  zone: string;
  owner: string;
  status: DeviceStatus;
  firmware_version: string;
  hardware_rev: string;
  ip_address: string;
  mac_address: string;
  last_seen: string;
  telemetry_interval_sec: number;
  expected_topics: string[];
  allowed_actuators: string[];
  is_virtual: boolean;
  metadata?: Record<string, any>;
}

export interface NormalizedTelemetry {
  event_id: string;
  device_id: string;
  device_type: string;
  zone: string;
  timestamp: string;
  seq: number;
  nonce: string;
  payload_hash: string;
  battery_level?: number;
  signal_rssi?: number;
  measurements: Record<string, any>;
  is_valid: boolean;
  validation_errors: string[];
}

export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'detected' | 'investigating' | 'pending_approval' | 'approved' | 'mitigated' | 'dismissed';

export interface Citation {
  document_id: string;
  version: string;
  title: string;
  section: string;
  snippet: string;
  relevance_score: number;
  doc_hash: string;
  source_type: string;
}

export interface EvidenceItem {
  id: string;
  evidence_type: string;
  source: string;
  timestamp: string;
  data: Record<string, any>;
  description: string;
}

export interface RiskAssessment {
  incident_id: string;
  device_criticality: string;
  threat_vector: string;
  potential_impact: string;
  calculated_risk: IncidentSeverity;
  safety_impact: string;
  confidence: number;
}

export interface RecommendedAction {
  type: string;
  scope: string;
  reason: string;
  requires_approval: boolean;
  suggested_params?: Record<string, any>;
}

export interface Incident {
  id: string;
  title: string;
  device_id: string;
  detector_id: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  confidence: number;
  observed_facts: string[];
  derived_findings: string[];
  recommendations: string[];
  evidence_items: EvidenceItem[];
  citations: Citation[];
  risk_assessment?: RiskAssessment;
  recommended_action?: RecommendedAction;
  limitations: string[];
  created_at: string;
  updated_at: string;
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'expired' | 'executed' | 'rolled_back';

export interface RemediationProposal {
  id: string;
  incident_id: string;
  action_type: string;
  target_device_id: string;
  scope: string;
  reason: string;
  impact_summary: string;
  rollback_procedure: string;
  requires_approval: boolean;
  parameters: Record<string, any>;
  created_at: string;
  expires_at: string;
  status: ApprovalStatus;
  idempotency_key: string;
  executed_at?: string;
  execution_result?: string;
}

export interface Approval {
  id: string;
  proposal_id: string;
  status: ApprovalStatus;
  actor_username: string;
  actor_role: string;
  reason: string;
  idempotency_key: string;
  action_taken_at: string;
}

export interface AuditEvent {
  event_id: string;
  timestamp: string;
  actor: string;
  actor_role: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  status: string;
  prev_hash: string;
  entry_hash: string;
}

export interface HealthSummary {
  total_devices: number;
  active: number;
  warning: number;
  isolated: number;
  offline: number;
  healthy_percentage: number;
  last_updated: string;
}

export interface DetectionRule {
  rule_id: string;
  name: string;
  detector_id: string;
  enabled: boolean;
  severity: IncidentSeverity;
  parameters: Record<string, any>;
  description?: string;
}
