/* ══════════════════════════════════════════
   UNEFA — Sistema de Gestión Académica
   ui.js  |  View Transitions & UI Behaviors
   ══════════════════════════════════════════ */

'use strict';

/* ── View navigation ─────────────────── */

const VIEWS = {
  login:    $('#viewLogin'),
  register: $('#viewRegister'),
  forgot:   $('#viewForgot'),
};

let _currentView = 'login';

/**
 * navigateTo — animate between views
 */
function navigateTo(targetKey) {
  if (targetKey === _currentView) return;

  const current = VIEWS[_currentView];
  const target  = VIEWS[targetKey];

  // Direction: going "deeper" slides right→left, going "back" slides left→right
  const goingBack = targetKey === 'login';

  current.classList.remove('active');
  current.style.transform = goingBack ? 'translateX(30px)' : 'translateX(-30px)';
  current.style.opacity   = '0';

  setTimeout(() => {
    current.style.transform = '';
    current.style.opacity   = '';

    target.classList.add('active');
    _currentView = targetKey;
  }, 300);
}

/* ── Toggle password visibility ──────── */

function initPasswordToggles() {
  $$('.toggle-pass').forEach(btn => {
    btn.addEventListener('click', () => {
      const inputId = btn.dataset.target;
      const input   = $(`#${inputId}`);
      const icon    = btn.querySelector('i');

      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    });
  });
}

/* ── Password strength meter ─────────── */

function initStrengthMeter() {
  const passInput = $('#regPass');
  const fill      = $('#strengthFill');
  const label     = $('#strengthLabel');

  passInput.addEventListener('input', () => {
    if (!passInput.value) {
      fill.style.width      = '0%';
      label.textContent     = '';
      label.style.color     = '';
      return;
    }
    const result = checkPasswordStrength(passInput.value);
    fill.style.width        = result.pct;
    fill.style.background   = result.color;
    label.textContent       = result.label;
    label.style.color       = result.color;
  });
}

/* ── Forgot password tabs ─────────────── */

let _activeTab = 'cedula';

function initForgotTabs() {
  const tabs = $$('.tab', $('#viewForgot'));

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      _activeTab = tab.dataset.tab;

      const cedulaGroup = $('#tabCedula');
      const emailGroup  = $('#tabEmail');

      if (_activeTab === 'cedula') {
        cedulaGroup.classList.remove('hidden');
        emailGroup.classList.add('hidden');
        clearError($('#forgotEmail'), $('#forgotEmailErr'));
      } else {
        emailGroup.classList.remove('hidden');
        cedulaGroup.classList.add('hidden');
        clearError($('#forgotCedula'), $('#forgotCedulaErr'));
      }
    });
  });
}

/* ── Real-time inline validation ──────── */

function initInlineValidation() {
  // Login
  $('#loginCedula').addEventListener('blur', () => {
    const el = $('#loginCedula'), err = $('#loginCedulaErr');
    if (el.value.trim() && !/(^[VvEe]-?\d{6,9}$)/.test(el.value.trim()))
      setError(el, err, 'Formato inválido. Ej: V-12345678');
    else clearError(el, err);
  });

  // Register name
  $('#regNombre').addEventListener('blur', () => {
    const el = $('#regNombre'), err = $('#regNombreErr');
    if (el.value.trim().length > 0 && el.value.trim().length < 4)
      setError(el, err, 'Mínimo 4 caracteres.');
    else clearError(el, err);
  });

  // Confirm password match
  $('#regPassConfirm').addEventListener('input', () => {
    const pass    = $('#regPass').value;
    const confirm = $('#regPassConfirm');
    const err     = $('#regPassConfirmErr');
    if (confirm.value && confirm.value !== pass)
      setError(confirm, err, 'Las contraseñas no coinciden.');
    else clearError(confirm, err);
  });
}

/* ── Get active tab (for forgot) ──────── */
function getActiveTab() { return _activeTab; }
