import React, { useState, useEffect } from 'react';
import '../../styles/style.css';
import '../../styles/animations.css';
import LoginView from './LoginView';
import RegisterView from './RegisterView';
import ForgotView from './ForgotView';

const AuthContainer = ({ onLogin }) => {
  const [currentView, setCurrentView] = useState('login'); // 'login', 'register', 'forgot'

  useEffect(() => {
    // Inject Font Awesome & Fonts if not already in index.html
    const linkFA = document.createElement('link');
    linkFA.rel = 'stylesheet';
    linkFA.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css';
    document.head.appendChild(linkFA);

    const linkFonts = document.createElement('link');
    linkFonts.rel = 'stylesheet';
    linkFonts.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Nunito:wght@300;400;500;600;700&display=swap';
    document.head.appendChild(linkFonts);

    return () => {
      document.head.removeChild(linkFA);
      document.head.removeChild(linkFonts);
    };
  }, []);

  return (
    <div style={{ fontFamily: 'var(--font-body)', background: 'var(--navy-900)', color: 'var(--white)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', overflowX: 'hidden', position: 'relative' }}>
      {/* ════════════ BACKGROUND ════════════ */}
      <div className="bg-layer">
        <div className="bg-image placeholder-bg"></div>
        <div className="bg-overlay"></div>
        <div className="bg-particles" id="particles"></div>
      </div>

      {/* ════════════ MAIN CARD ════════════ */}
      <main className="main-wrapper">
        <div className="card" id="authCard">
          
          {/* ── LEFT PANEL ── */}
          <div className="card__left">
            <img src="/assets/images/escudo.png" alt="Escudo UNEFA" className="logo" />
            <h1 className="brand-name">UNEFA</h1>
            <p className="brand-full">Universidad Nacional Experimental<br />Politécnica de la Fuerza Armada<br />Nacional Bolivariana</p>
            <p className="brand-sub">República Bolivariana de Venezuela<br />Desde el 26 de Abril de 1999</p>
          </div>

          {/* ── DIVIDER ── */}
          <div className="card__divider"></div>

          {/* ── RIGHT PANEL (views) ── */}
          <div className="card__right">
            <LoginView isActive={currentView === 'login'} navigateTo={setCurrentView} onLogin={onLogin} />
            <RegisterView isActive={currentView === 'register'} navigateTo={setCurrentView} />
            <ForgotView isActive={currentView === 'forgot'} navigateTo={setCurrentView} />
          </div>
        </div>
      </main>

      {/* ════════════ FOOTER ════════════ */}
      <footer className="site-footer" style={{ zIndex: 10, position: 'absolute', bottom: '10px', fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
        © {new Date().getFullYear()} UNEFA — Sistema de Detección de Uniforme. Todos los derechos reservados.
      </footer>
    </div>
  );
};

export default AuthContainer;
