import React, { useState } from 'react';
import { authService } from '../../services/authService';

const ForgotView = ({ isActive, navigateTo }) => {
  const [step, setStep] = useState(1);
  const [cedula, setCedula] = useState('');
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState(['', '', '']);
  const [nuevaClave, setNuevaClave] = useState('');
  const [confirmarClave, setConfirmarClave] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCedulaChange = (e) => {
    let val = e.target.value.replace(/[^0-9VvEe\-]/g, '');
    const digits = val.replace(/[^0-9]/g, '');
    if (digits.length > 0) {
      setCedula('V-' + digits);
    } else {
      setCedula('');
    }
  };

  const handleBuscarPreguntas = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (!cedula) {
      setErrorMsg('Ingrese su cédula.');
      return;
    }

    setIsLoading(true);
    try {
      const data = await authService.getPreguntas(cedula.replace('V-', ''));
      setPreguntas(data.preguntas);
      setStep(2);
    } catch (error) {
      setErrorMsg(error.message || 'Usuario no encontrado');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecuperar = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (respuestas.some(r => r.trim() === '')) {
      setErrorMsg('Debe responder todas las preguntas.');
      return;
    }
    if (nuevaClave !== confirmarClave) {
      setErrorMsg('Las contraseñas no coinciden.');
      return;
    }
    if (nuevaClave.length < 6) {
      setErrorMsg('La contraseña debe tener al menos 6 caracteres.');
      return;
    }

    setIsLoading(true);
    try {
      await authService.recuperarClave(cedula.replace('V-', ''), respuestas, nuevaClave);
      alert('Contraseña actualizada correctamente. Ya puede iniciar sesión.');
      handleBackToLogin();
    } catch (error) {
      setErrorMsg(error.message || 'Error al recuperar contraseña. Verifique sus respuestas.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRespuestaChange = (index, value) => {
    const nuevas = [...respuestas];
    nuevas[index] = value;
    setRespuestas(nuevas);
  };

  const handleBackToLogin = () => {
    setStep(1);
    setCedula('');
    setPreguntas([]);
    setRespuestas(['', '', '']);
    setNuevaClave('');
    setConfirmarClave('');
    setErrorMsg('');
    navigateTo('login');
  };

  return (
    <div className={`view ${isActive ? 'active' : ''}`} id="viewForgot">
      <div className="view__header">
        <button className="back-btn" type="button" onClick={handleBackToLogin}>
          <i className="fa fa-arrow-left"></i>
        </button>
        <div>
          <h2>Recuperar Contraseña</h2>
          <p>Responda sus preguntas de seguridad para continuar.</p>
        </div>
      </div>

      {step === 1 ? (
        <form onSubmit={handleBuscarPreguntas} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="form-group">
            <label className="form-label">CÉDULA REGISTRADA</label>
            <div className="input-wrap">
              <i className="fa fa-id-card input-icon"></i>
              <input 
                type="text" 
                className={`input ${errorMsg ? 'error' : ''}`} 
                placeholder="Ej: V-12345678" 
                value={cedula}
                onChange={handleCedulaChange}
                onFocus={() => { if(!cedula) setCedula('V-') }}
              />
            </div>
            {errorMsg && <span className="field-error">{errorMsg}</span>}
          </div>

          <div className="info-box info-box--sm">
            <i className="fa fa-shield-halved"></i>
            <p>Se le pedirán las <strong>3 preguntas de seguridad</strong> que configuró al crear su cuenta.</p>
          </div>

          <button className="btn-primary" type="submit" disabled={isLoading}>
            <span className={`btn-text ${isLoading ? 'hidden' : ''}`}><i className="fa fa-magnifying-glass" style={{marginRight: '8px'}}></i>BUSCAR USUARIO</span>
            <span className={`btn-loader ${isLoading ? '' : 'hidden'}`}><i className="fa fa-spinner fa-spin"></i></span>
          </button>
        </form>
      ) : (
        <form onSubmit={handleRecuperar} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="info-box info-box--sm" style={{ marginBottom: '5px' }}>
            <p>Responda correctamente para validar su identidad.</p>
          </div>

          {errorMsg && <span className="field-error">{errorMsg}</span>}

          {preguntas.map((pregunta, index) => (
            <div className="form-group" key={index}>
              <label className="form-label">{pregunta.toUpperCase()}</label>
              <div className="input-wrap">
                <i className="fa fa-question-circle input-icon"></i>
                <input 
                  type="text" 
                  className="input" 
                  placeholder="Su respuesta secreta" 
                  value={respuestas[index]}
                  onChange={(e) => handleRespuestaChange(index, e.target.value)}
                  required
                />
              </div>
            </div>
          ))}

          <div className="form-group" style={{ marginTop: '10px' }}>
            <label className="form-label">NUEVA CONTRASEÑA</label>
            <div className="input-wrap">
              <i className="fa fa-lock input-icon"></i>
              <input 
                type={showPassword ? "text" : "password"} 
                className="input" 
                placeholder="••••••••" 
                value={nuevaClave}
                onChange={(e) => setNuevaClave(e.target.value)}
                required
              />
              <button className="toggle-pass" type="button" onClick={() => setShowPassword(!showPassword)}>
                <i className={`fa ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">CONFIRMAR NUEVA CONTRASEÑA</label>
            <div className="input-wrap">
              <i className="fa fa-lock input-icon"></i>
              <input 
                type={showPassword ? "text" : "password"} 
                className="input" 
                placeholder="••••••••" 
                value={confirmarClave}
                onChange={(e) => setConfirmarClave(e.target.value)}
                required
              />
            </div>
          </div>

          <button className="btn-primary" type="submit" disabled={isLoading} style={{ marginTop: '10px' }}>
            <span className={`btn-text ${isLoading ? 'hidden' : ''}`}><i className="fa fa-check-circle" style={{marginRight: '8px'}}></i>RESTABLECER CONTRASEÑA</span>
            <span className={`btn-loader ${isLoading ? '' : 'hidden'}`}><i className="fa fa-spinner fa-spin"></i></span>
          </button>
        </form>
      )}

      {step === 1 && (
        <p className="support-line" id="forgotSupport">
          ¿Problemas para ingresar?{' '}
          <a href="https://mail.google.com/mail/?view=cm&to=soporte@unefa.edu.ve&su=Soporte%20Técnico" target="_blank" rel="noopener noreferrer" className="link-underline">Contacte a Soporte Técnico</a>
        </p>
      )}
    </div>
  );
};

export default ForgotView;
