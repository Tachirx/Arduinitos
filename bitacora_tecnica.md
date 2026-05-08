# Bitácora Técnica de Desarrollo

**[2026-04-15 22:10]**
*   **Modulo:** IA — Especificación del Modelo
*   **Resumen Técnico:** Sesión de levantamiento de requerimientos para definir las clases de detección del modelo YOLOv8. Se definieron 5 clases: `chemise_reglamentaria`, `pantalon_reglamentario`, `uniforme_deportivo`, `carnet_visible` y `rostro`. Se documentó la lógica de cumplimiento, el pipeline de procesamiento, el sistema de roles (Super Admin + Portero/Vigilante) y los lineamientos de dataset para el Grupo A. Archivo generado: `especificacion_modelo_ia.md` (NO subir a GitHub).

**[2026-04-11 18:56]**
*   **Modulo:** Arquitectura Global
*   **Resumen Técnico:** Scaffolding inicializado para monorepo. Se establecieron las barreras de arquitectura entre Frontend (React), Backend (FastAPI Python), IA (YOLO) y Hardware (Arduino Serial). Se agregaron manejadores de excepciones globales y patrón de Logger central en capa Backend. Proyecto listo para que los sub-equipos empiecen a clonar/trabajar.
**[2026-04-18 17:30]**
*   **Modulo:** IA / Arquitectura
*   **Resumen Técnico:** Alineación del proyecto con la versión corregida del reporte de Karla Se reestructuró la especificación de IA (`especificacion_modelo_ia.md`) reduciendo clases a 3 (`Uniforme_superior_reglamentario`, `Pantalon_oscuro`, `Carnet`) e integrando MediaPipe para privacidad. Se definió la Arquitectura Dirigida por Eventos (EDA) y la estrategia de alertas multi-capa. Creado Plan de Implementación formal para iniciar el desarrollo del motor de visión paralelo (será necesario python 3.12 por compatibilidad:). 

**[2026-04-18 18:26]**
*   **Modulo:** IA — Código Base (MVP)
*   **Resumen Técnico:** Entorno de desarrollo preparado (Python 3.12.10 venv en `ai/venv/`, incompatibilidad con 3.14 para mediapipe). Dependencias instaladas: ultralytics 8.4.39, mediapipe 0.10.33, torch 2.11.0+cpu, opencv 4.13, httpx 0.28.1. Código base implementado en 4 archivos modulares: `configuracion.py` (parámetros centralizados), `detector.py` (inferencia YOLOv8n + censura MediaPipe), `alertas.py` (Filtro de Novedad + Capa Local winsound + Capa Red httpx), `app.py` (pipeline orquestador con HUD en pantalla). Imports verificados OK. Archivo `requirements.txt` generado.

**[2026-05-08 00:55]**
*   **Módulo:** Backend — Unificación de Usuarios y Autenticación
*   **Resumen Técnico:** Consolidación de aportes de Miguel, Gladys y Héctor en un núcleo sólido. Se implementó el modelo `Usuario` centralizado con identificación por cédula única y soporte para 3 preguntas de seguridad. Se configuró la autenticación mediante JWT (HS256) con lógica de bloqueo temporal de 15 minutos tras 5 intentos fallidos. Estructura de archivos organizada en `base_datos.py`, `modelos.py`, `core/autenticacion.py` y `rutas/`. Se estableció el entorno virtual (`venv`) con dependencias verificadas (FastAPI, SQLAlchemy, PyMySQL, bcrypt 4.0.1). Pruebas de persistencia y seguridad validadas con éxito en SQLite/MariaDB.

