import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Threats from './pages/Threats';
import ThreatAnalysis from './pages/ThreatAnalysis';
import Incidents from './pages/Incidents';
import Alerts from './pages/Alerts';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import UserManagement from './pages/UserManagement';
import { useThreatWebSocket } from './hooks/useThreatWebSocket';
import { useAuth } from './hooks/useAuth';
import Settings from './pages/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function GlobalThreatNotification() {
  const { latestThreat } = useThreatWebSocket();
  if (!latestThreat) return null;
  return (
    <div className="fixed top-20 right-4 z-50 bg-red-900 border-2 border-red-500 rounded-lg shadow-2xl p-4 max-w-sm animate-bounce">
      <div className="flex items-start gap-3">
        <span className="text-2xl">🚨</span>
        <div>
          <h3 className="text-white font-bold text-sm">NEW THREAT DETECTED</h3>
          <p className="text-red-200 text-xs mt-1 font-semibold">{latestThreat.threat_type}</p>
          <p className="text-gray-300 text-xs mt-1">
            IP: {latestThreat.source_ip} • Severity: <span className="uppercase font-bold">{latestThreat.severity}</span>
          </p>
        </div>
      </div>
    </div>
  );
}

function App() {
  const { user, isAdmin } = useAuth();

  console.log("🔍 Current user:", user);
  console.log("🔍 Is admin:", isAdmin);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-950 flex">
                <aside className="w-64 bg-gray-900 border-r border-gray-800 p-6 hidden md:block">
                  <h1 className="text-xl font-bold text-white mb-8">🛡️ AI-CTDRS</h1>
                  <nav className="space-y-2">
                    <Link to="/" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">📊 Dashboard</Link>
                    <Link to="/threats" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">🚨 Threats</Link>
                    <Link to="/analyze" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">🔍 Threat Analysis</Link>
                    <Link to="/incidents" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">📋 Incidents</Link>
                    <Link to="/alerts" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">🔔 Alerts</Link>
                    <Link to="/profile" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors">👤 My Profile</Link>
                    
                    {/* Admin-only link */}
                   {isAdmin && (
  <>
    <Link to="/users" className="block px-4 py-2 text-purple-300 hover:bg-gray-800 rounded-lg transition-colors font-semibold">
      👥 User Management
    </Link>
    <Link to="/settings" className="block px-4 py-2 text-purple-300 hover:bg-gray-800 rounded-lg transition-colors font-semibold">
      ⚙️ Settings
    </Link>
  </>
)}
                    
                    <button
                      onClick={() => {
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        localStorage.removeItem('user');
                        window.location.href = '/login';
                      }}
                      className="w-full text-left px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors mt-8"
                    >
                      🚪 Logout
                    </button>
                  </nav>
                  
                  {/* Show current user info */}
                  {user && (
                    <div className="mt-6 pt-6 border-t border-gray-800">
                      <p className="text-xs text-gray-500">Logged in as:</p>
                      <p className="text-sm text-white font-medium truncate">{user.full_name || user.email}</p>
                      <p className={`text-xs mt-1 ${isAdmin ? 'text-purple-400' : 'text-blue-400'}`}>
                        {isAdmin ? '👑 Administrator' : '🔍 Analyst'}
                      </p>
                    </div>
                  )}
                </aside>

                <main className="flex-1 overflow-y-auto relative">
                  <GlobalThreatNotification />
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/threats" element={<Threats />} />
                    <Route path="/analyze" element={<ThreatAnalysis />} />
                    <Route path="/incidents" element={<Incidents />} />
                    <Route path="/alerts" element={<Alerts />} />
                    <Route path="/profile" element={<Profile />} />
                  {isAdmin && <Route path="/users" element={<UserManagement />} />}
{isAdmin && <Route path="/settings" element={<Settings />} />}
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;