# Proyecto Visión Artificial

Este es el repositorio maestro del sistema de monitoreo institucional basado en Visión Artificial. En este monorepo colaboramos 8 desarrolladores estructurados en 4 capas.

## Estructura del Equipo y Carpetas

- `/ai` : **Equipo IA (2 personas).** Scripts de Python con YOLOv8 y OpenCV.
- `/backend` : **Equipo Backend (2 personas).** API REST y WebSockets en Python (FastAPI). Punto de contacto central.
- `/frontend` : **Equipo Frontend (2 personas).** Aplicación SPA en React.
- `/hardware` : **Equipo Hardware (2 personas).** Firmware en C++ para Arduino que se acopla por comunicación local/Serial al Backend (o gateway).

## Reglas Globales (Vigentes para los 8 integrantes)

1. **Gestión de Entornos:** 
   - Backend e IA usan Python. Se debe crear un entorno virtual local (`python -m venv venv`) y manejar dependencias en `requirements.txt`.
   - Frontend usa Node.js, instalar dependencias con `npm install`.
2. **Control de Versiones (GitHub):**
   - No comitear directamente a `main`.
   - Crear ramas tipo `feature/nombre-del-modulo` (ej. `feature/ia-deteccion-cara`).
   - Hacer Pull Requests y solicitar code review de al menos 1 integrante de otra capa si hay cambios de interfaz (API).
3. **Manejo de Errores y Logs:**
   - Queda estrictamente prohibido usar `print()` simple para trazabilidad en producción.
   - El backend emplea una configuración en `backend/core/logger.py`. Las demás capas deben igualar este estándar visual.
   - Cualquier error crítico debe ser capturado de forma global para evitar caídas del servidor.

## Iniciar el Entorno

### 1. El Backend
```bash
cd backend
python -m venv venv
# Activar venv según OS (venv\Scripts\activate en Windows)
pip install fastapi uvicorn
python main.py
```

### 2. El Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. La IA
```bash
cd ai
# Recomendable: Compartir el venv del Backend si corren en el mismo servidor.
pip install opencv-python ultralytics
python src/app.py
```

### 4. Hardware
Cargar `hardware/firmware/main.ino` en la placa Arduino usando el IDE de Arduino y monitorear salida Serial a 9600 baudios.
