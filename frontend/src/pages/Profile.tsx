import React, { useEffect, useState } from 'react';
import { userService } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

interface Profile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  date_joined: string;
  last_login: string | null;
}

export default function Profile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('analyst');
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  const fetchProfile = async () => {
    try {
      const res = await userService.getProfile();
      setProfile(res.data);
      setFullName(res.data.full_name);
      setRole(res.data.role);
    } catch {
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await userService.updateProfile({ full_name: fullName, role });
      setProfile(res.data);
      setEditing(false);
      toast.success("Profile updated");
    } catch {
      toast.error("Failed to update profile");
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="text-center text-gray-500 p-8">Failed to load profile</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <Toaster position="top-right" />
      
      <div>
        <h1 className="text-2xl font-bold text-white">My Profile</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your account settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="lg:col-span-1 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold mb-4">
              {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : profile.email.charAt(0).toUpperCase()}
            </div>
            <h2 className="text-xl font-bold text-white">{profile.full_name || "No name set"}</h2>
            <p className="text-gray-400 text-sm mt-1">{profile.email}</p>
            <span className={`mt-3 text-xs px-3 py-1 rounded-full font-medium ${
              profile.role === 'admin' ? 'bg-purple-900 text-purple-300' : 'bg-blue-900 text-blue-300'
            }`}>
              {profile.role === 'admin' ? '👑 Administrator' : '🔍 Security Analyst'}
            </span>
            <div className="mt-6 w-full space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">Member since</span>
                <span className="text-white">{new Date(profile.date_joined).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-400">Last login</span>
                <span className="text-white">
                  {profile.last_login ? new Date(profile.last_login).toLocaleString() : "Never"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Edit Profile Card */}
        <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-white">Account Details</h2>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                ✏️ Edit Profile
              </button>
            )}
          </div>

          {editing ? (
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-gray-300 text-sm mb-2">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-gray-300 text-sm mb-2">Email (cannot change)</label>
                <input
                  type="email"
                  value={profile.email}
                  disabled
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-500 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-gray-300 text-sm mb-2">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="analyst">Security Analyst</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium">
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => { setEditing(false); setFullName(profile.full_name); setRole(profile.role); }}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <p className="text-gray-400 text-sm">Full Name</p>
                <p className="text-white font-medium">{profile.full_name || "Not set"}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Email</p>
                <p className="text-white font-medium">{profile.email}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Role</p>
                <p className="text-white font-medium capitalize">{profile.role}</p>
              </div>
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-gray-800">
            <h3 className="text-lg font-bold text-white mb-4">Security</h3>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium"
            >
              🔒 Change Password
            </button>
          </div>
        </div>
      </div>

      {showPasswordModal && <ChangePasswordModal onClose={() => setShowPasswordModal(false)} />}
    </div>
  );
}

function ChangePasswordModal({ onClose }: { onClose: () => void }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await userService.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: confirmPassword
      });
      toast.success("Password changed successfully. Please login again.");
      setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }, 1500);
    } catch (error: any) {
      const errors = error.response?.data;
      if (errors) {
        const firstError = Object.values(errors).flat()[0];
        toast.error(firstError as string);
      } else {
        toast.error("Failed to change password");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-white mb-4">🔒 Change Password</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 text-sm mb-2">Current Password</label>
            <input
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
              minLength={8}
            />
          </div>
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-2 rounded-lg font-medium"
            >
              {loading ? "Changing..." : "Change Password"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}