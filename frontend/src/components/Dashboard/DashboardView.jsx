import React, { useState, useEffect } from 'react';
import '../../styles/style.css';
import '../../styles/animations.css';

const DashboardView = ({ onLogout }) => {
  const [eventos, setEventos] = useState([]);
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null);
  const [conexionWS, setConexionWS] = useState(false);

  useEffect(() => {
    // 1. Cargar historial
    const fetchEventos = async () => {
      try {
        // En una app real, aquí se envía el JWT token en los headers
        const res = await fetch('http://localhost:8000/eventos/');
        if (res.ok) {
          const data = await res.json();
          setEventos(data);
        }
      } catch (err) {
        console.error("Error al cargar eventos", err);
      }
    };
    fetchEventos();

    // 2. Conectar WebSocket
    const ws = new WebSocket('ws://localhost:8000/eventos/ws');
    
    ws.onopen = () => {
      setConexionWS(true);
      console.log("WebSocket conectado");
    };

    ws.onmessage = (event) => {
      const nuevoEvento = JSON.parse(event.data);
      console.log("Nuevo evento recibido:", nuevoEvento);
      // Añadir al inicio de la lista
      setEventos(prev => [nuevoEvento, ...prev]);
      
      // Opcional: Si no hay ninguno seleccionado y llega una alerta, auto-seleccionarlo
      if (nuevoEvento.alerta) {
        setEventoSeleccionado(nuevoEvento);
      }
    };

    ws.onclose = () => {
      setConexionWS(false);
      console.log("WebSocket desconectado");
    };

    return () => {
      ws.close();
    };
  }, []);

  const formatearFecha = (isoString) => {
    const fecha = new Date(isoString);
    return fecha.toLocaleString('es-VE', { 
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };

  return (
    <div style={{ fontFamily: 'var(--font-body)', background: 'var(--navy-900)', color: 'var(--white)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* BACKGROUND */}
      <div className="bg-layer" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        <div className="bg-image placeholder-bg"></div>
        <div className="bg-overlay"></div>
        <div className="bg-particles" id="particles"></div>
      </div>

      {/* HEADER */}
      <header style={{ position: 'relative', zIndex: 10, padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(10, 25, 47, 0.7)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <img src="/assets/images/escudo.png" alt="Escudo UNEFA" style={{ width: '40px', height: 'auto' }} />
          <div>
            <h1 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'var(--font-brand)', letterSpacing: '1px' }}>SISTEMA DE CONTROL UNEFA</h1>
            <span style={{ fontSize: '0.8rem', color: conexionWS ? '#4caf50' : '#f44336', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <i className="fa fa-circle" style={{ fontSize: '8px' }}></i>
              {conexionWS ? 'MONITOREO EN LÍNEA' : 'DESCONECTADO'}
            </span>
          </div>
        </div>
        <button onClick={onLogout} className="btn-primary" style={{ padding: '8px 20px', width: 'auto', borderRadius: '4px' }}>
          <i className="fa fa-sign-out-alt" style={{ marginRight: '8px' }}></i> SALIR
        </button>
      </header>

      {/* MAIN CONTENT */}
      <main style={{ position: 'relative', zIndex: 10, flex: 1, padding: '30px 40px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        
        {/* LISTA DE EVENTOS */}
        <div className="card" style={{ width: '100%', maxWidth: 'none', height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column', padding: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
            <i className="fa fa-list" style={{ marginRight: '10px' }}></i>
            Historial de Accesos y Alertas
          </h2>
          
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: '10px' }}>
            {eventos.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.5)', marginTop: '40px' }}>No hay eventos registrados.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {eventos.map(evt => (
                  <div 
                    key={evt.id} 
                    onClick={() => setEventoSeleccionado(evt)}
                    style={{ 
                      padding: '15px', 
                      background: eventoSeleccionado?.id === evt.id ? 'rgba(100, 255, 218, 0.1)' : 'rgba(255,255,255,0.03)', 
                      border: `1px solid ${eventoSeleccionado?.id === evt.id ? 'var(--accent-teal)' : 'rgba(255,255,255,0.05)'}`,
                      borderLeft: `4px solid ${evt.alerta ? '#f44336' : '#4caf50'}`,
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.6)', marginBottom: '5px' }}>
                        <i className="fa fa-clock" style={{ marginRight: '5px' }}></i> {formatearFecha(evt.fecha)}
                      </div>
                      <div style={{ fontWeight: '600', color: evt.alerta ? '#ff8a80' : '#b9f6ca' }}>
                        {evt.alerta ? 'INCUMPLIMIENTO DETECTADO' : 'ACCESO PERMITIDO'}
                      </div>
                    </div>
                    <div>
                      <i className="fa fa-chevron-right" style={{ color: 'rgba(255,255,255,0.3)' }}></i>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* DETALLE DEL EVENTO */}
        <div className="card" style={{ width: '100%', maxWidth: 'none', height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column', padding: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
            <i className="fa fa-camera" style={{ marginRight: '10px' }}></i>
            Evidencia Fotográfica
          </h2>

          {eventoSeleccionado ? (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div style={{ flex: 1, background: '#000', borderRadius: '8px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                <img 
                  src={`http://localhost:8000/${eventoSeleccionado.foto_path}`} 
                  alt="Evidencia" 
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                  onError={(e) => { e.target.onerror = null; e.target.src = 'https://via.placeholder.com/640x480?text=Imagen+no+encontrada' }}
                />
                {eventoSeleccionado.alerta && (
                  <div style={{ position: 'absolute', top: '15px', right: '15px', background: 'rgba(244, 67, 54, 0.9)', padding: '5px 15px', borderRadius: '20px', fontWeight: 'bold', fontSize: '0.8rem', boxShadow: '0 4px 10px rgba(0,0,0,0.5)' }}>
                    ALERTA
                  </div>
                )}
              </div>
              
              <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '1rem', marginBottom: '10px', color: 'var(--accent-teal)' }}>Metadatos de la IA</h3>
                {eventoSeleccionado.alerta ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.9rem' }}>
                    <p style={{ margin: 0 }}><strong style={{ color: '#ff8a80' }}>Prendas Faltantes:</strong> {eventoSeleccionado.metadatos_ia.clases_faltantes.join(', ') || 'Desconocido'}</p>
                    <p style={{ margin: 0 }}><strong>Rostros Detectados:</strong> {eventoSeleccionado.metadatos_ia.rostros_detectados}</p>
                  </div>
                ) : (
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>El estudiante cumplía con toda la normativa (Chaqueta/Uniforme, Pantalón Oscuro y Carnet).</p>
                )}
              </div>
            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.3)' }}>
              <i className="fa fa-image" style={{ fontSize: '4rem', marginBottom: '15px' }}></i>
              <p>Seleccione un evento de la lista para ver la evidencia.</p>
            </div>
          )}
        </div>

      </main>
    </div>
  );
};

export default DashboardView;
