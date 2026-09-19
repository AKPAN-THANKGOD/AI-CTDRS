import React, { useEffect, useState } from "react";
import api from "../services/api";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { useThreatWebSocket } from "../hooks/useThreatWebSocket"; // 👈 Added

interface Alert {
  id: string;
  title: string;
  message: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'acknowledged' | 'dismissed';
  threat: string | null;
  threat_id: string | null;
  created_at: string;
  acknowledged_by_email: string | null;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-400 bg-red-950",
  high: "text-orange-400 bg-orange-950",
  medium: "text-yellow-400 bg-yellow-950",
  low: "text-green-400 bg-green-950",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  // 👈 Listen to global WebSocket
  const { latestThreat } = useThreatWebSocket();

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/alerts/');
      setAlerts(res.data.results || res.data);
    } catch (error) {
      console.error("Failed to load alerts:", error);
    } finally {
      setLoading(false);
    }
  };

  // 👈 Auto-refresh when a new threat is detected globally
  useEffect(() => {
    if (latestThreat) {
      console.log("🔄 New threat detected, refreshing alerts...");
      fetchAlerts();
    }
  }, [latestThreat]);

  // Initial fetch
  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await api.post(`/alerts/${alertId}/acknowledge/`);
      toast.success("Alert acknowledged");
      fetchAlerts();
    } catch {
      toast.error("Failed to acknowledge alert");
    }
  };

  const handleAcknowledgeAll = async () => {
    try {
      await api.post('/alerts/acknowledge_all/');
      toast.success("All alerts acknowledged");
      fetchAlerts();
    } catch {
      toast.error("Failed to acknowledge all alerts");
    }
  };

  const handleDismiss = async (alertId: string) => {
    try {
      await api.delete(`/alerts/${alertId}/dismiss/`);
      toast.success("Alert dismissed");
      setAlerts(alerts.filter((a) => a.id !== alertId));
    } catch {
      toast.error("Failed to dismiss alert");
    }
  };

  const handleViewThreat = (alert: Alert) => {
    const threatId = alert.threat_id || alert.threat;
    if (!threatId) {
      toast.error("No threat linked to this alert");
      return;
    }
    navigate('/threats', { state: { viewThreatId: threatId } });
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading alerts...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Alerts</h1>
          <p className="text-gray-400 text-sm mt-1">Monitor and respond to security alerts ({alerts.length} total)</p>
        </div>
        {alerts.length > 0 && (
          <button
            onClick={handleAcknowledgeAll}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            ✓ Acknowledge All
          </button>
        )}
      </div>

      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-500">
            <p className="text-4xl mb-3">🔔</p>
            <p>No alerts yet. Submit a threat via Threat Analysis to generate alerts.</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-gray-900 border border-gray-800 rounded-xl p-5 ${
                alert.status === 'pending' ? 'border-l-4 border-l-red-500' : ''
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <h3 className="text-white font-semibold">{alert.title}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${SEVERITY_COLORS[alert.severity]}`}>
                      {alert.severity}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      alert.status === 'pending' ? 'bg-red-900 text-red-300' :
                      alert.status === 'acknowledged' ? 'bg-blue-900 text-blue-300' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {alert.status}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm">{alert.message}</p>
                  <p className="text-gray-500 text-xs mt-2">
                    {new Date(alert.created_at).toLocaleString()}
                    {alert.acknowledged_by_email && ` • Acknowledged by ${alert.acknowledged_by_email}`}
                  </p>
                </div>
                <div className="flex gap-2 ml-4 flex-wrap justify-end">
                  {(alert.threat || alert.threat_id) && (
                    <button
                      onClick={() => handleViewThreat(alert)}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-xs font-medium"
                    >
                      🔍 View Threat
                    </button>
                  )}
                  {alert.status === 'pending' && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium"
                    >
                      ✓ Acknowledge
                    </button>
                  )}
                  <button
                    onClick={() => handleDismiss(alert.id)}
                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-medium"
                  >
                    × Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}