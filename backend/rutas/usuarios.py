from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from base_datos import obtener_db
from modelos import Usuario
from core.autenticacion import obtener_usuario_actual

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/perfil")
def obtener_perfil(usuario: Usuario = Depends(obtener_usuario_actual)):
    return {
        "cedula": usuario.cedula,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "rol": usuario.rol,
        "telefono": usuario.telefono
    }

@router.get("/")
def listar_usuarios(db: Session = Depends(obtener_db), actual: Usuario = Depends(obtener_usuario_actual)):
    if actual.rol != "admin":
        raise HTTPException(status_code=403, detail="No tiene permisos para ver esta lista")
    
    usuarios = db.query(Usuario).all()
    return usuarios
