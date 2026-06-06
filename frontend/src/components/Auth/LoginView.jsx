import React, { useState } from 'react';
import { authService } from '../../services/authService';

const LoginView = ({ isActive, navigateTo, onLogin }) => {
  const [cedula, setCedula] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Formato automático de cédula
  const handleCedulaChange = (e) => {
    let val = e.target.value.replace(/[^0-9VvEe\-]/g, '');
    let prefix = 'V-';
    if (val.toUpperCase().startsWith('E')) {
      prefix = 'E-';
    }
    const digits = val.replace(/[^0-9]/g, '');
    if (digits.length > 0) {
      setCedula(prefix + digits);
    } else {
      setCedula(val.toUpperCase() === 'E' ? 'E-' : '');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (!cedula || !password) {
      setErrorMsg('Por favor complete todos los campos');
      return;
    }

    setIsLoading(true);
    try {
      const response = await authService.login(cedula, password);
      console.log("Login exitoso:", response);
      if (onLogin) onLogin(response.access_token);
    } catch (error) {
      setErrorMsg(error.message || 'Credenciales inválidas');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`view ${isActive ? 'active' : ''}`} id="viewLogin">
      <div className="view__header view__header--column">
        <h2>Bienvenido al Sistema de Detección de Uniforme</h2>
        <p>Ingrese las credenciales necesarias para continuar.</p>
      </div>

      <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%' }}>
        <div className="form-group">
          <label className="form-label">CÉDULA / USUARIO</label>
          <div className="input-wrap">
            <i className="fa fa-user input-icon"></i>
            <input 
              type="text" 
              className={`input ${errorMsg ? 'error' : ''}`} 
              placeholder="Ej: V-12345678" 
              value={cedula}
              onChange={handleCedulaChange}
              onFocus={() => { if(!cedula) setCedula('V-') }}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">CONTRASEÑA</label>
          <div className="input-wrap">
            <i className="fa fa-lock input-icon"></i>
            <input 
              type={showPassword ? "text" : "password"} 
              className={`input ${errorMsg ? 'error' : ''}`} 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button 
              className="toggle-pass" 
              type="button" 
              onClick={() => setShowPassword(!showPassword)}
            >
              <i className={`fa ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
            </button>
          </div>
        </div>

        {errorMsg && <span className="field-error" style={{ display: 'block', marginTop: '-5px' }}>{errorMsg}</span>}

        <div className="form-row">
          <label className="checkbox-wrap">
            <input 
              type="checkbox" 
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            />
            <span className="checkbox-custom"></span>
            Recordar sesión
          </label>
          <button type="button" className="link-btn" onClick={() => navigateTo('forgot')}>
            ¿Olvidó su contraseña?
          </button>
        </div>

        <button className="btn-primary" type="submit" disabled={isLoading}>
          <span className={`btn-text ${isLoading ? 'hidden' : ''}`}>INICIAR SESIÓN</span>
          <span className={`btn-loader ${isLoading ? '' : 'hidden'}`}><i className="fa fa-spinner fa-spin"></i></span>
        </button>
      </form>

      <p className="form-footer">
        ¿No tiene cuenta?{' '}
        <button className="link-btn link-btn--accent" onClick={() => navigateTo('register')}>Crear cuenta</button>
      </p>

      <p className="support-line">
        ¿Problemas para ingresar?{' '}
        <a href="https://mail.google.com/mail/?view=cm&to=soporte@unefa.edu.ve&su=Soporte%20Técnico&body=Buen%20día,%20necesito%20ayuda%20para%20ingresar%20al%20sistema." target="_blank" rel="noopener noreferrer" className="link-underline">Contacte a Soporte Técnico</a>
      </p>
    </div>
  );
};

export default LoginView;
