import { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'analyst';
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const loadUser = () => {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const parsed = JSON.parse(userData);
          setUser(parsed);
        } catch {
          setUser(null);
        }
      }
    };

    loadUser();

    // Listen for storage changes (in case login happens in another tab)
    window.addEventListener('storage', loadUser);
    
    // Also check every time the component mounts
    const interval = setInterval(loadUser, 1000);

    return () => {
      window.removeEventListener('storage', loadUser);
      clearInterval(interval);
    };
  }, []);

  const isAdmin = user?.role === 'admin';
  const isAnalyst = user?.role === 'analyst';

  return { user, isAdmin, isAnalyst };
}