import React, { useState, useEffect, useCallback } from 'react';
import '../../styles/style.css';
import '../../styles/animations.css';
import '../../styles/dashboard.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const PAGE_SIZE = 30;

function decodeJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

const DashboardView = ({ onLogout }) => {
  const [eventos, setEventos] = useState([]);
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null);
  const [conexionWS, setConexionWS] = useState(false);
  const [verEnVivo, setVerEnVivo] = useState(false);

  const [usuario, setUsuario] = useState(null);

  const [totalEventos, setTotalEventos] = useState(0);
  const [paginaActual, setPaginaActual] = useState(0);
  const [cargandoPagina, setCargandoPagina] = useState(false);

  const [filtro, setFiltro] = useState('todos');
  const [busqueda, setBusqueda] = useState('');

  const [kpis, setKpis] = useState({ alertasHoy: 0, accesosOkHoy: 0, totalRegistros: 0 });

  const [alertaBanner, setAlertaBanner] = useState(null);
  const alertaTimerRef = React.useRef(null);

  const reproducirBeep = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [[0, 880], [0.35, 660]].forEach(([inicio, freq]) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'square';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + inicio);
        gain.gain.setValueAtTime(0.25, ctx.currentTime + inicio);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + inicio + 0.3);
        osc.start(ctx.currentTime + inicio);
        osc.stop(ctx.currentTime + inicio + 0.3);
      });
    } catch { /* audio bloqueado por el navegador */ }
  };

  const dispararAlerta = (evento) => {
    reproducirBeep();
    let parpadeando = true;
    const titleOriginal = document.title;
    const parpadeoInterval = setInterval(() => {
      document.title = parpadeando ? '🚨 ALERTA DETECTADA' : titleOriginal;
      parpadeando = !parpadeando;
    }, 700);
    setAlertaBanner({ id: evento.id, fecha: evento.fecha });
    clearTimeout(alertaTimerRef.current);
    alertaTimerRef.current = setTimeout(() => {
      setAlertaBanner(null);
      clearInterval(parpadeoInterval);
      document.title = titleOriginal;
    }, 8000);
    if (Notification.permission === 'granted') {
      new Notification('🚨 Alerta UNEFA', {
        body: 'Incumplimiento de normativa detectado.',
        icon: '/assets/images/escudo.png',
      });
    } else if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    const payload = decodeJwtPayload(token);
    if (payload?.sub) {
      fetch(`${API_URL}/usuarios/perfil`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(r => (r.ok ? r.json() : null))
        .then(data => {
          if (data) setUsuario(data);
          else setUsuario({ cedula: payload.sub });
        })
        .catch(() => setUsuario({ cedula: payload.sub }));
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/eventos/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setKpis(data);
      }
    } catch (err) {
      console.error('Error al cargar stats', err);
    }
  }, []);

  const fetchEventos = useCallback(async (pagina = 0, currentFiltro = 'todos') => {
    setCargandoPagina(true);
    try {
      const token = localStorage.getItem('token');
      const skip = pagina * PAGE_SIZE;
      const res = await fetch(`${API_URL}/eventos/?skip=${skip}&limit=${PAGE_SIZE}&tipo=${currentFiltro}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        const lista = Array.isArray(data) ? data : (data.data ?? []);
        const total = data.total ?? lista.length;
        setEventos(lista);
        setTotalEventos(total);
      }
    } catch (err) {
      console.error('Error al cargar eventos', err);
    } finally {
      setCargandoPagina(false);
    }
  }, []);

  const wsRef = React.useRef(null);
  const reconnectDelayRef = React.useRef(1000);
  const reconnectTimerRef = React.useRef(null);
  const unmountedRef = React.useRef(false);

  useEffect(() => {
    fetchStats();
    fetchEventos(0);
    unmountedRef.current = false;

    const WS_URL = API_URL.replace(/^http/, 'ws') + '/eventos/ws';

    function conectar() {
      if (unmountedRef.current) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectDelayRef.current = 1000;
        setConexionWS(true);
      };

      ws.onmessage = (event) => {
        const nuevoEvento = JSON.parse(event.data);
        setEventos(prev => [nuevoEvento, ...prev].slice(0, PAGE_SIZE));
        setTotalEventos(prev => prev + 1);
        setKpis(prev => ({
          ...prev,
          totalRegistros: prev.totalRegistros + 1,
          ...(nuevoEvento.alerta
            ? { alertasHoy: prev.alertasHoy + 1 }
            : { accesosOkHoy: prev.accesosOkHoy + 1 }),
        }));
        if (nuevoEvento.alerta) {
          setEventoSeleccionado(nuevoEvento);
          dispararAlerta(nuevoEvento);
        }
      };

      ws.onclose = () => {
        setConexionWS(false);
        if (unmountedRef.current) return;
        reconnectTimerRef.current = setTimeout(() => {
          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 30000);
          conectar();
        }, reconnectDelayRef.current);
      };

      ws.onerror = () => ws.close();
    }

    conectar();

    return () => {
      unmountedRef.current = true;
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [fetchEventos, fetchStats]);

  const totalPaginas = Math.ceil(totalEventos / PAGE_SIZE);

  const irAPagina = (pagina) => {
    if (pagina < 0 || pagina >= totalPaginas) return;
    setPaginaActual(pagina);
    fetchEventos(pagina, filtro);
  };

  const formatearFecha = (isoString) =>
    new Date(isoString).toLocaleString('es-VE', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    });

  const eventosFiltrados = eventos.filter(evt => {
    // El filtro de alerta/ok ya lo hace el backend, pero mantenemos búsqueda por texto localmente en la página actual
    if (busqueda) {
      const texto = busqueda.toLowerCase();
      const fecha = formatearFecha(evt.fecha).toLowerCase();
      const tipo  = evt.alerta ? 'incumplimiento' : 'acceso permitido';
      return fecha.includes(texto) || tipo.includes(texto);
    }
    return true;
  });

  const nombreUsuario = usuario
    ? (usuario.nombres ? `${usuario.nombres} ${usuario.apellidos ?? ''}`.trim() : usuario.cedula)
    : '—';
  const rolUsuario = usuario?.rol ? usuario.rol.toUpperCase() : '';

  return (
    <div className="dashboard">
      {/* BACKGROUND */}
      <div className="dashboard__bg">
        <div className="bg-image placeholder-bg" />
        <div className="bg-overlay" />
        <div className="bg-particles" id="particles" />
      </div>

      {/* ── HEADER ── */}
      <header className="dashboard__header">
        <div className="dashboard__header-brand">
          <img
            src="/assets/images/escudo.png"
            alt="Escudo UNEFA"
            className="dashboard__header-logo"
          />
          <div>
            <h1 className="dashboard__header-title">SISTEMA DE CONTROL UNEFA</h1>
            <span className={`dashboard__header-status ${conexionWS ? 'dashboard__header-status--online' : 'dashboard__header-status--offline'}`}>
              <i className="fa fa-circle dashboard__header-status-dot" />
              {conexionWS ? 'MONITOREO EN LÍNEA' : 'DESCONECTADO'}
            </span>
          </div>
        </div>

        <div className="dashboard__header-actions">
          <div className="dashboard__user-info">
            <div className="dashboard__user-name">
              <i className="fa fa-user-shield dashboard__user-name-icon" />
              {nombreUsuario}
            </div>
            {rolUsuario && (
              <div className="dashboard__user-role">{rolUsuario}</div>
            )}
          </div>

          <button
            onClick={() => setVerEnVivo(!verEnVivo)}
            className={`btn-camera ${verEnVivo ? 'btn-camera--on' : 'btn-camera--off'}`}
          >
            <i className={`fa ${verEnVivo ? 'fa-video-slash' : 'fa-video'}`} />
            {' '}
            <span>{verEnVivo ? 'OCULTAR CÁMARA' : 'VER EN VIVO'}</span>
          </button>

          <button onClick={onLogout} className="btn-primary btn-logout">
            <i className="fa fa-sign-out-alt" /> SALIR
          </button>
        </div>
      </header>

      {/* ── BANNER DE ALERTA ── */}
      {alertaBanner && (
        <div className="dashboard__alert-banner" onClick={() => setAlertaBanner(null)}>
          <i className="fa fa-exclamation-triangle dashboard__alert-banner-icon" />
          <span className="dashboard__alert-banner-text">
            🚨 ALERTA — INCUMPLIMIENTO DETECTADO — {formatearFecha(alertaBanner.fecha)}
          </span>
          <i className="fa fa-times dashboard__alert-banner-close" />
        </div>
      )}

      {/* ── MAIN ── */}
      <main className="dashboard__main">

        {/* COLUMNA IZQUIERDA */}
        <div className="dashboard__col-left">

          {/* KPIs */}
          <div className="dashboard__kpis">
            <div className="kpi-card kpi-card--danger">
              <div className="kpi-card__label">
                <i className="fa fa-exclamation-triangle" /> Alertas Hoy
              </div>
              <div className="kpi-card__value">{kpis.alertasHoy}</div>
            </div>
            <div className="kpi-card kpi-card--success">
              <div className="kpi-card__label">
                <i className="fa fa-check-circle" /> Accesos OK Hoy
              </div>
              <div className="kpi-card__value">{kpis.accesosOkHoy}</div>
            </div>
            <div className="kpi-card kpi-card--info">
              <div className="kpi-card__label">
                <i className="fa fa-database" /> Total Registros
              </div>
              <div className="kpi-card__value">{kpis.totalRegistros}</div>
            </div>
          </div>

          {/* FILTROS */}
          <div className="dashboard__filters">
            <div className="dashboard__search-wrap">
              <i className="fa fa-search dashboard__search-icon" />
              <input
                type="text"
                placeholder="Buscar por fecha o tipo..."
                value={busqueda}
                onChange={e => setBusqueda(e.target.value)}
                className="dashboard__search-input"
              />
            </div>
            {[
              { key: 'todos',  label: 'Todos' },
              { key: 'alerta', label: '🔴 Alertas' },
              { key: 'ok',     label: '🟢 OK' },
            ].map(f => (
              <button
                key={f.key}
                onClick={() => { 
                  setFiltro(f.key); 
                  setPaginaActual(0); 
                  fetchEventos(0, f.key); 
                }}
                className={`filter-btn ${filtro === f.key ? 'filter-btn--active' : ''}`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* HISTORIAL */}
          <div className="card dashboard__history">
            <h2 className="dashboard__history-header">
              <i className="fa fa-list" /> Historial de Accesos y Alertas
              <span className="dashboard__history-count">
                {eventosFiltrados.length} de {totalEventos} registros
              </span>
            </h2>

            <div className="dashboard__history-list">
              {cargandoPagina ? (
                <p className="dashboard__history-empty">
                  <i className="fa fa-spinner fa-spin" /> Cargando...
                </p>
              ) : eventosFiltrados.length === 0 ? (
                <p className="dashboard__history-empty">No hay eventos que coincidan.</p>
              ) : (
                <div className="dashboard__event-list">
                  {eventosFiltrados.map(evt => (
                    <div
                      key={evt.id}
                      onClick={() => { setEventoSeleccionado(evt); setVerEnVivo(false); }}
                      className={[
                        'event-row',
                        evt.alerta ? 'event-row--alert' : 'event-row--ok',
                        eventoSeleccionado?.id === evt.id ? 'event-row--selected' : '',
                      ].join(' ')}
                    >
                      <div>
                        <div className="event-row__fecha">
                          <i className="fa fa-clock" /> {formatearFecha(evt.fecha)}
                        </div>
                        <div className={`event-row__tipo ${evt.alerta ? 'event-row__tipo--alert' : 'event-row__tipo--ok'}`}>
                          {evt.alerta ? '⚠ INCUMPLIMIENTO DETECTADO' : '✓ ACCESO PERMITIDO'}
                        </div>
                      </div>
                      <i className="fa fa-chevron-right event-row__arrow" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* PAGINACIÓN */}
            {totalPaginas > 1 && (
              <div className="dashboard__pagination">
                <button className="pagination-btn" onClick={() => irAPagina(0)} disabled={paginaActual === 0}>
                  <i className="fa fa-angle-double-left" />
                </button>
                <button className="pagination-btn" onClick={() => irAPagina(paginaActual - 1)} disabled={paginaActual === 0}>
                  <i className="fa fa-angle-left" />
                </button>
                <span className="pagination-label">Página {paginaActual + 1} / {totalPaginas}</span>
                <button className="pagination-btn" onClick={() => irAPagina(paginaActual + 1)} disabled={paginaActual >= totalPaginas - 1}>
                  <i className="fa fa-angle-right" />
                </button>
                <button className="pagination-btn" onClick={() => irAPagina(totalPaginas - 1)} disabled={paginaActual >= totalPaginas - 1}>
                  <i className="fa fa-angle-double-right" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* COLUMNA DERECHA */}
        <div className="card dashboard__col-right">
          <h2 className="dashboard__detail-header">
            <i className={`fa ${verEnVivo ? 'fa-video' : 'fa-camera'}`} />
            {' '}{verEnVivo ? 'Transmisión en Vivo' : 'Evidencia Fotográfica'}
          </h2>

          {verEnVivo ? (
            <div className="dashboard__media-wrap">
              <div className="dashboard__video-container">
                <img
                  src="http://localhost:8001/stream"
                  alt="Transmisión en Vivo"
                  onError={e => {
                    e.target.onerror = null;
                    e.target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22640%22%20height%3D%22480%22%3E%3Crect%20width%3D%22640%22%20height%3D%22480%22%20fill%3D%22%230a1628%22%2F%3E%3Ctext%20x%3D%22320%22%20y%3D%22240%22%20font-family%3D%22sans-serif%22%20font-size%3D%2222%22%20fill%3D%22%23e05c5c%22%20text-anchor%3D%22middle%22%3E%26%239888%3B%20C%C3%81MARA%20NO%20DISPONIBLE%3C%2Ftext%3E%3C%2Fsvg%3E';
                  }}
                />
                <div className="badge-live">
                  <i className="fa fa-circle badge-live__dot" /> EN VIVO
                </div>
              </div>
              <div className="dashboard__detail-info">
                <h3 className="dashboard__detail-info-title">Monitoreo en Tiempo Real</h3>
                <p className="dashboard__detail-info-text">
                  Estás viendo la cámara procesada por el motor de IA en el Edge. Este flujo no se guarda en el servidor.
                </p>
              </div>
            </div>
          ) : eventoSeleccionado ? (
            <div className="dashboard__media-wrap">
              <div className="dashboard__video-container">
                <img
                  src={`${API_URL}/${eventoSeleccionado.foto_path}`}
                  alt="Evidencia"
                  className="dashboard__detail-img"
                  onError={e => {
                    e.target.onerror = null;
                    e.target.src = 'https://via.placeholder.com/640x480?text=Imagen+no+encontrada';
                  }}
                />
                {eventoSeleccionado.alerta && (
                  <div className="badge-alert">ALERTA</div>
                )}
              </div>
              <div className="dashboard__detail-info">
                <h3 className="dashboard__detail-info-title">Análisis de Vestimenta</h3>
                {eventoSeleccionado.alerta ? (
                  <div className="dashboard__detail-meta">
                    <p>
                      <strong className="detail-meta-alert">Motivo:</strong>{' '}
                      Faltan prendas requeridas ({eventoSeleccionado.metadatos_ia?.clases_faltantes?.join(', ') || 'No identificadas'})
                    </p>
                    <p>
                      <strong>Personas en cuadro:</strong>{' '}
                      {eventoSeleccionado.metadatos_ia?.rostros_detectados}
                    </p>
                  </div>
                ) : (
                  <p className="dashboard__detail-info-text">
                    El estudiante cumplía con toda la normativa (Chaqueta/Uniforme, Pantalón Oscuro y Carnet).
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="dashboard__empty-state">
              <i className="fa fa-image dashboard__empty-state-icon" />
              <p>Seleccione un evento de la lista para ver la evidencia.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardView;
