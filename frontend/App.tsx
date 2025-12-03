import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { TodoApp } from './pages/TodoApp';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

const AppRoutes: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const session = localStorage.getItem('lumina_session');
    if (session) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    localStorage.setItem('lumina_session', 'active');
    setIsAuthenticated(true);
    navigate('/app', { replace: true });
  };

  const handleLogout = () => {
    localStorage.removeItem('lumina_session');
    setIsAuthenticated(false);
    navigate('/login', { replace: true });
  };

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to="/app" replace />
          ) : (
            <Login onLogin={handleLogin} />
          )
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? (
            <Navigate to="/app" replace />
          ) : (
            <Register onLogin={handleLogin} />
          )
        }
      />
      <Route
        path="/app"
        element={
          isAuthenticated ? <TodoApp onLogout={handleLogout} /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/app' : '/login'} replace />}
      />
    </Routes>
  );
};

const App: React.FC = () => {
  return <AppRoutes />;
};

export default App;
