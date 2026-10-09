// LOCATION: frontend/src/pages/Register.tsx
import React, { useState } from 'react';
<<<<<<< Updated upstream
import { Link } from 'react-router-dom';
import { authService } from '../services/api'; // 👈 CHANGED: authService instead of userService
import toast, { Toaster } from 'react-hot-toast';

export default function Register() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
=======
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    role: 'analyst',
    password: '',
    password_confirm: ''
  });
>>>>>>> Stashed changes
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
<<<<<<< Updated upstream
      // 👈 CHANGED: Use authService.register
      const response = await authService.register({
        email,
        full_name: fullName,
        password,
        password_confirm: passwordConfirm 
      });
=======
      const res = await authService.register(formData);
>>>>>>> Stashed changes
      
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      
      toast.success('Account created successfully!');
      window.location.href = '/';
    } catch (error: any) {
      const errors = error.response?.data;
      if (errors) {
        const firstError = Object.values(errors).flat()[0];
        toast.error(firstError as string);
      } else {
        toast.error('Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 p-4">
      <Toaster position="top-right" />
      <div className="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-gray-700">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Create Account</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 text-sm mb-2">Full Name</label>
            <input 
              name="full_name" 
              value={formData.full_name} 
              onChange={handleChange} 
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" 
              required 
            />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Email Address</label>
            <input 
              name="email" 
              type="email" 
              value={formData.email} 
              onChange={handleChange} 
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" 
              required 
            />
          </div>
          <div>
<<<<<<< Updated upstream
            <label className="block text-gray-300 text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••"
              required
              minLength={8}
=======
            <label className="block text-gray-300 text-sm mb-2">Role</label>
            <select 
              name="role" 
              value={formData.role} 
              onChange={handleChange} 
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
            >
              <option value="analyst">Security Analyst</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Password</label>
            <input 
              name="password" 
              type="password" 
              value={formData.password} 
              onChange={handleChange} 
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" 
              required 
              minLength={8} 
>>>>>>> Stashed changes
            />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">Confirm Password</label>
            <input 
              name="password_confirm" 
              type="password" 
              value={formData.password_confirm} 
              onChange={handleChange} 
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" 
              required 
              minLength={8} 
            />
          </div>
          <button 
            type="submit" 
            disabled={loading} 
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>
        <p className="text-gray-400 text-sm mt-4 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:underline">Login here</Link>
        </p>
      </div>
    </div>
  );
}