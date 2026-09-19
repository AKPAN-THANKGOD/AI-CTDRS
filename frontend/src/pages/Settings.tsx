import React, { useEffect, useState } from 'react';
import api from '../services/api';
import toast, { Toaster } from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';

interface Settings {
  confidence_threshold: number;
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
  auto_create_incidents: boolean;
  auto_create_alerts: boolean;
  websocket_notifications: boolean;
  updated_at: string;
  updated_by: string;
}

interface Health {
  database: { size_mb: number; engine: string };
  totals: { threats: number; incidents: number; alerts: number; users: number };
  last_24h: { threats: number; incidents: number };
  critical: { threats: number; open_incidents: number; pending_alerts: number };
  server_time: string;
}

export default function Settings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const { isAdmin } = useAuth();

  const fetchSettings = async () => {
    try {
      const [settingsRes, healthRes] = await Promise.all([
        api.get('/settings/'),
        api.get('/settings/health/'),
      ]);
      setSettings(settingsRes.data);
      setHealth(healthRes.data);
    } catch (err) {
      toast.error("Failed to load settings");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      const res = await api.patch('/settings/', {
        confidence_threshold: settings.confidence_threshold,
        critical_threshold: settings.critical_threshold,
        high_threshold: settings.high_threshold,
        medium_threshold: settings.medium_threshold,
        auto_create_incidents: settings.auto_create_incidents,
        auto_create_alerts: settings.auto_create_alerts,
        websocket_notifications: settings.websocket_notifications,
      });
      setSettings(res.data);
      setHasChanges(false);
      toast.success("✅ Settings saved successfully!");
    } catch (err: any) {
      const errors = err.response?.data;
      const errorMsg = errors ? Object.values(errors).flat().join(', ') : "Failed to save";
      toast.error(errorMsg as string);
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: keyof Settings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, [key]: value });
    setHasChanges(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading settings...
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="p-6 text-red-400">Failed to load settings</div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <Toaster position="top-right" />

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">⚙️ System Settings</h1>
          <p className="text-gray-400 text-sm mt-1">
            Configure AI detection thresholds and system behavior
            {settings.updated_by && (
              <span className="ml-2 text-gray-500">
                • Last updated by {settings.updated_by} on {new Date(settings.updated_at).toLocaleString()}
              </span>
            )}
          </p>
        </div>
        {hasChanges && isAdmin && (
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            {saving ? '💾 Saving...' : '💾 Save Changes'}
          </button>
        )}
      </div>

      {/* System Health Overview */}
      {health && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">🖥️ System Health</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase">Database</p>
              <p className="text-white text-2xl font-bold mt-1">{health.database.size_mb} MB</p>
              <p className="text-gray-500 text-xs">{health.database.engine}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase">Total Threats</p>
              <p className="text-white text-2xl font-bold mt-1">{health.totals.threats}</p>
              <p className="text-gray-500 text-xs">+{health.last_24h.threats} in 24h</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase">Open Incidents</p>
              <p className="text-yellow-400 text-2xl font-bold mt-1">{health.critical.open_incidents}</p>
              <p className="text-gray-500 text-xs">{health.totals.incidents} total</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase">Pending Alerts</p>
              <p className="text-red-400 text-2xl font-bold mt-1">{health.critical.pending_alerts}</p>
              <p className="text-gray-500 text-xs">{health.totals.alerts} total</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Detection Thresholds */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-bold text-white mb-2">🎯 AI Detection Thresholds</h2>
        <p className="text-gray-400 text-sm mb-6">
          Adjust how sensitive the AI model is when detecting threats.
          {isAdmin ? "" : " (Read-only for analysts)"}
        </p>

        <div className="space-y-6">
          {/* Main Confidence Threshold */}
          <div className="bg-blue-950/30 border border-blue-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <label className="text-white font-semibold">
                🎯 Minimum Confidence to Flag as Threat
              </label>
              <span className="text-blue-400 font-mono text-lg font-bold">
                {(settings.confidence_threshold * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-gray-400 text-xs mb-3">
              Traffic with confidence below this will be classified as benign.
            </p>
            <input
              type="range"
              min="50"
              max="99"
              value={settings.confidence_threshold * 100}
              onChange={(e) => updateSetting('confidence_threshold', parseInt(e.target.value) / 100)}
              disabled={!isAdmin}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-50"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>50% (Sensitive)</span>
              <span>99% (Strict)</span>
            </div>
          </div>

          {/* Severity Thresholds */}
          <div>
            <h3 className="text-white font-semibold mb-4">📊 Severity Classification</h3>
            <div className="space-y-4">
              <SeveritySlider
                label="Critical Threshold"
                color="red"
                value={settings.critical_threshold}
                onChange={(v) => updateSetting('critical_threshold', v)}
                disabled={!isAdmin}
              />
              <SeveritySlider
                label="High Threshold"
                color="orange"
                value={settings.high_threshold}
                onChange={(v) => updateSetting('high_threshold', v)}
                disabled={!isAdmin}
              />
              <SeveritySlider
                label="Medium Threshold"
                color="yellow"
                value={settings.medium_threshold}
                onChange={(v) => updateSetting('medium_threshold', v)}
                disabled={!isAdmin}
              />
            </div>
            <p className="text-gray-500 text-xs mt-3">
              Anything below the medium threshold is classified as <span className="text-green-400">Low</span> severity.
            </p>
          </div>
        </div>
      </div>

      {/* Feature Toggles */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-bold text-white mb-2">🔧 Feature Toggles</h2>
        <p className="text-gray-400 text-sm mb-6">
          Enable or disable automated system features.
        </p>

        <div className="space-y-4">
          <Toggle
            label="Auto-Create Incidents"
            description="Automatically create an incident record when a new threat is detected"
            checked={settings.auto_create_incidents}
            onChange={(v) => updateSetting('auto_create_incidents', v)}
            disabled={!isAdmin}
          />
          <Toggle
            label="Auto-Create Alerts"
            description="Automatically create an alert notification for every detected threat"
            checked={settings.auto_create_alerts}
            onChange={(v) => updateSetting('auto_create_alerts', v)}
            disabled={!isAdmin}
          />
          <Toggle
            label="WebSocket Notifications"
            description="Push real-time threat notifications to all connected clients"
            checked={settings.websocket_notifications}
            onChange={(v) => updateSetting('websocket_notifications', v)}
            disabled={!isAdmin}
          />
        </div>
      </div>

      {/* Info Card for Analysts */}
      {!isAdmin && (
        <div className="bg-blue-950/30 border border-blue-800 rounded-xl p-4">
          <p className="text-blue-300 text-sm">
            🔒 <strong>Read-Only Mode:</strong> You're viewing settings as an analyst. 
            Only administrators can modify these configurations.
          </p>
        </div>
      )}
    </div>
  );
}

function SeveritySlider({
  label, color, value, onChange, disabled
}: {
  label: string;
  color: 'red' | 'orange' | 'yellow';
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
}) {
  const colorClasses = {
    red: 'text-red-400 accent-red-500',
    orange: 'text-orange-400 accent-orange-500',
    yellow: 'text-yellow-400 accent-yellow-500',
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <label className={`text-sm font-medium ${colorClasses[color]}`}>
          {label}
        </label>
        <span className={`font-mono font-bold ${colorClasses[color]}`}>
          {(value * 100).toFixed(0)}%
        </span>
      </div>
      <input
        type="range"
        min="50"
        max="99"
        value={value * 100}
        onChange={(e) => onChange(parseInt(e.target.value) / 100)}
        disabled={disabled}
        className={`w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer ${colorClasses[color]} disabled:opacity-50`}
      />
    </div>
  );
}

function Toggle({
  label, description, checked, onChange, disabled
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 bg-gray-800 rounded-lg p-4">
      <div className="flex-1">
        <p className="text-white font-medium">{label}</p>
        <p className="text-gray-400 text-xs mt-1">{description}</p>
      </div>
      <button
        onClick={() => !disabled && onChange(!checked)}
        disabled={disabled}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? 'bg-green-600' : 'bg-gray-600'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}