import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from base_datos import obtener_db
from modelos import Usuario

# Configuración desde entorno
SECRET_KEY = os.getenv("SECRET_KEY", "CLAVE_POR_DEFECTO_CAMBIAR_EN_PROD")
ALGORITMO = os.getenv("ALGORITMO", "HS256")
TIEMPO_EXPIRACION_MINUTOS = int(os.getenv("TIEMPO_EXPIRACION_MINUTOS", 480))
TIEMPO_BLOQUEO_MINUTOS = 15

esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/iniciar_sesion")
contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_hash_clave(clave: str) -> str:
    """Genera un hash bcrypt de la clave."""
    return contexto_pwd.hash(clave)

def verificar_clave(clave_plana: str, clave_hash: str) -> bool:
    """Verifica si la clave plana coincide con el hash."""
    return contexto_pwd.verify(clave_plana, clave_hash)

def crear_token_acceso(data: dict, tiempo_expiracion: Optional[timedelta] = None):
    """Crea un token JWT firmado."""
    a_codificar = data.copy()
    if tiempo_expiracion:
        expiracion = datetime.utcnow() + tiempo_expiracion
    else:
        expiracion = datetime.utcnow() + timedelta(minutes=TIEMPO_EXPIRACION_MINUTOS)
    
    a_codificar.update({"exp": expiracion})
    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITMO)

def obtener_usuario_actual(token: str = Depends(esquema_oauth2), db: Session = Depends(obtener_db)):
    """Dependencia para obtener el usuario autenticado desde el token."""
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        cedula: str = payload.get("sub")
        if cedula is None:
            raise excepcion_credenciales
    except JWTError:
        raise excepcion_credenciales
        
    usuario = db.query(Usuario).filter(Usuario.cedula == cedula).first()
    if usuario is None:
        raise excepcion_credenciales
    
    if not usuario.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    return usuario

def verificar_bloqueo(usuario: Usuario):
    """Verifica si el usuario está bloqueado temporalmente."""
    if usuario.inicio_bloqueo:
        tiempo_transcurrido = datetime.utcnow() - usuario.inicio_bloqueo
        if tiempo_transcurrido < timedelta(minutes=TIEMPO_BLOQUEO_MINUTOS):
            minutos_restantes = TIEMPO_BLOQUEO_MINUTOS - (tiempo_transcurrido.seconds // 60)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cuenta bloqueada temporalmente. Intente en {minutos_restantes} minutos."
            )
        else:
            # El tiempo de bloqueo expiró, limpiar estado (se hará en la lógica de login)
            pass
    return False
