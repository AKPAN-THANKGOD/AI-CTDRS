export interface Threat {
  id: string;
  threat_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source_ip: string;
  destination_ip: string | null;
  confidence: number;
  status: 'open' | 'responded' | 'resolved';
  detected_at: string;
  responded_at: string | null;
  resolved_at: string | null;
  notes: string;
  raw_features?: Record<string, any>;
  shap_explanation?: Array<{ feature: string; shap_value: number; input_value: number }>;
  lime_explanation?: Array<{ feature: string; lime_weight: number }>;
}

export interface DashboardStats {
  threats_last_24h: number;
  open_incidents: number;
  critical_threats: number;
  unacknowledged_alerts: number;
  top_threat_types: Array<{ threat_type: string; count: number }>;
  threat_trend_7d: Array<{ day: string; count: number }>;
}