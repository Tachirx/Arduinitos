from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_datos import obtener_db
from modelos import EventoVision, Usuario
from core.autenticacion import obtener_usuario_actual

router = APIRouter(prefix="/eventos", tags=["Eventos de Visión"])

@router.get("/")
def listar_eventos(db: Session = Depends(obtener_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    # Los porteros y admins pueden ver eventos
    return db.query(EventoVision).all()

@router.post("/")
def registrar_evento(evento: dict, db: Session = Depends(obtener_db)):
    # Este endpoint sería llamado por el motor de IA
    # Por ahora solo un placeholder
    return {"mensaje": "Evento recibido (pendiente implementación lógica IA)"}
