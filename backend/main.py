from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
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
    allow_origins=["*"], # Permitimos todo para despliegue local
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Frontend Construido 
ruta_frontend = os.path.join(ruta_directorio_base, "..", "frontend", "dist")
if os.path.exists(ruta_frontend):
    
    app.mount("/assets", StaticFiles(directory=os.path.join(ruta_frontend, "assets")), name="frontend_assets")
    
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        
        rutas_api = ["auth", "usuarios", "eventos", "almacenamiento", "health"]
        if any(full_path.startswith(ruta) for ruta in rutas_api):
            raise HTTPException(status_code=404, detail="API Route Not Found")
            
        index_path = os.path.join(ruta_frontend, "index.html")
        public_file = os.path.join(ruta_frontend, full_path)
        
        
        if os.path.isfile(public_file):
            return FileResponse(public_file)
            
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"estado": "Backend en línea. Frontend index.html no encontrado."}
else:
    @app.get("/")
    def read_root():
        log.info("Acceso a ruta raíz.")
        return {"estado": "Backend en línea. Frontend no compilado (usa npm run build)."}

if __name__ == "__main__":
    log.info("Iniciando servicio Backend para producción local...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
