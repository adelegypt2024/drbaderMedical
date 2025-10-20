'use client';

import { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';

export type UserRole = 'admin' | 'consultant' | 'client';

export interface AuthUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  emailVerified: boolean;
}

export interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const storedToken = typeof window !== 'undefined' ? window.localStorage.getItem('token') : null;
    if (storedToken) {
      setToken(storedToken);
      void fetchUser(storedToken);
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const fetchUser = useCallback(async (jwt: string) => {
    try {
      const response = await axios.get<AuthUser>(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${jwt}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user', error);
      setUser(null);
      setToken(null);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem('token');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await axios.post<{ access_token: string }>(`${API_URL}/auth/login`, {
      email,
      password
    });
    const jwt = response.data.access_token;
    setToken(jwt);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('token', jwt);
    }
    await fetchUser(jwt);
  }, [fetchUser]);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('token');
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!token) return;
    await fetchUser(token);
  }, [fetchUser, token]);

  const value = useMemo(
    () => ({ user, token, loading, login, logout, refresh }),
    [user, token, loading, login, logout, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
