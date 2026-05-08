from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

from base_datos import obtener_db
from modelos import Usuario
from core.autenticacion import generar_hash_clave, verificar_clave, crear_token_acceso, verificar_bloqueo

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Esquemas de Pydantic
class PreguntaSeguridad(BaseModel):
    pregunta: str
    respuesta: str

class RegistroUsuario(BaseModel):
    cedula: str = Field(..., example="12345678")
    nombres: str = Field(..., example="Juan")
    apellidos: str = Field(..., example="Perez")
    telefono: str = Field(None, example="04121234567")
    clave: str = Field(..., min_length=6)
    rol: str = Field("portero", pattern="^(admin|portero)$")
    preguntas: List[PreguntaSeguridad] = Field(..., min_items=3, max_items=3)

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/registrar", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: RegistroUsuario, db: Session = Depends(obtener_db)):
    # Verificar si ya existe el usuario
    existente = db.query(Usuario).filter(Usuario.cedula == datos.cedula).first()
    if existente:
        raise HTTPException(status_code=400, detail="La cédula ya se encuentra registrada.")
    
    #  clave y respuestas de seguridad
    clave_hash = generar_hash_clave(datos.clave)
    preguntas_procesadas = []
    for p in datos.preguntas:
        preguntas_procesadas.append({
            "pregunta": p.pregunta,
            "respuesta_hash": generar_hash_clave(p.respuesta.lower().strip())
        })
    
    nuevo_usuario = Usuario(
        cedula=datos.cedula,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        telefono=datos.telefono,
        clave_hash=clave_hash,
        rol=datos.rol,
        preguntas_seguridad=preguntas_procesadas
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    token = crear_token_acceso(data={"sub": nuevo_usuario.cedula})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/iniciar_sesion", response_model=Token)
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(obtener_db)):
    usuario = db.query(Usuario).filter(Usuario.cedula == form_data.username).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Cédula o clave incorrecta")
    
    # por si está bloqueado
    verificar_bloqueo(usuario)
    
    if not verificar_clave(form_data.password, usuario.clave_hash):
        # el numero de intentos fallidos
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= 5:
            usuario.inicio_bloqueo = datetime.utcnow()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Demasiados intentos fallidos. Cuenta bloqueada por 15 min."
            )
        db.commit()
        raise HTTPException(status_code=401, detail="Cédula o clave incorrecta")
    
    # Reiniciar intentos fallidos tras éxito
    usuario.intentos_fallidos = 0
    usuario.inicio_bloqueo = None
    db.commit()
    
    token = crear_token_acceso(data={"sub": usuario.cedula})
    return {"access_token": token, "token_type": "bearer"}
