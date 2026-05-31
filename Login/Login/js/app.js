/* ══════════════════════════════════════════
   UNEFA — Sistema de Gestión Académica
   app.js  |  Main Entry – Event Bindings
   ══════════════════════════════════════════ */

'use strict';

/* ════════════════════════════════════════
   INIT
   ════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  // Ambient particles
  generateParticles($('#particles'), 30);

  // UI behaviors
  initPasswordToggles();
  initStrengthMeter();
  initForgotTabs();
  initInlineValidation();
  initCedulaFields();
  initFieldGuards();

  // Event bindings
  bindLogin();
  bindRegister();
  bindForgot();
  bindNavigation();
});

/* ════════════════════════════════════════
   NAVIGATION BINDINGS
   ════════════════════════════════════════ */

function bindNavigation() {
  // Login → Register
  $('#goRegister').addEventListener('click', () => navigateTo('register'));

  // Register → Login
  $('#goLogin').addEventListener('click', () => navigateTo('login'));
  $('#backFromRegister').addEventListener('click', () => navigateTo('login'));

  // Login → Forgot
  $('#goForgot').addEventListener('click', () => navigateTo('forgot'));

  // Forgot → Login
  $('#backFromForgot').addEventListener('click', () => {
    navigateTo('login');
    resetForgotView();
  });

  // Forgot success → Login
  $('#btnBackToLogin').addEventListener('click', () => {
    navigateTo('login');
    resetForgotView();
  });
}

/* ════════════════════════════════════════
   LOGIN
   ════════════════════════════════════════ */

function bindLogin() {
  const btn = $('#btnLogin');

  btn.addEventListener('click', async () => {
    if (!validateLogin()) {
      shakeElement($('#viewLogin .card__right') || btn);
      return;
    }

    setLoading(btn, true);
    await fakeDelay(1400);
    setLoading(btn, false);

    // Demo: simulate success
    // In production: replace with real fetch() to your backend
    const cedula = $('#loginCedula').value.trim();
    showToast(`Bienvenido, ${cedula}. Cargando sistema...`, 'success', 2500);

    // Optionally redirect after login:
    // setTimeout(() => { window.location.href = '/dashboard'; }, 2000);
  });

  // Allow Enter key
  ['loginCedula', 'loginPass'].forEach(id => {
    $(`#${id}`).addEventListener('keydown', e => {
      if (e.key === 'Enter') btn.click();
    });
  });
}

/* ════════════════════════════════════════
   REGISTER
   ════════════════════════════════════════ */

function bindRegister() {
  const btn = $('#btnRegister');

  btn.addEventListener('click', async () => {
    if (!validateRegister()) return;

    setLoading(btn, true);
    await fakeDelay(1600);
    setLoading(btn, false);

    // Demo: simulate successful registration
    const nombre = $('#regNombre').value.trim().split(' ')[0];
    showToast(`¡Cuenta creada! Bienvenido/a, ${nombre}.`, 'success', 3000);

    // Clear form
    clearRegisterForm();

    // Return to login
    setTimeout(() => navigateTo('login'), 1200);
  });

  // Enter key on last field
  $('#regPassConfirm').addEventListener('keydown', e => {
    if (e.key === 'Enter') btn.click();
  });
}

function clearRegisterForm() {
  ['regCedula','regNombre','regTelefono','regCorreo','regPass','regPassConfirm']
    .forEach(id => { $(`#${id}`).value = ''; });

  // Reset strength meter
  $('#strengthFill').style.width = '0%';
  $('#strengthLabel').textContent = '';

  clearAllErrors($('#viewRegister'));
}

/* ════════════════════════════════════════
   FORGOT PASSWORD — Solo Frontend / UI
   ════════════════════════════════════════ */

function bindForgot() {
  const btn = $('#btnForgot');

  // ── Mostrar pantalla de éxito ──
  btn.addEventListener('click', () => {
    const gmailInput = $('#forgotGmail');
    const gmailErr   = $('#forgotGmailErr');
    const email      = gmailInput.value.trim();

    clearError(gmailInput, gmailErr);

    if (!email) {
      setError(gmailInput, gmailErr, 'Ingrese su correo Gmail.');
      return;
    }
    if (!/^[^\s@]+@gmail\.com$/i.test(email)) {
      setError(gmailInput, gmailErr, 'Debe ser un correo @gmail.com válido.');
      return;
    }

    // Mostrar email en pantalla de éxito y pasar al paso 2
    $('#sentToEmail').textContent = email;
    $('#forgotStep1').classList.add('hidden');
    $('#forgotStep2').classList.remove('hidden');
    $('#forgotSupport').classList.add('hidden');
  });

  // ── Enter key ──
  $('#forgotGmail').addEventListener('keydown', e => {
    if (e.key === 'Enter') btn.click();
  });

  // ── Abrir Gmail en el navegador ──
  $('#btnOpenGmail').addEventListener('click', () => {
    window.open('https://mail.google.com', '_blank', 'noopener,noreferrer');
  });

  // ── Reenviar — solo UI, sin backend ──
  $('#btnResend').addEventListener('click', () => {
    const resendBtn = $('#btnResend');
    resendBtn.disabled = true;

    let secs = 30;
    resendBtn.innerHTML = `<i class="fa fa-clock" style="margin-right:5px"></i>Reenviar en ${secs}s`;

    const interval = setInterval(() => {
      secs--;
      if (secs <= 0) {
        clearInterval(interval);
        resendBtn.disabled = false;
        resendBtn.innerHTML = '<i class="fa fa-rotate-right" style="margin-right:5px"></i>No recibí el correo, reenviar';
      } else {
        resendBtn.innerHTML = `<i class="fa fa-clock" style="margin-right:5px"></i>Reenviar en ${secs}s`;
      }
    }, 1000);
  });
}

function resetForgotView() {
  $('#forgotStep1').classList.remove('hidden');
  $('#forgotStep2').classList.add('hidden');
  $('#forgotSupport').classList.remove('hidden');
  $('#forgotGmail').value = '';
  clearAllErrors($('#viewForgot'));
  const resendBtn = $('#btnResend');
  if (resendBtn) {
    resendBtn.disabled = false;
    resendBtn.innerHTML = '<i class="fa fa-rotate-right" style="margin-right:5px"></i>No recibí el correo, reenviar';
  }
}

/* ════════════════════════════════════════
   REMEMBER SESSION (persist to localStorage)
   ════════════════════════════════════════ */

// Pre-fill cédula if remembered
(function loadRemembered() {
  const saved = localStorage.getItem('unefa_cedula');
  if (saved) {
    $('#loginCedula').value = saved;
    $('#rememberMe').checked = true;
  }
})();

$('#btnLogin').addEventListener('click', () => {
  const remember = $('#rememberMe').checked;
  const cedula   = $('#loginCedula').value.trim();
  if (remember && cedula) {
    localStorage.setItem('unefa_cedula', cedula);
  } else {
    localStorage.removeItem('unefa_cedula');
  }
});
