import React, { useEffect, useState } from 'react';
import api from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

export default function UserManagement() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    console.log("🚀 UserManagement component mounted!");
    const fetchUsers = async () => {
      try {
        console.log("📡 Fetching /auth/management/...");
        const res = await api.get('/auth/management/');
        console.log("✅ API Response:", res.data);
        
        // 🔧 FIX: Extract the 'results' array from the paginated response
        const userList = res.data.results || res.data;
        setUsers(Array.isArray(userList) ? userList : []);
        
      } catch (err: any) {
        console.error("❌ API Error:", err);
        setErrorMsg(err.response?.data?.detail || err.message || "Unknown error");
        toast.error("Failed to load users");
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-white">
        <h1 className="text-2xl font-bold mb-4">User Management</h1>
        <p className="text-gray-400">⏳ Loading users...</p>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-red-400 mb-4">Error Loading Users</h1>
        <p className="text-gray-300 bg-red-950 p-4 rounded border border-red-800">{errorMsg}</p>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <Toaster position="top-right" />
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">User Management</h1>
          <p className="text-gray-400 text-sm mt-1">{users.length} users found</p>
        </div>
      </div>
      
      {users.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
          <p className="text-gray-400">No users found in the database.</p>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="min-w-full text-left">
            <thead className="bg-gray-800 text-gray-400 text-sm uppercase">
              <tr>
                <th className="px-6 py-3">Email</th>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Role</th>
                <th className="px-6 py-3">Joined</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 text-sm">
              {users.map((user: any) => (
                <tr key={user.id} className="hover:bg-gray-800 transition-colors">
                  <td className="px-6 py-4 text-white font-medium">{user.email}</td>
                  <td className="px-6 py-4 text-gray-400">{user.full_name || '—'}</td>
                  <td className="px-6 py-4">
                    <select
                      value={user.role}
                      onChange={async (e) => {
                        try {
                          await api.patch(`/auth/management/${user.id}/`, { role: e.target.value });
                          toast.success("Role updated successfully");
                          // Refresh list to show updated role
                          const res = await api.get('/auth/management/');
                          setUsers(res.data.results || res.data);
                        } catch (err: any) {
                          toast.error("Failed to update role");
                        }
                      }}
                      className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="analyst">🔍 Analyst</option>
                      <option value="admin">👑 Admin</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 text-gray-400">
                    {new Date(user.date_joined).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={async () => {
                        if (!window.confirm(`Are you sure you want to delete ${user.email}?`)) return;
                        try {
                          await api.delete(`/auth/management/${user.id}/`);
                          toast.success("User deleted successfully");
                          setUsers(users.filter((u: any) => u.id !== user.id));
                        } catch (err: any) {
                          toast.error(err.response?.data?.error || "Failed to delete user");
                        }
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded text-xs font-medium transition-colors"
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}