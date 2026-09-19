import axios from 'axios';
import type { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (email: string, password: string) => api.post('/auth/login/', { email, password }),
};

export const threatService = {
  list: (params?: object) => api.get('/threats/', { params }),
  analyze: (data: object) => api.post('/threats/analyze/', data),
  respond: (id: string, data: object) => api.post(`/threats/${id}/respond/`, data),
  dismiss: (id: string) => api.delete(`/threats/${id}/dismiss/`),
  get: (id: string) => api.get(`/threats/${id}/`),
};

export const analyticsService = {
  dashboard: () => api.get('/analytics/dashboard/'),
  evaluation: () => api.get('/analytics/evaluation/'),
};

export const userService = {
  register: (data: { email: string; full_name: string; password: string; password_confirm: string; role: string }) => 
    api.post('/auth/register/', data),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data: object) => api.patch('/auth/profile/', data),
  changePassword: (data: { old_password: string; new_password: string; new_password_confirm: string }) => 
    api.post('/auth/profile/change-password/', data),
};

export default api;