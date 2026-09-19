import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { userService } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

export default function Register() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('analyst');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== passwordConfirm) {
      toast.error("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const response = await userService.register({
        email,
        full_name: fullName,
        password,
        password_confirm: passwordConfirm,
        role
      });
      
      // Auto-login after registration
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      toast.success('Account created successfully!');
      navigate('/');
    } catch (error: any) {
      const errors = error.response?.data;
      if (errors) {
        const firstError = Object.values(errors).flat()[0];
        toast.error(firstError as string || 'Registration failed');
      } else {
        toast.error('Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <Toaster position="top-right" />
      
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">🛡️ AI-CTDRS</h1>
          <p className="text-gray-400 text-sm">Create your analyst account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="John Doe"
              required
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="analyst@ctdrs.com"
              required
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
            >
              <option value="analyst">Security Analyst</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••"
              required
              minLength={8}
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">Confirm Password</label>
            <input
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-medium py-3 rounded-lg transition-colors"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-400 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}