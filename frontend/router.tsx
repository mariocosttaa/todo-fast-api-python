import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Today } from './pages/Today';
import { IndexPage } from './pages/IndexPage';
import { useAuth } from './providers/AuthProvider';
import { NEXT_PATH_KEY } from './services/api';
import { Setting } from './pages/Setting';
import { SettingsProfile } from './pages/SettingsProfile';
import { SettingsSecurity } from './pages/SettingsSecurity';
import { SettingsTimeDate } from './pages/SettingsTimeDate';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    const attemptedPath = location.pathname + location.search;
    localStorage.setItem(NEXT_PATH_KEY, attemptedPath);

    return <Navigate to={`/login?next=${encodeURIComponent(attemptedPath)}`} replace />;
  }

  return <>{children}</>;
};

export const AppRouter: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/"
        element={<IndexPage />}
      />
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />  
      <Route
        path="/today"
        element={
          <ProtectedRoute>
            <Today />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Setting />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/profile"
        element={
          <ProtectedRoute>
            <SettingsProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/security"
        element={
          <ProtectedRoute>
            <SettingsSecurity />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/time"
        element={
          <ProtectedRoute>
            <SettingsTimeDate />
          </ProtectedRoute>
        }
      />
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/dashboard' : '/'} replace />}
      />
    </Routes>
  );
};

