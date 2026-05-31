from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from core.logger import log
import uvicorn

import base_datos
from rutas import autenticacion, usuarios, eventos

# Inicializar base de datos
base_datos.inicializar_db()

app = FastAPI(title="Backend Proyecto Visión")

# Habilitar CORS para permitir peticiones desde el frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asegurar existencia y montar directorio estático de almacenamiento para evidencias de la IA
ruta_directorio_base = os.path.dirname(os.path.abspath(__file__))
ruta_almacenamiento = os.path.join(ruta_directorio_base, "almacenamiento")
os.makedirs(ruta_almacenamiento, exist_ok=True)
app.mount("/almacenamiento", StaticFiles(directory=ruta_almacenamiento), name="almacenamiento")

#  Routers
app.include_router(autenticacion.router)
app.include_router(usuarios.router)
app.include_router(eventos.router)


# Middleware / Handler de Excepciones Globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Error no manejado en {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. El equipo ha sido notificado en logs."},
    )

@app.get("/")
def read_root():
    log.info("Acceso a ruta raíz.")
    return {"estado": "Backend en línea y preparado."}

@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    log.info("Iniciando servicio Backend...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
