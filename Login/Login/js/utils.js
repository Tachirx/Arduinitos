/* ══════════════════════════════════════════
   UNEFA — Sistema de Gestión Académica
   utils.js  |  Shared Helpers
   ══════════════════════════════════════════ */

'use strict';

/**
 * $ — shorthand querySelector
 */
const $ = (selector, ctx = document) => ctx.querySelector(selector);

/**
 * $$ — shorthand querySelectorAll (returns array)
 */
const $$ = (selector, ctx = document) => [...ctx.querySelectorAll(selector)];

/**
 * showToast — display a transient notification
 * @param {string} msg     - message text
 * @param {'success'|'error'} type - style variant
 * @param {number} duration        - milliseconds visible
 */
function showToast(msg, type = 'success', duration = 3200) {
  const toast = $('#toast');
  const icon  = toast.querySelector('.toast__icon');
  const label = toast.querySelector('.toast__msg');

  // Reset classes
  toast.classList.remove('success', 'error');
  icon.classList.remove('fa-circle-check', 'fa-circle-xmark');

  toast.classList.add(type);
  icon.classList.add(type === 'success' ? 'fa-circle-check' : 'fa-circle-xmark');
  label.textContent = msg;

  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

/**
 * setLoading — toggle button loading state
 */
function setLoading(btn, loading) {
  const text   = btn.querySelector('.btn-text');
  const loader = btn.querySelector('.btn-loader');
  btn.disabled = loading;
  text.classList.toggle('hidden', loading);
  loader.classList.toggle('hidden', !loading);
}

/**
 * shakeElement — trigger shake animation
 */
function shakeElement(el) {
  el.classList.remove('shake');
  void el.offsetWidth; // reflow
  el.classList.add('shake');
  el.addEventListener('animationend', () => el.classList.remove('shake'), { once: true });
}

/**
 * fakeDelay — simulate async network call
 */
function fakeDelay(ms = 1200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * generateParticles — ambient background dots
 */
function generateParticles(container, count = 25) {
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.cssText = `
      left: ${Math.random() * 100}%;
      top:  ${Math.random() * 100}%;
      width:  ${Math.random() * 2 + 1}px;
      height: ${Math.random() * 2 + 1}px;
      animation-duration:  ${Math.random() * 20 + 12}s;
      animation-delay:    -${Math.random() * 20}s;
      opacity: ${Math.random() * .5 + .1};
    `;
    container.appendChild(p);
  }
}
