import React, { useEffect, useState } from "react";
import api from "../services/api";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { useThreatWebSocket } from "../hooks/useThreatWebSocket";
import { useAuth } from "../hooks/useAuth";
import ConfirmModal from "../components/ConfirmModal";

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  assigned_to: string | null;
  assigned_to_email: string | null;
  created_at: string;
  resolved_at: string | null;
  notes: Array<{ id: string; author: string; content: string; created_at: string }>;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-400 bg-red-950",
  high: "text-orange-400 bg-orange-950",
  medium: "text-yellow-400 bg-yellow-950",
  low: "text-green-400 bg-green-950",
};

const STATUS_COLORS: Record<string, string> = {
  open: "bg-red-900 text-red-300",
  in_progress: "bg-yellow-900 text-yellow-300",
  resolved: "bg-green-900 text-green-300",
  closed: "bg-gray-700 text-gray-300",
};

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [newNote, setNewNote] = useState("");
  const [incidentToDelete, setIncidentToDelete] = useState<Incident | null>(null);
  const navigate = useNavigate();
  
  const { latestThreat } = useThreatWebSocket();
  const { isAdmin } = useAuth();

  const fetchIncidents = async () => {
    try {
      const res = await api.get('/incidents/');
      setIncidents(res.data.results || res.data);
    } catch (error) {
      console.error("Failed to load incidents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (latestThreat) {
      console.log("🔄 New threat detected, refreshing incidents...");
      fetchIncidents();
    }
  }, [latestThreat]);

  useEffect(() => {
    fetchIncidents();
  }, []);

  const handleAssign = async (incidentId: string) => {
    try {
      await api.post(`/incidents/${incidentId}/assign/`);
      toast.success("Incident assigned to you");
      fetchIncidents();
    } catch {
      toast.error("Failed to assign incident");
    }
  };

  const handleDismiss = async (incident: Incident) => {
    setIncidentToDelete(incident);
  };

  const confirmDismiss = async () => {
    if (!incidentToDelete) return;
    
    try {
      await api.delete(`/incidents/${incidentToDelete.id}/dismiss/`);
      toast.success("Incident removed");
      setIncidents(incidents.filter((i) => i.id !== incidentToDelete.id));
      if (selectedIncident?.id === incidentToDelete.id) setSelectedIncident(null);
      setIncidentToDelete(null);
    } catch {
      toast.error("Failed to remove incident");
    }
  };

  const cancelDismiss = () => {
    setIncidentToDelete(null);
  };

  const handleAddNote = async (incidentId: string) => {
    if (!newNote.trim()) return;
    try {
      await api.post(`/incidents/${incidentId}/add_note/`, { content: newNote });
      toast.success("Note added");
      setNewNote("");
      fetchIncidents();
      if (selectedIncident?.id === incidentId) {
        const res = await api.get(`/incidents/${incidentId}/`);
        setSelectedIncident(res.data);
      }
    } catch {
      toast.error("Failed to add note");
    }
  };

  const handleResolve = async (incidentId: string) => {
    try {
      await api.post(`/incidents/${incidentId}/resolve/`);
      toast.success("Incident resolved");
      fetchIncidents();
      setSelectedIncident(null);
    } catch {
      toast.error("Failed to resolve incident");
    }
  };

  const handleViewThreat = () => {
    const match = selectedIncident?.description.match(/Source IP: ([\d.]+)/);
    if (match) {
      navigate('/threats', { state: { searchIP: match[1] } });
      setSelectedIncident(null);
    } else {
      toast.error("Could not find linked threat");
    }
  };

  const handleExportPDF = async () => {
    try {
      toast.loading("Generating PDF report...", { id: 'export' });
      const response = await api.get('/incidents/export_pdf/', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `incident_report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("PDF report downloaded successfully", { id: 'export' });
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("Failed to export PDF", { id: 'export' });
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading incidents...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Incident Management</h1>
          <p className="text-gray-400 text-sm mt-1">Track and resolve security incidents ({incidents.length} total)</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExportPDF}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            📄 Export PDF Report
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            + Create Incident
          </button>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Title</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Severity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Assigned To</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Created</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-gray-900 divide-y divide-gray-800">
            {incidents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  <p className="text-4xl mb-3">📋</p>
                  <p>No incidents yet. Submit a threat via Threat Analysis to auto-create incidents.</p>
                </td>
              </tr>
            ) : (
              incidents.map((incident) => (
                <tr key={incident.id} className="hover:bg-gray-800 transition-colors group">
                  <td className="px-6 py-4 text-sm text-white font-medium">{incident.title}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${SEVERITY_COLORS[incident.severity]}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[incident.status]}`}>
                      {incident.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {incident.assigned_to_email || "Unassigned"}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {new Date(incident.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2 items-center">
                      <button
                        onClick={() => setSelectedIncident(incident)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium"
                      >
                        View
                      </button>
                      {incident.status === "open" && (
                        <button
                          onClick={() => handleAssign(incident.id)}
                          className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded text-xs font-medium"
                        >
                          Assign to Me
                        </button>
                      )}
                      {isAdmin && (
                        <button
                          onClick={() => handleDismiss(incident)}
                          title="Remove incident"
                          className="opacity-0 group-hover:opacity-100 bg-red-600 hover:bg-red-700 text-white w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold transition-all"
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

      {selectedIncident && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-white">{selectedIncident.title}</h2>
                <button onClick={() => setSelectedIncident(null)} className="text-gray-400 hover:text-white text-2xl">×</button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-gray-400 text-sm">Severity</p><span className={`text-xs px-2 py-1 rounded-full font-medium ${SEVERITY_COLORS[selectedIncident.severity]}`}>{selectedIncident.severity}</span></div>
                  <div><p className="text-gray-400 text-sm">Status</p><span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[selectedIncident.status]}`}>{selectedIncident.status.replace('_', ' ')}</span></div>
                  <div><p className="text-gray-400 text-sm">Assigned To</p><p className="text-white">{selectedIncident.assigned_to_email || "Unassigned"}</p></div>
                  <div><p className="text-gray-400 text-sm">Created</p><p className="text-white">{new Date(selectedIncident.created_at).toLocaleString()}</p></div>
                </div>

                <div>
                  <p className="text-gray-400 text-sm mb-2">Description</p>
                  <p className="text-white bg-gray-800 p-3 rounded whitespace-pre-wrap">{selectedIncident.description}</p>
                </div>

                {selectedIncident.description.includes('Automated incident created from AI threat detection') && (
                  <div className="bg-blue-950/30 border border-blue-800 rounded-lg p-3">
                    <p className="text-blue-300 text-sm font-medium mb-2">🔗 Linked Threat</p>
                    <p className="text-gray-300 text-xs mb-2">This incident was automatically created from an AI-detected threat.</p>
                    <button onClick={handleViewThreat} className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium">
                      🔍 View Threat in Threats Page
                    </button>
                  </div>
                )}

                <div>
                  <p className="text-gray-400 text-sm mb-2">Notes ({selectedIncident.notes.length})</p>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {selectedIncident.notes.length === 0 ? (
                      <p className="text-gray-500 text-sm">No notes yet.</p>
                    ) : (
                      selectedIncident.notes.map((note) => (
                        <div key={note.id} className="bg-gray-800 p-3 rounded">
                          <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>{note.author}</span>
                            <span>{new Date(note.created_at).toLocaleString()}</span>
                          </div>
                          <p className="text-white text-sm">{note.content}</p>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="mt-3 flex gap-2">
                    <input
                      type="text"
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      placeholder="Add a note..."
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={() => handleAddNote(selectedIncident.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                {selectedIncident.status !== "resolved" && selectedIncident.status !== "closed" && (
                  <button onClick={() => handleResolve(selectedIncident.id)} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-medium">
                    Mark as Resolved
                  </button>
                )}
                <button onClick={() => setSelectedIncident(null)} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded font-medium">
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={!!incidentToDelete}
        title="Remove Incident"
        message={`Are you sure you want to remove "${incidentToDelete?.title}"? This action cannot be undone.`}
        confirmText="Remove"
        cancelText="Cancel"
        onConfirm={confirmDismiss}
        onCancel={cancelDismiss}
      />

      {showCreateModal && <CreateIncidentModal onClose={() => setShowCreateModal(false)} onCreated={fetchIncidents} />}
    </div>
  );
}

function CreateIncidentModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/incidents/', { title, description, severity });
      toast.success("Incident created");
      onCreated();
      onClose();
    } catch {
      toast.error("Failed to create incident");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-white mb-4">Create New Incident</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 text-sm mb-2">Title</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500" required />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500" required />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Severity</label>
            <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="submit" disabled={loading} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-2 rounded-lg font-medium">{loading ? "Creating..." : "Create"}</button>
            <button type="button" onClick={onClose} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg font-medium">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}