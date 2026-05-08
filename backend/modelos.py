from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, JSON
from datetime import datetime
from base_datos import Base

class Usuario(Base):
    """Modelo para la gestión de usuarios y seguridad."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    clave_hash = Column(String(255), nullable=False)
    rol = Column(Enum("admin", "portero", name="roles_usuario"), default="portero")
    
    #  hashes de las respuestas a 3 preguntas
    preguntas_seguridad = Column(JSON, nullable=True)
    
    #  acceso y bloqueo
    intentos_fallidos = Column(Integer, default=0)
    inicio_bloqueo = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)

class EventoVision(Base):
    """Modelo para el registro de eventos detectados por la IA."""
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(Enum("pendiente", "registrado", "descartado", name="estados_evento"), default="pendiente")
    alerta = Column(Boolean, default=False)
    foto_path = Column(String(255), nullable=True)
    metadatos_ia = Column(JSON, nullable=True)
    
    #  portero que validó el evento (no es obligatorio:))
    id_usuario_validador = Column(Integer, nullable=True)
