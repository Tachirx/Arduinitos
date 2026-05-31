/* ══════════════════════════════════════════
   UNEFA — Sistema de Gestión Académica
   validation.js  |  Form Validation Rules
   ══════════════════════════════════════════ */

'use strict';

/* ════════════════════════════════════════
   AUTO-FORMATO CÉDULA
   ════════════════════════════════════════ */

function formatCedula(input) {
  let val = input.value;
  val = val.replace(/[^0-9VvEe\-]/g, '');
  if (!val) { input.value = ''; return; }
  const digits = val.replace(/[^0-9]/g, '');
  input.value = digits.length > 0 ? 'V-' + digits : '';
  const len = input.value.length;
  input.setSelectionRange(len, len);
}

function initCedulaFields() {
  ['loginCedula', 'regCedula', 'forgotCedula'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input',  () => formatCedula(el));
    el.addEventListener('paste',  () => setTimeout(() => formatCedula(el), 0));
    el.addEventListener('focus',  () => {
      if (!el.value) el.value = 'V-';
      const len = el.value.length;
      setTimeout(() => el.setSelectionRange(len, len), 0);
    });
    el.addEventListener('blur', () => {
      if (el.value === 'V-' || el.value === 'V') el.value = '';
    });
  });
}

/* ════════════════════════════════════════
   BLOQUEO DE CARACTERES EN TIEMPO REAL
   Evita que el usuario escriba caracteres
   inválidos directamente en el campo.
   ════════════════════════════════════════ */

function initFieldGuards() {

  /* NOMBRE — solo letras y espacios, sin números ni especiales */
  const nombre = document.getElementById('regNombre');
  if (nombre) {
    nombre.addEventListener('keypress', e => {
      const char = e.key;
      // Permitir letras (incluyendo acentos), espacios y teclas de control
      if (!/^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]$/.test(char) && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
      }
    });
    nombre.addEventListener('input', () => {
      // Por si pegan texto: eliminar cualquier carácter no permitido
      const cleaned = nombre.value.replace(/[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]/g, '');
      if (nombre.value !== cleaned) nombre.value = cleaned;
    });
  }

  /* TELÉFONO — solo números y guión */
  const tel = document.getElementById('regTelefono');
  if (tel) {
    tel.addEventListener('keypress', e => {
      if (!/^[0-9\-]$/.test(e.key) && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
      }
    });
    tel.addEventListener('input', () => {
      const cleaned = tel.value.replace(/[^0-9\-]/g, '');
      if (tel.value !== cleaned) tel.value = cleaned;
    });
  }

  /* CORREO — mostrar error en tiempo real si no es @gmail.com */
  const correo   = document.getElementById('regCorreo');
  const correoErr = document.getElementById('regCorreoErr');
  if (correo && correoErr) {
    correo.addEventListener('blur', () => {
      const v = correo.value.trim();
      if (!v) return;
      if (!v.includes('@')) {
        setError(correo, correoErr, 'Debe incluir @ en el correo.');
      } else if (!/^[^\s@]+@gmail\.com$/i.test(v)) {
        setError(correo, correoErr, 'Solo se acepta correo @gmail.com.');
      } else {
        clearError(correo, correoErr);
      }
    });
    correo.addEventListener('input', () => {
      // Limpiar error mientras edita
      clearError(correo, correoErr);
    });
  }

  /* CONTRASEÑAS — indicar en tiempo real si es menor de 8 */
  ['regPass', 'regPassConfirm'].forEach(id => {
    const el  = document.getElementById(id);
    const err = document.getElementById(id + 'Err');
    if (!el || !err) return;
    el.addEventListener('input', () => {
      if (el.value.length > 0 && el.value.length < 8) {
        setError(el, err, 'Mínimo 8 caracteres.');
      } else {
        clearError(el, err);
      }
      // Confirmar coincidencia si es el campo de confirmación
      if (id === 'regPassConfirm') {
        const pass = document.getElementById('regPass');
        if (el.value && el.value !== pass.value) {
          setError(el, err, 'Las contraseñas no coinciden.');
        }
      }
    });
  });
}

/* ════════════════════════════════════════
   HELPERS
   ════════════════════════════════════════ */

function setError(inputEl, errEl, msg) {
  inputEl.classList.add('error');
  errEl.textContent = msg;
  return false;
}

function clearError(inputEl, errEl) {
  inputEl.classList.remove('error');
  errEl.textContent = '';
}

function clearAllErrors(viewEl) {
  viewEl.querySelectorAll('.input').forEach(i => i.classList.remove('error'));
  viewEl.querySelectorAll('.field-error').forEach(e => e.textContent = '');
}

/* ════════════════════════════════════════
   REGEX PATTERNS
   ════════════════════════════════════════ */

const RE = {
  cedula:   /^V-\d{6,9}$/,
  telefono: /^0(412|414|416|424|426)-?\d{7}$/,
  gmail:    /^[^\s@]+@gmail\.com$/i,
  nombre:   /^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]{4,80}$/,
};

/* ════════════════════════════════════════
   VALIDACIÓN LOGIN
   ════════════════════════════════════════ */

function validateLogin() {
  const cedula = $('#loginCedula');
  const pass   = $('#loginPass');
  const cErr   = $('#loginCedulaErr');
  const pErr   = $('#loginPassErr');
  let valid    = true;

  clearError(cedula, cErr);
  clearError(pass, pErr);

  if (!cedula.value.trim()) {
    setError(cedula, cErr, 'Ingrese su cédula.'); valid = false;
  } else if (!RE.cedula.test(cedula.value.trim())) {
    setError(cedula, cErr, 'Cédula inválida. Ej: V-12345678'); valid = false;
  }

  if (!pass.value) {
    setError(pass, pErr, 'Ingrese su contraseña.'); valid = false;
  } else if (pass.value.length < 8) {
    setError(pass, pErr, 'Mínimo 8 caracteres.'); valid = false;
  }

  return valid;
}

/* ════════════════════════════════════════
   VALIDACIÓN REGISTRO
   ════════════════════════════════════════ */

function validateRegister() {
  const f = {
    cedula:      { el: $('#regCedula'),      err: $('#regCedulaErr') },
    nombre:      { el: $('#regNombre'),      err: $('#regNombreErr') },
    telefono:    { el: $('#regTelefono'),    err: $('#regTelefonoErr') },
    correo:      { el: $('#regCorreo'),      err: $('#regCorreoErr') },
    pass:        { el: $('#regPass'),        err: $('#regPassErr') },
    passConfirm: { el: $('#regPassConfirm'), err: $('#regPassConfirmErr') },
  };

  let valid = true;
  Object.values(f).forEach(({ el, err }) => clearError(el, err));

  // Cédula
  if (!f.cedula.el.value.trim()) {
    setError(f.cedula.el, f.cedula.err, 'Ingrese su cédula.'); valid = false;
  } else if (!RE.cedula.test(f.cedula.el.value.trim())) {
    setError(f.cedula.el, f.cedula.err, 'Cédula inválida. Ej: V-12345678'); valid = false;
  }

  // Nombre — solo letras
  if (!f.nombre.el.value.trim()) {
    setError(f.nombre.el, f.nombre.err, 'Ingrese sus nombres y apellidos.'); valid = false;
  } else if (!RE.nombre.test(f.nombre.el.value.trim())) {
    setError(f.nombre.el, f.nombre.err, 'Solo letras y espacios, mínimo 4 caracteres.'); valid = false;
  }

  // Teléfono — solo números venezolanos
  if (!f.telefono.el.value.trim()) {
    setError(f.telefono.el, f.telefono.err, 'Ingrese su número de teléfono.'); valid = false;
  } else if (!RE.telefono.test(f.telefono.el.value.trim())) {
    setError(f.telefono.el, f.telefono.err, 'Número inválido. Ej: 0412-1234567'); valid = false;
  }

  // Correo — obligatorio @gmail.com
  if (!f.correo.el.value.trim()) {
    setError(f.correo.el, f.correo.err, 'Ingrese su correo electrónico.'); valid = false;
  } else if (!RE.gmail.test(f.correo.el.value.trim())) {
    setError(f.correo.el, f.correo.err, 'Solo se acepta correo @gmail.com.'); valid = false;
  }

  // Contraseña — mínimo 8 caracteres
  if (!f.pass.el.value) {
    setError(f.pass.el, f.pass.err, 'Ingrese una contraseña.'); valid = false;
  } else if (f.pass.el.value.length < 8) {
    setError(f.pass.el, f.pass.err, 'Mínimo 8 caracteres.'); valid = false;
  }

  // Confirmar contraseña
  if (!f.passConfirm.el.value) {
    setError(f.passConfirm.el, f.passConfirm.err, 'Confirme su contraseña.'); valid = false;
  } else if (f.passConfirm.el.value.length < 8) {
    setError(f.passConfirm.el, f.passConfirm.err, 'Mínimo 8 caracteres.'); valid = false;
  } else if (f.pass.el.value !== f.passConfirm.el.value) {
    setError(f.passConfirm.el, f.passConfirm.err, 'Las contraseñas no coinciden.'); valid = false;
  }

  return valid;
}

/* ════════════════════════════════════════
   MEDIDOR DE FORTALEZA DE CONTRASEÑA
   ════════════════════════════════════════ */

function checkPasswordStrength(pass) {
  let score = 0;
  if (pass.length >= 8)              score++;
  if (pass.length >= 12)             score++;
  if (/[A-Z]/.test(pass))            score++;
  if (/[0-9]/.test(pass))            score++;
  if (/[^A-Za-z0-9]/.test(pass))    score++;

  const levels = [
    { label: 'MUY DÉBIL',  color: '#e05c5c', pct: '15%'  },
    { label: 'DÉBIL',      color: '#e07d4a', pct: '30%'  },
    { label: 'REGULAR',    color: '#f0a500', pct: '55%'  },
    { label: 'FUERTE',     color: '#6abf69', pct: '78%'  },
    { label: 'MUY FUERTE', color: '#4caf7d', pct: '100%' },
  ];

  return levels[Math.min(score, 4)];
}
