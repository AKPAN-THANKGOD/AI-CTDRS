import axios from 'axios';

// 🔧 CRITICAL: Ensure this matches your ACTUAL live Render URL.
// Your logs showed the new URL is: https://ai-ctdrs-lo9k.onrender.com
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ai-ctdrs.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  login: (email: string, password: string) => {
    return api.post('/auth/login/', { email, password });
  },

  register: (data: {
    email: string;
    password: string;
    full_name: string;
    role: string;
    password_confirm: string;
  }) => {
    return api.post('/auth/register/', data);
  },

  getProfile: () => {
    return api.get('/auth/profile/');
  },

  updateProfile: (data: any) => {
    return api.patch('/auth/profile/', data);
  },

  changePassword: (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    return api.post('/auth/profile/change-password/', data);
  },
};

export const threatsService = {
  getAll: (params?: any) => api.get('/threats/', { params }),
  getOne: (id: string) => api.get(`/threats/${id}/`),
  analyze: (data: any) => api.post('/threats/analyze/', data),
  respond: (id: string, data: { action: string; notes: string }) => api.post(`/threats/${id}/respond/`, data),
  resolve: (id: string) => api.patch(`/threats/${id}/resolve/`),
  dismiss: (id: string) => api.delete(`/threats/${id}/dismiss/`),
  exportCSV: () => api.get('/threats/export_csv/', { responseType: 'blob' }),
};

export const incidentsService = {
  getAll: (params?: any) => api.get('/incidents/', { params }),
  getOne: (id: string) => api.get(`/incidents/${id}/`),
  create: (data: any) => api.post('/incidents/', data),
  assign: (id: string) => api.post(`/incidents/${id}/assign/`),
  resolve: (id: string, data?: any) => api.post(`/incidents/${id}/resolve/`, data),
  exportPDF: (id: string) => api.get(`/incidents/${id}/export_pdf/`, { responseType: 'blob' }),
};

export const alertsService = {
  getAll: (params?: any) => api.get('/alerts/', { params }),
  acknowledge: (id: string) => api.post(`/alerts/${id}/acknowledge/`),
  acknowledgeAll: () => api.post('/alerts/acknowledge_all/'),
  dismiss: (id: string) => api.delete(`/alerts/${id}/dismiss/`),
};

export const analyticsService = {
  getDashboard: () => api.get('/analytics/dashboard/'),
  getEvaluation: () => api.get('/analytics/evaluation/'),
};

export const settingsService = {
  get: () => api.get('/settings/'),
  update: (data: any) => api.patch('/settings/', data),
  getHealth: () => api.get('/settings/health/'),
};

export const userService = {
  getAll: (params?: any) => api.get('/auth/management/', { params }),
  updateRole: (id: string, role: string) => api.patch(`/auth/management/${id}/`, { role }),
  delete: (id: string) => api.delete(`/auth/management/${id}/`),
};

export default api;
export const threatService = threatsService;