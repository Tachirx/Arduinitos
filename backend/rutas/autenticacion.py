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


class PreguntaSeguridad(BaseModel):
    pregunta: str
    respuesta: str

class RegistroUsuario(BaseModel):
    cedula: str = Field(..., ejemplo="12345678")
    nombres: str = Field(..., ejemplo="Juan")
    apellidos: str = Field(..., ejemplo="Perez")
    telefono: str = Field(None, ejemplo="04121234567")
    clave: str = Field(..., min_length=6)
    rol: str = Field("portero", pattern="^(admin|portero)$")
    preguntas: List[PreguntaSeguridad] = Field(..., min_items=3, max_items=3)

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/registrar", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: RegistroUsuario, db: Session = Depends(obtener_db)):
    
    cedula_limpia = datos.cedula.strip().upper()
    if cedula_limpia.isdigit():
        cedula_limpia = f"V-{cedula_limpia}"
        
   
    existente = db.query(Usuario).filter(Usuario.cedula == cedula_limpia).first()
    if existente:
        raise HTTPException(status_code=400, detail="La cédula ya se encuentra registrada.")
    
    
    clave_hash = generar_hash_clave(datos.clave)
    preguntas_procesadas = []
    for p in datos.preguntas:
        preguntas_procesadas.append({
            "pregunta": p.pregunta,
            "respuesta_hash": generar_hash_clave(p.respuesta.lower().strip())
        })
    
    nuevo_usuario = Usuario(
        cedula=cedula_limpia,
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
    usuario_ingresado = form_data.username.strip()
    
    
    if usuario_ingresado.isdigit():
        usuario_ingresado = f"V-{usuario_ingresado}"
        
    usuario = db.query(Usuario).filter(Usuario.cedula == usuario_ingresado).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Cédula o clave incorrecta")
    
    
    verificar_bloqueo(usuario)
    
    if not verificar_clave(form_data.password, usuario.clave_hash):
       
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
    

    usuario.intentos_fallidos = 0
    usuario.inicio_bloqueo = None
    db.commit()
    
    token = crear_token_acceso(data={"sub": usuario.cedula})
    return {"access_token": token, "token_type": "bearer"}

class RecuperarClave(BaseModel):
    cedula: str
    respuestas: List[str]
    nueva_clave: str = Field(..., min_length=6)

@router.get("/preguntas/{cedula}")
def obtener_preguntas(cedula: str, db: Session = Depends(obtener_db)):
    cedula_limpia = cedula.strip().upper()
    if cedula_limpia.isdigit():
        cedula_limpia = f"V-{cedula_limpia}"
        
    usuario = db.query(Usuario).filter(Usuario.cedula == cedula_limpia).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    preguntas = [p["pregunta"] for p in usuario.preguntas_seguridad]
    return {"preguntas": preguntas}

@router.post("/recuperar_clave")
def recuperar_clave(datos: RecuperarClave, db: Session = Depends(obtener_db)):
    cedula_limpia = datos.cedula.strip().upper()
    if cedula_limpia.isdigit():
        cedula_limpia = f"V-{cedula_limpia}"
        
    usuario = db.query(Usuario).filter(Usuario.cedula == cedula_limpia).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if len(datos.respuestas) != len(usuario.preguntas_seguridad):
        raise HTTPException(status_code=400, detail="Cantidad de respuestas incorrecta")
        
    for i, p in enumerate(usuario.preguntas_seguridad):
        if not verificar_clave(datos.respuestas[i].lower().strip(), p["respuesta_hash"]):
            raise HTTPException(status_code=401, detail="Respuestas de seguridad incorrectas")
            
    usuario.clave_hash = generar_hash_clave(datos.nueva_clave)
    usuario.intentos_fallidos = 0
    usuario.inicio_bloqueo = None
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}
