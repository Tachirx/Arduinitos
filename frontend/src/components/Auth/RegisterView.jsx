import React, { useState } from 'react';
import { authService } from '../../services/authService';

const RegisterView = ({ isActive, navigateTo }) => {
  const [formData, setFormData] = useState({
    cedula: '',
    nombres: '',
    apellidos: '', // La UI original tenia "NOMBRES Y APELLIDOS" combinado, lo separaremos acá
    telefono: '',
    correo: '',
    clave: '',
    claveConfirm: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCedulaChange = (e) => {
    // Permitir ingreso de texto libre (cédula o usuario). El backend se encargará de normalizarlo.
    setFormData(prev => ({ ...prev, cedula: e.target.value }));
  };

  const PREGUNTAS_OPCIONES = [
    "¿Color favorito?",
    "¿Nombre de tu primera mascota?",
    "¿Ciudad de nacimiento?",
    "¿Comida favorita?",
    "¿Nombre de la escuela primaria?",
    "¿Deporte favorito?"
  ];

  const [preguntas, setPreguntas] = useState([
    { pregunta: PREGUNTAS_OPCIONES[0], respuesta: '' },
    { pregunta: PREGUNTAS_OPCIONES[1], respuesta: '' },
    { pregunta: PREGUNTAS_OPCIONES[2], respuesta: '' }
  ]);

  const handlePreguntaChange = (index, field, value) => {
    const nuevas = [...preguntas];
    nuevas[index][field] = value;
    setPreguntas(nuevas);
  };

  const calculateStrength = (pass) => {
    let score = 0;
    if (pass.length >= 8) score++;
    if (pass.length >= 12) score++;
    if (/[A-Z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;
    const pct = ['0%', '20%', '40%', '60%', '80%', '100%'][score] || '0%';
    const color = ['#e05c5c', '#e05c5c', '#e07d4a', '#f0a500', '#6abf69', '#4caf7d'][score] || 'transparent';
    const label = ['', 'MUY DÉBIL', 'DÉBIL', 'REGULAR', 'FUERTE', 'MUY FUERTE'][score] || '';
    return { pct, color, label };
  };

  const strength = calculateStrength(formData.clave);

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    
    if (formData.clave !== formData.claveConfirm) {
      setErrorMsg('Las contraseñas no coinciden');
      return;
    }

    // Dividir Nombres y Apellidos de un solo input si se desea, o manejarlos
    const partesNombre = formData.nombres.trim().split(' ');
    const nombreFinal = partesNombre[0] || 'N/A';
    const apellidoFinal = partesNombre.length > 1 ? partesNombre.slice(1).join(' ') : 'N/A';

    const payload = {
      cedula: formData.cedula,
      nombres: nombreFinal,
      apellidos: apellidoFinal,
      telefono: formData.telefono,
      clave: formData.clave,
      rol: 'portero', // Por defecto según requerimientos
      preguntas: preguntas
    };

    setIsLoading(true);
    try {
      await authService.register(payload);
      alert('¡Cuenta creada exitosamente!');
      navigateTo('login');
    } catch (error) {
      setErrorMsg(error.message || 'Error al crear la cuenta');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`view ${isActive ? 'active' : ''}`} id="viewRegister">
      <div className="view__header">
        <button className="back-btn" type="button" onClick={() => navigateTo('login')}>
          <i className="fa fa-arrow-left"></i>
        </button>
        <div>
          <h2>Crear Cuenta</h2>
          <p>Complete los campos para registrarse en el sistema.</p>
        </div>
      </div>

      <form onSubmit={handleRegister} className="form-grid" style={{ width: '100%' }}>
        {errorMsg && <div className="form-group form-group--full"><span className="field-error" style={{display:'block'}}>{errorMsg}</span></div>}
        
        <div className="form-group">
          <label className="form-label">CÉDULA</label>
          <div className="input-wrap">
            <i className="fa fa-id-card input-icon"></i>
            <input type="text" className="input" name="cedula" value={formData.cedula} onChange={handleCedulaChange} placeholder="Cédula o Nombre de usuario" required />
          </div>
        </div>

        <div className="form-group form-group--full">
          <label className="form-label">NOMBRES Y APELLIDOS</label>
          <div className="input-wrap">
            <i className="fa fa-user-circle input-icon"></i>
            <input type="text" className="input" name="nombres" value={formData.nombres} onChange={handleChange} placeholder="Ej: Juan Carlos Pérez García" required />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">TELÉFONO</label>
          <div className="input-wrap">
            <i className="fa fa-phone input-icon"></i>
            <input type="tel" className="input" name="telefono" value={formData.telefono} onChange={handleChange} placeholder="Ej: 0412-1234567" />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">CORREO ELECTRÓNICO</label>
          <div className="input-wrap">
            <i className="fa fa-envelope input-icon"></i>
            <input type="email" className="input" name="correo" value={formData.correo} onChange={handleChange} placeholder="Ej: usuario@gmail.com" required />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">CONTRASEÑA</label>
          <div className="input-wrap">
            <i className="fa fa-lock input-icon"></i>
            <input type={showPassword ? "text" : "password"} className="input" name="clave" value={formData.clave} onChange={handleChange} placeholder="••••••••" required minLength={6} />
            <button className="toggle-pass" type="button" onClick={() => setShowPassword(!showPassword)}>
              <i className={`fa ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
            </button>
          </div>
          <div className="pass-strength">
            <div className="pass-strength__bar">
              <div className="pass-strength__fill" style={{ width: strength.pct, backgroundColor: strength.color }}></div>
            </div>
            <span className="pass-strength__label" style={{ color: strength.color }}>{strength.label}</span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">CONFIRMAR CONTRASEÑA</label>
          <div className="input-wrap">
            <i className="fa fa-lock input-icon"></i>
            <input type={showPasswordConfirm ? "text" : "password"} className="input" name="claveConfirm" value={formData.claveConfirm} onChange={handleChange} placeholder="••••••••" required />
            <button className="toggle-pass" type="button" onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}>
              <i className={`fa ${showPasswordConfirm ? 'fa-eye-slash' : 'fa-eye'}`}></i>
            </button>
          </div>
        </div>

        <div className="form-group form-group--full" style={{ marginTop: '5px' }}>
          <h3 style={{ fontSize: '12px', marginBottom: '10px', color: 'var(--accent-teal)', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '5px', letterSpacing: '1px' }}>PREGUNTAS DE SEGURIDAD (Obligatorias para recuperar cuenta)</h3>
          {preguntas.map((p, index) => (
            <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <select 
                className="input" 
                style={{ flex: 1, paddingLeft: '10px', color: 'black' }} 
                value={p.pregunta}
                onChange={(e) => handlePreguntaChange(index, 'pregunta', e.target.value)}
              >
                {PREGUNTAS_OPCIONES.map((opc, i) => <option key={i} value={opc}>{opc}</option>)}
              </select>
              <input 
                type="text" 
                className="input" 
                style={{ flex: 1, paddingLeft: '10px' }} 
                placeholder="Respuesta secreta" 
                value={p.respuesta}
                onChange={(e) => handlePreguntaChange(index, 'respuesta', e.target.value)}
                required
              />
            </div>
          ))}
        </div>

        <button className="btn-primary btn-primary--register" type="submit" disabled={isLoading} style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
          <span className={`btn-text ${isLoading ? 'hidden' : ''}`}>CREAR CUENTA</span>
          <span className={`btn-loader ${isLoading ? '' : 'hidden'}`}><i className="fa fa-spinner fa-spin"></i></span>
        </button>
      </form>

      <p className="form-footer">
        ¿Ya tiene cuenta?{' '}
        <button className="link-btn link-btn--accent" onClick={() => navigateTo('login')}>Iniciar sesión</button>
      </p>
    </div>
  );
};

export default RegisterView;
