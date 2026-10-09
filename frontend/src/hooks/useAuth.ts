// LOCATION: frontend/src/hooks/useAuth.ts
import { useState, useEffect } from 'react';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'analyst';
}

function readUser(): User | null {
  try {
    const raw = localStorage.getItem('user');
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

// NOTE: the role stored here only controls what the UI SHOWS. The backend enforces
// permissions on every request, so editing localStorage grants nothing.
export function useAuth() {
  // Read synchronously so admin routes exist on the very first render (no blank page on refresh)
  const [user, setUser] = useState<User | null>(readUser);

  useEffect(() => {
    const onStorage = () => setUser(readUser()); // login/logout in another tab
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  return { user, isAdmin: user?.role === 'admin', isAnalyst: user?.role === 'analyst' };
}