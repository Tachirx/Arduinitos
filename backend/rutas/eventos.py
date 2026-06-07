import os
import base64
import time
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from base_datos import obtener_db
from modelos import EventoVision, Usuario
from core.autenticacion import obtener_usuario_actual
from core.hardware import despachador

router = APIRouter(prefix="/eventos", tags=["Eventos de Visión"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_eventos(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class DatosEventoIA(BaseModel):
    """Esquema de validación para los eventos de visión artificial."""
    timestamp: str
    cumple_normativa: bool
    clases_faltantes: List[str]
    confianzas: Dict[str, float]
    rostros_detectados: int
    evidencia_b64: str

@router.get("/stats")
def obtener_estadisticas(db: Session = Depends(obtener_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    """Obtiene los KPIs globales y del día para el dashboard."""
    inicio_dia = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    
    total = db.query(EventoVision).count()
    eventos_hoy = db.query(EventoVision.alerta).filter(EventoVision.fecha >= inicio_dia).all()
    
    alertas_hoy = sum(1 for e in eventos_hoy if e[0])
    accesos_ok_hoy = sum(1 for e in eventos_hoy if not e[0])
    
    return {
        "totalRegistros": total,
        "alertasHoy": alertas_hoy,
        "accesosOkHoy": accesos_ok_hoy
    }

@router.get("/")
def listar_eventos(
    skip: int = 0, 
    limit: int = 30,
    tipo: str = "todos",
    db: Session = Depends(obtener_db), 
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Lista los eventos de visión registrados en el sistema con soporte para paginación y filtros reales de base de datos."""
    query = db.query(EventoVision)
    
    if tipo == "alerta":
        query = query.filter(EventoVision.alerta == True)
    elif tipo == "ok":
        query = query.filter(EventoVision.alerta == False)
        
    total_eventos = query.count()
    eventos = query.order_by(EventoVision.fecha.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total_eventos,
        "skip": skip,
        "limit": limit,
        "tipo": tipo,
        "data": eventos
    }

@router.post("/")
def registrar_evento(evento: dict, db: Session = Depends(obtener_db)):
    """Placeholder original para compatibilidad retrospectiva."""
    return {"mensaje": "Evento recibido (pendiente implementación lógica IA)"}

@router.post("/ia")
def registrar_evento_ia(datos: DatosEventoIA, background_tasks: BackgroundTasks, db: Session = Depends(obtener_db)):
    """Recibe, decodifica y persiste los eventos enviados por el motor de visión artificial."""
    try:
        # 1. Definir y asegurar la existencia de la carpeta de almacenamiento físico
        ruta_directorio_base = os.path.dirname(os.path.abspath(__file__))
        ruta_almacenamiento = os.path.abspath(
            os.path.join(ruta_directorio_base, "..", "almacenamiento", "eventos")
        )
        os.makedirs(ruta_almacenamiento, exist_ok=True)

        # 2. Decodificar la imagen en Base64 enviada como evidencia
        try:
            imagen_bytes = base64.b64decode(datos.evidencia_b64)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Evidencia fotográfica corrupta o codificación Base64 inválida: {exc}"
            )

        # 3. Guardar el archivo físico en el almacenamiento del servidor
        nombre_archivo = f"evento_{int(time.time())}.jpg"
        ruta_archivo_completa = os.path.join(ruta_almacenamiento, nombre_archivo)
        
        with open(ruta_archivo_completa, "wb") as archivo_imagen:
            archivo_imagen.write(imagen_bytes)

        # Ruta relativa uniforme para guardar en base de datos
        ruta_relativa_db = f"almacenamiento/eventos/{nombre_archivo}"

        # 4. Crear e insertar el registro del evento en la base de datos MariaDB
        estado_inicial = "pendiente" if not datos.cumple_normativa else "registrado"
        alerta_activa = not datos.cumple_normativa

        nuevo_evento = EventoVision(
            fecha=datetime.utcnow(),
            estado=estado_inicial,
            alerta=alerta_activa,
            foto_path=ruta_relativa_db,
            metadatos_ia={
                "clases_faltantes": datos.clases_faltantes,
                "confianzas": datos.confianzas,
                "rostros_detectados": datos.rostros_detectados
            }
        )

        db.add(nuevo_evento)
        db.commit()
        db.refresh(nuevo_evento)

        # 5. Emitir alerta física/acústica si hay incumplimiento normativo
        if alerta_activa:
            despachador.emitir_alerta()

        # 6. Emitir por WebSocket
        evento_dict = {
            "id": nuevo_evento.id,
            "fecha": nuevo_evento.fecha.isoformat(),
            "estado": nuevo_evento.estado,
            "alerta": nuevo_evento.alerta,
            "foto_path": nuevo_evento.foto_path,
            "metadatos_ia": nuevo_evento.metadatos_ia
        }
        background_tasks.add_task(manager.broadcast, evento_dict)

        return {
            "mensaje": "Evento de visión artificial registrado exitosamente.",
            "id": nuevo_evento.id,
            "estado": nuevo_evento.estado
        }

    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al persistir el evento de IA en el servidor: {exc}"
        )
