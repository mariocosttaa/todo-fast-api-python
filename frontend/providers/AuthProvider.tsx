import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api, NEXT_PATH_KEY } from '../services/api';
import type { User } from '../types';
import { getCurrentUser } from '../services/user';

interface AuthContextValue {
  isAuthenticated: boolean;
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  login: (redirectPath?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const ACCESS_TOKEN_KEY = 'access_token';
let hasLoadedUserOnce = false;

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
  });
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const loadUser = async () => {
    try {
      const data = await getCurrentUser();
      setUser(data);
    } catch (err) {
      console.error('Failed to load current user', err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      return;
    }

    if (hasLoadedUserOnce) {
      return;
    }
    hasLoadedUserOnce = true;

    setIsAuthenticated(true);
    loadUser();
  }, []);

  const login = (redirectPath?: string) => {
    setIsAuthenticated(true);

    loadUser();

    const storedNextPath = localStorage.getItem(NEXT_PATH_KEY);
    const target = redirectPath || storedNextPath || '/dashboard';

    if (storedNextPath) {
      localStorage.removeItem(NEXT_PATH_KEY);
    }

    navigate(target, { replace: true });
  };

  const logout = async () => {

    const response = await api.delete('/auth/logout');
    if (response.status !== 200) {
      console.log(response.data);
      throw new Error('Logout failed');
    }

    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(NEXT_PATH_KEY);
    setIsAuthenticated(false);
    setUser(null);

    const currentPath = location.pathname + location.search;
    localStorage.setItem(NEXT_PATH_KEY, currentPath);

    navigate('/login', { replace: true });
  };

  const value: AuthContextValue = {
    isAuthenticated,
    user,
    setUser,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

