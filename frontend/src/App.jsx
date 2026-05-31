import React, { useState, useEffect } from 'react';
import AuthContainer from './components/Auth/AuthContainer';
import DashboardView from './components/Dashboard/DashboardView';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (token) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <>
      {isAuthenticated ? (
        <DashboardView onLogout={handleLogout} />
      ) : (
        <AuthContainer onLogin={handleLogin} />
      )}
    </>
  );
}

export default App;
