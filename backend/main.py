from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from core.logger import log
import uvicorn

app = FastAPI(title="Backend Proyecto Visión")

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

# TODO para el equipo Backend: Agregar Endpoints CRUD y WebSockets

if __name__ == "__main__":
    log.info("Iniciando servicio Backend...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
