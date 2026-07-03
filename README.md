# Proyecto Visión Artificial

Este es el repositorio maestro del sistema de monitoreo institucional basado en Visión Artificial. En este monorepo colaboramos 8 desarrolladores estructurados en 4 capas.

## Estructura de Equipos y Responsabilidades (Monorepo)

- `/ai` : **GRUPO A (IA) - Karla, Alexandra, Tachiro.** Gestión, programación, modelo de IA (YOLOv8) e inferencia. TODO lo relacionado a la IA es exclusivo de este grupo.
- `/frontend` : **GRUPO B (Frontend) - Julián, Iván, Tachiro.** UI, paleta de colores y UX/UI para visualizar el trabajo de IA y Backend.
- `/backend` : **GRUPO C (Backend) - Gladys, Miguel, Tachiro.** BD (MariaDB), API, lógica de negocio, manejo de errores, logs obligatorios, y el Login de porteros (n8n API puente).
- `/hardware` : **GRUPO D (Hardware) - Hector, Tachiro.** Arduino, buzzer, conexiones físicas y validación de viabilidad de software en la placa.

## Reglas Globales y de Trabajo en Equipo (¡ESTRICTO!)

1. **Nomenclaturas:** Mantenimiento obligatorio de nomenclaturas. **SIEMPRE usarán `snake_case`.**
2. **Calidad de Código:** No se aceptarán placeholders ni comentarios genéricos. Si el bloque de código se entiende a simple vista (Self-Documenting Code), NO deberá ser explicado.
3. **Rol de IAs (Gemini, Claude, ChatGPT):** Prohibido copiar y pegar código sin haberlo leído línea a línea o haberlo debugeado. Obligatorio usar los modelos top tier.
4. **Flujo de Código (Git):**
   - Uso obligatorio de **GitHub Desktop**.
   - Prohibido hacer push directo a main. Todos los cambios se suben a la plataforma mediante repositorios/ramas.
   - **Nadie fusiona nada** hasta que Tachiro revise y haga el *Code Review*.
5. **División de Responsabilidades (No tocar):** El GRUPO A no tocará nada del GRUPO B sin permiso y argumentos, y así sucesivamente para todos. El Backend diseña la arquitectura, Frontend se basa en él, y encima va la IA.
6. **Integraciones:** Se debe crear cuenta en **n8n** (Tachiro) para gestión de flujos.
7. **Tiempos:** Límite por módulo de 2 a 3 días. El trabajo es equitativo (50/50 por módulo).

## Arranque Rápido (Windows)

Para iniciar todo el sistema con un solo clic (compilación de React, creación de entornos virtuales y arranque de servicios), ejecuta desde la raíz:

```cmd
iniciar_sistema.bat
```
El sistema abrirá automáticamente las ventanas de servicio y estará disponible en `http://localhost:8000`.

---

## Ejecución Manual por Módulos

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

### 3. Motor de Inteligencia Artificial (YOLOv8 + MediaPipe)
```bash
cd ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

### 4. Hardware (Arduino)
Carga el archivo `hardware/firmware/main.ino` en la placa usando el IDE de Arduino. El microcontrolador se comunicará con el Backend a 9600 baudios por el puerto Serial configurado.

