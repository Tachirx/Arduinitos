# Bitácora Técnica

**[2026-05-28 15:15]**
*   **Módulo:** Integración Sistémica y Frontend Dashboard
*   **Resumen Técnico:** Implementación de la Fase 1 y Fase 2 de arquitectura. En hardware, se robusteció el fallback acústico nativo de Windows (`winsound`) como predeterminado ante la ausencia de Arduino, y se sincronizó el payload UART (`ACTIVAR_ALARMA`). En autenticación, se migró el registro y recuperación hacia un esquema interactivo dinámico de 3 preguntas de seguridad acoplado con `GET /auth/preguntas` y `POST /auth/recuperar_clave`. Adicionalmente, se configuró un gestor bidireccional WebSocket en FastAPI (`/eventos/ws`) para despachar alertas en tiempo real hacia React, integrándolo en un nuevo componente `DashboardView.jsx` que incluye historial de eventos con fecha/hora y previsualización de evidencias fotográficas de la IA.
**[2026-05-31 12:58]**
*   **Módulo:** Arquitectura Sistémica e Integración (Frontend/Backend/IA)
*   **Resumen Técnico:** Resolución de inconsistencias de integración de "vibe coding". Se purgó el historial Git de artefactos basura (`runs/`, `ai - copia/`, `Login/`) forzando reescritura de GitHub. En el Frontend, se implementó `react-router-dom` en `App.jsx` para protección de rutas, se configuró `.env` para desvincular hardcodeo de red y se inyectó el token JWT (`Authorization: Bearer`) en los endpoints del Dashboard. En Backend, se añadió la relación `ForeignKey` en `EventoVision.id_usuario_validador`. En IA, se completó la lógica en `EstabilizadorVentana.actualizar()` sobrescribiendo los campos dinámicamente con las proporciones suavizadas para reducir ruido temporal.

**[2026-05-31 16:48]**
*   **Módulo:** IA & Frontend - Streaming Híbrido MJPEG
*   **Resumen Técnico:** Implementación de un micro-servidor de streaming de video MJPEG nativo (sin dependencias adicionales como Flask/FastAPI) embebido directamente en la capa de IA (streamer.py puerto 8001). Esto permite una **arquitectura híbrida**: el sistema sigue siendo guiado por eventos (eficiente) y guarda fotos de evidencias, pero el frontend ahora cuenta con un estado interactivo (verEnVivo) en React que carga una etiqueta <img> con el stream en vivo a petición del portero, mostrando el renderizado en tiempo real del HUD de diagnóstico sin saturar el ancho de banda innecesariamente.


**[2026-05-31 23:02]**
*   **Módulo:** Frontend (Estilos & Compilación)
*   **Resumen Técnico:** Corrección de un error crítico de sintaxis CSS en `frontend/src/styles/style.css`. Se restauró el selector `.back-btn` faltante antes de un bloque de propiedades que se encontraban huérfanas en la línea 330, lo cual producía un fallo de compilación en `lightningcss` durante el proceso de empaquetado de Vite (`npm run build`). Posterior a la corrección, se validó la compilación exitosa tanto del Frontend en Vite (React) como del Backend y el Motor de IA en Python (mediante compilación en seco `py_compile`), confirmando que la integridad sintáctica de todo el sistema está restablecida.

**[2026-05-31 23:07]**
*   **Módulo:** Core (Arquitectura de Fallos y Servidor)
*   **Resumen Técnico:**
    1. **Resiliencia de Cámara:** Se modificó `ai/src/app.py` para operar en "modo degradado" en caso de no detectar una cámara. En lugar de detener la ejecución, el pipeline genera sintéticamente frames negros con un aviso de error `ERROR: SIN SENAL DE CAMARA` y opera a 15 FPS para ahorrar CPU. El servidor de streaming asíncrono se mantiene online evitando caídas de servicio.
    2. **Fallback Visual en Frontend:** Se implementó en `DashboardView.jsx` un render de error inline basado en data-URI SVG con la estética nativa de la app (evitando dependencias externas como via.placeholder.com).
    3. **Base de Datos:** Se activó temporalmente la base de datos de respaldo en SQLite agregando la variable `DATABASE_URL=sqlite:///./proyecto.db` en `backend/.env` debido a un error de operación y autenticación GSSAPI (`auth_gssapi_client`) persistente con la instancia local de MariaDB. Esto garantiza consistencia de esquema DDL mientras se evita el error 2059 de PyMySQL. Los 3 demonios (FastAPI, Vite, y Motor IA) han sido levantados localmente.

**[2026-05-31 23:11]**
*   **Módulo:** Core IA & Estabilidad
*   **Resumen Técnico:**
    1. **Ejecución Headless:** Se eliminó la instanciación de ventanas nativas del sistema operativo en OpenCV (`cv2.imshow` y `cv2.waitKey`) dentro de `app.py` para que el servicio opere 100% en segundo plano y asíncrono, delegando toda responsabilidad de renderizado al Frontend a través del `streamer.py`.
    2. **Fallo de Tipo JSON:** Se mitigó un crash severo que detenía el motor en el momento de detección y envío de un webhook (Error: `Object of type float32 is not JSON serializable`). Esto se solucionó en `detector.py` (Líneas 179-184) forzando el cast de los arrays NumPy `conf` y `cx` devueltos por YOLO a tipos flotantes nativos primitivos de Python (`float()`) justo antes de agregarlos al payload de las alertas.

**[2026-05-31 23:15]**
*   **Módulo:** Core IA & Configuración
*   **Resumen Técnico:**
    Se añadió flexibilidad a la detección de fuentes de video. En `ai/src/configuracion.py`, la asignación de la cámara (`fuente_camara`) ahora se lee automáticamente a través de `os.environ.get("CAMERA_SOURCE", "0")`. Esto mantiene la selección automática del hardware predeterminado de la laptop (ID 0) por defecto, pero habilita que administradores puedan forzar una cámara USB externa inyectando simplemente `CAMERA_SOURCE=1` sin necesidad de alterar el código de producción.

**[2026-05-31 23:19]**
*   **Módulo:** Frontend & UX (Dashboard)
*   **Resumen Técnico:**
    1. **Bug de Renderizado Solapado:** Se corrigió un comportamiento no deseado en `DashboardView.jsx` donde el renderizado de la cámara en vivo (`verEnVivo === true`) prevalecía jerárquicamente sobre la selección de un evento histórico. Ahora, al invocar `onClick` sobre un registro, el estado de transmisión se detiene forzosamente (`setVerEnVivo(false)`) para priorizar la visualización de la evidencia fotográfica.
    2. **Iteración Semántica:** Se modificó la jerga técnica en el panel de detalle de la IA (ej. "Metadatos de la IA" -> "Análisis de Vestimenta", "Prendas Faltantes" -> "Motivo de Alerta", "Rostros Detectados" -> "Personas en cuadro") para garantizar un lenguaje de diseño enfocado en la operación del usuario final (personal de portería).

**[2026-05-31 23:21]**
*   **Módulo:** Frontend (Optimización de Rendimiento y Memoria)
*   **Resumen Técnico:**
    Se mitigó un riesgo latente de fuga de memoria (Memory Leak) en el DOM provocado por el flujo continuo del WebSocket. En `DashboardView.jsx`, se implementó una estrategia de truncamiento circular (`.slice(0, 100)`) sobre el array de estado de `eventos`. Esto asegura que el cliente de React en la portería retenga un máximo de 100 nodos históricos en pantalla de forma rotativa, garantizando un rendimiento estable y sin lag incluso tras sesiones ininterrumpidas de operación 24/7.


## [2026-06-02 15:40] - Despliegue Local Single-PC
- Se refactorizó main.py del backend para servir los estáticos de Vite (dist), unificando todo en un solo puerto y eliminando el problema de CORS.
- Se creó el script de orquestación local iniciar_sistema.bat para automatizar la inicialización.
- Se validó la ejecución headless del módulo IA (StreamerLocal en puerto 8001).

## [2026-06-05 22:27] fix: login fallaba por prefijo "V-" en cédula

**Archivo modificado:** `frontend/src/components/Auth/LoginView.jsx`

**Problema:** El formulario de registro limpiaba el prefijo `V-` de la cédula antes de enviarla al backend (`cedula.replace('V-', '')`), guardándola como `12345678`. El formulario de login NO hacía este limpiado y enviaba `V-12345678`. El backend buscaba la cédula tal cual en la BD, no la encontraba, y retornaba "Cédula o clave incorrecta".

**Solución:** Se agregó `cedula.replace('V-', '').replace('v-', '')` en el handler de login antes de llamar al servicio de autenticación. Frontend recompilado.

## [2026-06-05 23:58] - Autoconfiguración y Validación de Entornos Virtuales (VENV)

**Archivo modificado:** `iniciar_sistema.bat`

**Problema:** Al ejecutar el sistema en entornos locales limpios o con copias directas de directorios virtuales (`venv`), los scripts de activación fallaban debido a rutas absolutas hardcodeadas en los scripts internos (ej. `activate.bat` apuntando a directorios inexistentes de otra máquina). Esto obligaba al script de lote a usar un Python global que usualmente carecía de dependencias esenciales (como FastAPI o Ultralytics).

**Solución:**
1. Se integró una validación previa en `iniciar_sistema.bat` que confirma la existencia de Python en el PATH global.
2. Se diseñó un flujo de saneamiento robusto con etiquetas `goto`. Si el entorno virtual de `ai/` o `backend/` no existe, o si la ejecución de prueba del intérprete local `venv\Scripts\python.exe` falla (confirmando que el entorno está corrupto, movido de directorio o copiado de otra computadora), el script elimina recursivamente el directorio `venv` roto.
3. Se crea automáticamente el entorno virtual nativo local (`python -m venv venv`) y se instalan/actualizan de forma transparente las dependencias listadas en los respectivos archivos `requirements.txt`.
4. Con esto, el sistema se autoconfigura al 100% en la máquina del desarrollador local sin necesidad de configuraciones previas manuales.
