import axios from 'axios';

// 🔧 IMPORTANT: Replace this with YOUR actual Render URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ai-ctdrs.onrender.com/api';
// Point to local backend for testing
//  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add JWT token to every request
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

// Response interceptor: Handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retrying, try to refresh token
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
          // Refresh failed, logout user
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

// Auth service
export const authService = {
  login: (email: string, password: string) => {
    return api.post('/auth/login/', { email, password });
  },

  register: (data: {
    email: string;
    password: string;
    full_name: string;
    role: string;
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

// Threats service
export const threatsService = {
  getAll: (params?: any) => {
    return api.get('/threats/', { params });
  },

  getOne: (id: string) => {
    return api.get(`/threats/${id}/`);
  },

  analyze: (features: any) => {
    return api.post('/threats/analyze/', { features });
  },

  respond: (id: string, data: { action: string; notes: string }) => {
    return api.post(`/threats/${id}/respond/`, data);
  },

  resolve: (id: string) => {
    return api.patch(`/threats/${id}/resolve/`);
  },

  dismiss: (id: string) => {
    return api.delete(`/threats/${id}/dismiss/`);
  },

  exportCSV: () => {
    return api.get('/threats/export_csv/', { responseType: 'blob' });
  },
};

// Incidents service
export const incidentsService = {
  getAll: (params?: any) => {
    return api.get('/incidents/', { params });
  },

  getOne: (id: string) => {
    return api.get(`/incidents/${id}/`);
  },

  create: (data: any) => {
    return api.post('/incidents/', data);
  },

  assign: (id: string) => {
    return api.post(`/incidents/${id}/assign/`);
  },

  resolve: (id: string, data?: any) => {
    return api.post(`/incidents/${id}/resolve/`, data);
  },

  exportPDF: (id: string) => {
    return api.get(`/incidents/${id}/export_pdf/`, { responseType: 'blob' });
  },
};

// Alerts service
export const alertsService = {
  getAll: (params?: any) => {
    return api.get('/alerts/', { params });
  },

  acknowledge: (id: string) => {
    return api.post(`/alerts/${id}/acknowledge/`);
  },

  acknowledgeAll: () => {
    return api.post('/alerts/acknowledge_all/');
  },

  dismiss: (id: string) => {
    return api.delete(`/alerts/${id}/dismiss/`);
  },
};

// Analytics service
export const analyticsService = {
  getDashboard: () => {
    return api.get('/analytics/dashboard/');
  },

  getEvaluation: () => {
    return api.get('/analytics/evaluation/');
  },
};

// Settings service
export const settingsService = {
  get: () => {
    return api.get('/settings/');
  },

  update: (data: any) => {
    return api.patch('/settings/', data);
  },

  getHealth: () => {
    return api.get('/settings/health/');
  },
};

// User management service (Admin only)
export const userService = {
  getAll: (params?: any) => {
    return api.get('/auth/management/', { params });
  },

  updateRole: (id: string, role: string) => {
    return api.patch(`/auth/management/${id}/`, { role });
  },

  delete: (id: string) => {
    return api.delete(`/auth/management/${id}/`);
  },
};

export default api;
// Alias for backward compatibility
export const threatService = threatsService;