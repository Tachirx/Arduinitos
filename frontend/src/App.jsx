import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthContainer from './components/Auth/AuthContainer';
import DashboardView from './components/Dashboard/DashboardView';

// Valida que el token exista y no haya expirado
function isTokenValid(token) {
  if (!token) return false;
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    // payload.exp está en segundos; Date.now() en milisegundos
    return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now();
  } catch {
    return false; // token malformado o basura
  }
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!isTokenValid(token)) {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setCargando(false);
        return;
      }

      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/usuarios/perfil`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (res.ok) {
          setIsAuthenticated(true);
        } else {
          // Token rechazado por el backend (usuario no existe o bloqueado)
          localStorage.removeItem('token');
          setIsAuthenticated(false);
        }
      } catch (err) {
        // Permitir entrada si el backend está inalcanzable pero el token es localmente válido
        setIsAuthenticated(true);
      } finally {
        setCargando(false);
      }
    };
    checkAuth();
  }, []);

  const handleLogin = (token) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (cargando) return null;

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={!isAuthenticated ? <AuthContainer onLogin={handleLogin} /> : <Navigate to="/dashboard" replace />}
        />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <DashboardView onLogout={handleLogout} /> : <Navigate to="/login" replace />}
        />
        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </Router>
  );
}

export default App;
