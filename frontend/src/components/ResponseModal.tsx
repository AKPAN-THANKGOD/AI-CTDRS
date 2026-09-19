import React, { useState } from "react";
import type { Threat } from "../types";
import { threatService } from "../services/api";
import toast from "react-hot-toast";

interface Props {
  threat: Threat;
  onClose: () => void;
  onResponded: () => void;
}

export default function ResponseModal({ threat, onClose, onResponded }: Props) {
  const [actionTaken, setActionTaken] = useState("");
  const [notes, setNotes] = useState("");
  const [severityAssessment, setSeverityAssessment] = useState<string>(threat.severity);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await threatService.respond(threat.id, {
        action_taken: actionTaken,
        notes: notes,
        severity_assessment: severityAssessment
      });
      toast.success("Response recorded successfully");
      onResponded();
      onClose();
    } catch {
      toast.error("Failed to record response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">Respond to Threat</h2>
              <p className="text-gray-400 text-sm mt-1">Document your response actions</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">×</button>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <h3 className="text-white font-semibold mb-3">Threat Summary</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-gray-400">Type</p>
                <p className="text-white font-medium">{threat.threat_type}</p>
              </div>
              <div>
                <p className="text-gray-400">Source IP</p>
                <p className="text-white font-mono">{threat.source_ip}</p>
              </div>
              <div>
                <p className="text-gray-400">Confidence</p>
                <p className="text-white font-medium">{(threat.confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-gray-400">Detected</p>
                <p className="text-white">{new Date(threat.detected_at).toLocaleString()}</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                Action Taken <span className="text-red-400">*</span>
              </label>
              <select
                value={actionTaken}
                onChange={(e) => setActionTaken(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              >
                <option value="">Select action...</option>
                <option value="blocked_ip">Blocked Source IP</option>
                <option value="isolated_system">Isolated Affected System</option>
                <option value="updated_firewall">Updated Firewall Rules</option>
                <option value="reset_credentials">Reset Compromised Credentials</option>
                <option value="patched_vulnerability">Patched Vulnerability</option>
                <option value="escalated_to_soc">Escalated to SOC Team</option>
                <option value="false_positive">Marked as False Positive</option>
                <option value="monitoring">Enhanced Monitoring</option>
                <option value="other">Other (specify in notes)</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                Severity Re-assessment
              </label>
              <select
                value={severityAssessment}
                onChange={(e) => setSeverityAssessment(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                Response Notes <span className="text-red-400">*</span>
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                placeholder="Describe the actions taken, findings, and any follow-up required..."
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-2 rounded-lg font-medium transition-colors"
              >
                {loading ? "Recording Response..." : "Record Response"}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}