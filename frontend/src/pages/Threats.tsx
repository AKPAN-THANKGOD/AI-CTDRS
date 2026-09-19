import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { threatService } from "../services/api";
import api from "../services/api";
import type { Threat } from "../types";
import toast from "react-hot-toast";
import ExplainabilityPanel from "../components/ExplainabilityPanel";
import ResponseModal from "../components/ResponseModal";
import { useAuth } from "../hooks/useAuth";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-400 bg-red-950", high: "text-orange-400 bg-orange-950",
  medium: "text-yellow-400 bg-yellow-950", low: "text-green-400 bg-green-950",
};

export default function Threats() {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null);
  const [respondingThreat, setRespondingThreat] = useState<Threat | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const location = useLocation();
  const { isAdmin } = useAuth();

  const fetchThreats = async () => {
    try {
      const res = await threatService.list();
      setThreats(res.data.results || res.data);
    } catch { toast.error("Failed to load threats"); } finally { setLoading(false); }
  };

  const handleDismiss = async (threatId: string) => {
    try {
      await threatService.dismiss(threatId);
      toast.success("Threat dismissed");
      setThreats(threats.filter((t) => t.id !== threatId));
      if (selectedThreat?.id === threatId) setSelectedThreat(null);
    } catch { toast.error("Failed to dismiss"); }
  };

  const handleExportCSV = async () => {
    try {
      toast.loading("Preparing CSV export...", { id: 'export' });
      const response = await api.get('/threats/export_csv/', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `threats_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("CSV downloaded successfully", { id: 'export' });
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("Failed to export CSV", { id: 'export' });
    }
  };

  useEffect(() => {
    fetchThreats();
  }, []);

  useEffect(() => {
    const state = location.state as { viewThreatId?: string; searchIP?: string } | null;
    
    if (state?.viewThreatId && threats.length > 0) {
      const threat = threats.find((t) => t.id === state.viewThreatId);
      if (threat) {
        setSelectedThreat(threat);
        window.history.replaceState({}, document.title);
      }
    } else if (state?.searchIP) {
      setSearchTerm(state.searchIP);
      window.history.replaceState({}, document.title);
    }
  }, [location.state, threats]);

  const filteredThreats = threats.filter((threat) => {
    const matchesSearch = threat.source_ip.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         threat.threat_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === "all" || threat.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading threats...</div>;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Detection</h1>
        <p className="text-gray-400 text-sm mt-1">AI-analyzed network threats ({filteredThreats.length} total)</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800 flex gap-4 items-center">
          <input
            type="text"
            placeholder="Search by IP or Threat Type..."
            className="bg-gray-800 text-white text-sm rounded-lg px-4 py-2 border border-gray-700 focus:outline-none focus:border-blue-500 flex-1"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="bg-gray-800 text-white text-sm rounded-lg px-4 py-2 border border-gray-700 focus:outline-none focus:border-blue-500"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button
            onClick={handleExportCSV}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 whitespace-nowrap"
          >
            📥 Export CSV
          </button>
        </div>

        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Source IP</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Severity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-gray-900 divide-y divide-gray-800">
            {filteredThreats.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-500">No threats match your filters.</td></tr>
            ) : (
              filteredThreats.map((threat) => (
                <tr key={threat.id} className="hover:bg-gray-800 transition-colors">
                  <td className="px-6 py-4 text-sm text-white font-medium">{threat.threat_type}</td>
                  <td className="px-6 py-4 text-sm text-gray-400 font-mono">{threat.source_ip}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${SEVERITY_COLORS[threat.severity]}`}>
                      {threat.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">{(threat.confidence * 100).toFixed(0)}%</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      threat.status === "resolved" ? "bg-green-900 text-green-300" :
                      threat.status === "responded" ? "bg-blue-900 text-blue-300" :
                      "bg-yellow-900 text-yellow-300"
                    }`}>
                      {threat.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2 items-center">
                      <button
                        onClick={() => setSelectedThreat(threat)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium"
                      >
                        View
                      </button>
                      {threat.status === "open" && (
                        <button
                          onClick={() => setRespondingThreat(threat)}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-medium"
                        >
                          Respond
                        </button>
                      )}
                      {isAdmin && (threat.status === "responded" || threat.status === "resolved") && (
                        <button
                          onClick={() => handleDismiss(threat.id)}
                          className="bg-red-600 hover:bg-red-700 text-white w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedThreat && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-white">Threat Details</h2>
                <button onClick={() => setSelectedThreat(null)} className="text-gray-400 hover:text-white text-2xl">×</button>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-gray-400 text-sm">Threat Type</p><p className="text-white font-semibold">{selectedThreat.threat_type}</p></div>
                  <div><p className="text-gray-400 text-sm">Severity</p><span className={`text-xs px-2 py-1 rounded-full font-medium ${SEVERITY_COLORS[selectedThreat.severity]}`}>{selectedThreat.severity}</span></div>
                  <div><p className="text-gray-400 text-sm">Source IP</p><p className="text-white font-mono">{selectedThreat.source_ip}</p></div>
                  <div><p className="text-gray-400 text-sm">Destination IP</p><p className="text-white font-mono">{selectedThreat.destination_ip || "N/A"}</p></div>
                  <div><p className="text-gray-400 text-sm">Confidence</p><p className="text-white font-semibold">{(selectedThreat.confidence * 100).toFixed(2)}%</p></div>
                  <div><p className="text-gray-400 text-sm">Status</p><p className="text-white">{selectedThreat.status}</p></div>
                  <div><p className="text-gray-400 text-sm">Detected</p><p className="text-white">{new Date(selectedThreat.detected_at).toLocaleString()}</p></div>
                  {selectedThreat.responded_at && <div><p className="text-gray-400 text-sm">Responded</p><p className="text-white">{new Date(selectedThreat.responded_at).toLocaleString()}</p></div>}
                </div>
                
                {selectedThreat.notes && (
                  <div>
                    <p className="text-gray-400 text-sm mb-2">Notes & Response History</p>
                    <p className="text-white bg-gray-800 p-3 rounded text-sm whitespace-pre-wrap">{selectedThreat.notes}</p>
                  </div>
                )}

                <ExplainabilityPanel 
                  shapExplanation={selectedThreat.shap_explanation}
                  limeExplanation={selectedThreat.lime_explanation}
                />
              </div>
              <div className="mt-6 flex gap-3">
                {selectedThreat.status === "open" && (
                  <button
                    onClick={() => { setRespondingThreat(selectedThreat); setSelectedThreat(null); }}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium"
                  >
                    Respond to Threat
                  </button>
                )}
                <button onClick={() => setSelectedThreat(null)} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded font-medium">
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {respondingThreat && (
        <ResponseModal
          threat={respondingThreat}
          onClose={() => setRespondingThreat(null)}
          onResponded={fetchThreats}
        />
      )}
    </div>
  );
}