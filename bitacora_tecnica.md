# Bit√°cora T√©cnica de Desarrollo

**[2026-04-15 22:10]**
*   **Modulo:** IA ‚Äî Especificaci√≥n del Modelo
*   **Resumen T√©cnico:** Sesi√≥n de levantamiento de requerimientos para definir las clases de detecci√≥n del modelo YOLOv8. Se definieron 5 clases: `chemise_reglamentaria`, `pantalon_reglamentario`, `uniforme_deportivo`, `carnet_visible` y `rostro`. Se document√≥ la l√≥gica de cumplimiento, el pipeline de procesamiento, el sistema de roles (Super Admin + Portero/Vigilante) y los lineamientos de dataset para el Grupo A. Archivo generado: `especificacion_modelo_ia.md` (NO subir a GitHub).

**[2026-04-11 18:56]**
*   **Modulo:** Arquitectura Global
*   **Resumen T√©cnico:** Scaffolding inicializado para monorepo. Se establecieron las barreras de arquitectura entre Frontend (React), Backend (FastAPI Python), IA (YOLO) y Hardware (Arduino Serial). Se agregaron manejadores de excepciones globales y patr√≥n de Logger central en capa Backend. Proyecto listo para que los sub-equipos empiecen a clonar/trabajar.
**[2026-04-18 17:30]**
*   **Modulo:** IA / Arquitectura
*   **Resumen T√©cnico:** Alineaci√≥n del proyecto con la versi√≥n corregida del reporte de Karla Se reestructur√≥ la especificaci√≥n de IA (`especificacion_modelo_ia.md`) reduciendo clases a 3 (`Uniforme_superior_reglamentario`, `Pantalon_oscuro`, `Carnet`) e integrando MediaPipe para privacidad. Se defini√≥ la Arquitectura Dirigida por Eventos (EDA) y la estrategia de alertas multi-capa. Creado Plan de Implementaci√≥n formal para iniciar el desarrollo del motor de visi√≥n paralelo (ser√° necesario python 3.12 por compatibilidad:). 

**[2026-04-18 18:26]**
*   **Modulo:** IA ‚Äî C√≥digo Base (MVP)
*   **Resumen T√©cnico:** Entorno de desarrollo preparado (Python 3.12.10 venv en `ai/venv/`, incompatibilidad con 3.14 para mediapipe). Dependencias instaladas: ultralytics 8.4.39, mediapipe 0.10.33, torch 2.11.0+cpu, opencv 4.13, httpx 0.28.1. C√≥digo base implementado en 4 archivos modulares: `configuracion.py` (par√°metros centralizados), `detector.py` (inferencia YOLOv8n + censura MediaPipe), `alertas.py` (Filtro de Novedad + Capa Local winsound + Capa Red httpx), `app.py` (pipeline orquestador con HUD en pantalla). Imports verificados OK. Archivo `requirements.txt` generado.

**[2026-05-08 00:55]**
*   **M√≥dulo:** Backend ‚Äî Unificaci√≥n de Usuarios y Autenticaci√≥n
*   **Resumen T√©cnico:** Consolidaci√≥n de aportes de Miguel, Gladys y H√©ctor en un n√∫cleo s√≥lido. Se implement√≥ el modelo `Usuario` centralizado con identificaci√≥n por c√©dula √∫nica y soporte para 3 preguntas de seguridad. Se configur√≥ la autenticaci√≥n mediante JWT (HS256) con l√≥gica de bloqueo temporal de 15 minutos tras 5 intentos fallidos. Estructura de archivos organizada en `base_datos.py`, `modelos.py`, `core/autenticacion.py` y `rutas/`. Se estableci√≥ el entorno virtual (`venv`) con dependencias verificadas (FastAPI, SQLAlchemy, PyMySQL, bcrypt 4.0.1). Pruebas de persistencia y seguridad validadas con √©xito en SQLite/MariaDB.

**[2026-05-16 20:45]**
*   **M√≥dulo:** IA ‚Äî An√°lisis de ai-copia e Integraci√≥n
*   **Resumen T√©cnico:** Auditor√≠a t√©cnica detallada y comparativa arquitect√≥nica de `ai - copia` frente al MVP s√≠ncrono activo en `ai`. Se identificaron mejoras cr√≠ticas: ejecuci√≥n as√≠ncrona multihilo en pipeline desacoplado, muestreo adaptativo de frames, estabilizaci√≥n temporal por ventana y unificaci√≥n con clases UNEFA (`chaqueta_unefa`). Se detectaron desalineaciones cr√≠ticas de endpoint en FastAPI (`/eventos/ia` vs `/eventos/`) y falta de persistencia real de eventos en el backend. Se redact√≥ un informe t√©cnico detallado de recomendaciones de migraci√≥n.

**[2026-05-28 15:05]**
*   **M√≥dulo:** Frontend ‚Äî Autenticaci√≥n y Arquitectura
*   **Resumen T√©cnico:** Migraci√≥n exitosa de la maqueta Vanilla JS/HTML/CSS de Login hacia el entorno React (Vite) en `frontend`. Se componentiz√≥ el dise√±o en `AuthContainer`, `LoginView`, `RegisterView` y `ForgotView`, preservando fielmente los estilos Glassmorphism y la experiencia UX original. Se integr√≥ un servicio nativo (`authService.js`) conect√°ndolo con los endpoints FastAPI. Se a√±adi√≥ temporalmente respuestas *hardcodeadas* a las preguntas de seguridad del registro para viabilizar pruebas E2E. En el Backend, se inyect√≥ `CORSMiddleware` en `main.py` para permitir la comunicaci√≥n cruzada con el frontend.

**[2026-05-28 15:15]**
*   **M√≥dulo:** Integraci√≥n Sist√©mica y Frontend Dashboard
*   **Resumen T√©cnico:** Implementaci√≥n de la Fase 1 y Fase 2 de arquitectura. En hardware, se robusteci√≥ el fallback ac√∫stico nativo de Windows (`winsound`) como predeterminado ante la ausencia de Arduino, y se sincroniz√≥ el payload UART (`ACTIVAR_ALARMA`). En autenticaci√≥n, se migr√≥ el registro y recuperaci√≥n hacia un esquema interactivo din√°mico de 3 preguntas de seguridad acoplado con `GET /auth/preguntas` y `POST /auth/recuperar_clave`. Adicionalmente, se configur√≥ un gestor bidireccional WebSocket en FastAPI (`/eventos/ws`) para despachar alertas en tiempo real hacia React, integr√°ndolo en un nuevo componente `DashboardView.jsx` que incluye historial de eventos con fecha/hora y previsualizaci√≥n de evidencias fotogr√°ficas de la IA.
**[2026-05-31 12:58]**
*   **M√≥dulo:** Arquitectura Sist√©mica e Integraci√≥n (Frontend/Backend/IA)
*   **Resumen T√©cnico:** Resoluci√≥n de inconsistencias de integraci√≥n de "vibe coding". Se purg√≥ el historial Git de artefactos basura (`runs/`, `ai - copia/`, `Login/`) forzando reescritura de GitHub. En el Frontend, se implement√≥ `react-router-dom` en `App.jsx` para protecci√≥n de rutas, se configur√≥ `.env` para desvincular hardcodeo de red y se inyect√≥ el token JWT (`Authorization: Bearer`) en los endpoints del Dashboard. En Backend, se a√±adi√≥ la relaci√≥n `ForeignKey` en `EventoVision.id_usuario_validador`. En IA, se complet√≥ la l√≥gica en `EstabilizadorVentana.actualizar()` sobrescribiendo los campos din√°micamente con las proporciones suavizadas para reducir ruido temporal.

**[2026-05-31 16:48]**
*   **MÛdulo:** IA & Frontend ó Streaming HÌbrido MJPEG
*   **Resumen TÈcnico:** ImplementaciÛn de un micro-servidor de streaming de video MJPEG nativo (sin dependencias adicionales como Flask/FastAPI) embebido directamente en la capa de IA (streamer.py puerto 8001). Esto permite una **arquitectura hÌbrida**: el sistema sigue siendo guiado por eventos (eficiente) y guarda fotos de evidencias, pero el frontend ahora cuenta con un estado interactivo (erEnVivo) en React que carga una etiqueta <img> con el stream en vivo a peticiÛn del portero, mostrando el renderizado en tiempo real del HUD de diagnÛstico sin saturar el ancho de banda innecesariamente.


**[2026-05-31 23:02]**
*   **MÛdulo:** Frontend (Estilos & CompilaciÛn)
*   **Resumen TÈcnico:** CorrecciÛn de un error crÌtico de sintaxis CSS en \`frontend/src/styles/style.css\`. Se restaurÛ el selector \`.back-btn\` faltante antes de un bloque de propiedades que se encontraban huÈrfanas en la lÌnea 330, lo cual producÌa un fallo de compilaciÛn en \`lightningcss\` durante el proceso de empaquetado de Vite (\`npm run build\`). Posterior a la correcciÛn, se validÛ la compilaciÛn exitosa tanto del Frontend en Vite (React) como del Backend y el Motor de IA en Python (mediante compilaciÛn en seco \`py_compile\`), confirmando que la integridad sint·ctica de todo el sistema est· restablecida.

**[2026-05-31 23:07]**
*   **MÛdulo:** Core (Arquitectura de Fallos y Servidor)
*   **Resumen TÈcnico:** 
    1. **Resiliencia de C·mara:** Se modificÛ \`ai/src/app.py\` para operar en "modo degradado" en caso de no detectar una c·mara. En lugar de detener la ejecuciÛn, el pipeline genera sintÈticamente frames negros con un aviso de error \`ERROR: SIN SENAL DE CAMARA\` y opera a 15 FPS para ahorrar CPU. El servidor de streaming asÌncrono se mantiene online evitando caÌdas de servicio.
    2. **Fallback Visual en Frontend:** Se implementÛ en \`DashboardView.jsx\` un render de error inline basado en data-URI SVG con la estÈtica nativa de la app (evitando dependencias externas como via.placeholder.com).
    3. **Base de Datos:** Se activÛ temporalmente la base de datos de respaldo en SQLite agregando la variable \`DATABASE_URL=sqlite:///./proyecto.db\` en \`backend/.env\` debido a un error de operaciÛn y autenticaciÛn GSSAPI (\`auth_gssapi_client\`) persistente con la instancia local de MariaDB. Esto garantiza consistencia de esquema DDL mientras se evita el error 2059 de PyMySQL. Los 3 demonios (FastAPI, Vite, y Motor IA) han sido levantados localmente.

**[2026-05-31 23:11]**
*   **MÛdulo:** Core IA & Estabilidad
*   **Resumen TÈcnico:** 
    1. **EjecuciÛn Headless:** Se eliminÛ la instanciaciÛn de ventanas nativas del sistema operativo en OpenCV (\`cv2.imshow\` y \`cv2.waitKey\`) dentro de \`app.py\` para que el servicio opere 100% en segundo plano y asÌncrono, delegando toda responsabilidad de renderizado al Frontend a travÈs del \`streamer.py\`.
    2. **Fallo de Tipo JSON:** Se mitigÛ un crash severo que detenÌa el motor en el momento de detecciÛn y envÌo de un webhook (Error: \`Object of type float32 is not JSON serializable\`). Esto se solucionÛ en \`detector.py\` (LÌneas 179-184) forzando el cast de los arrays NumPy \`conf\` y \`cx\` devueltos por YOLO a tipos flotantes nativos primitivos de Python (\`float()\`) justo antes de agregarlos al payload de las alertas.

**[2026-05-31 23:15]**
*   **MÛdulo:** Core IA & Configurazione
*   **Resumen TÈcnico:** 
    Se aÒadiÛ flexibilidad a la detecciÛn de fuentes de video. En \`ai/src/configuracion.py\`, la asignaciÛn de la c·mara (\`fuente_camara\`) ahora se lee autom·ticamente a travÈs de \`os.environ.get("CAMERA_SOURCE", "0")\`. Esto mantiene la selecciÛn autom·tica del hardware predeterminado de la laptop (ID 0) por defecto, pero habilita que administradores puedan forzar una c·mara USB externa inyectando simplemente \`CAMERA_SOURCE=1\` sin necesidad de alterar el cÛdigo de producciÛn.

**[2026-05-31 23:19]**
*   **MÛdulo:** Frontend & UX (Dashboard)
*   **Resumen TÈcnico:** 
    1. **Bug de Renderizado Solapado:** Se corrigiÛ un comportamiento no deseado en \`DashboardView.jsx\` donde el renderizado de la c·mara en vivo (\`verEnVivo === true\`) prevalecÌa jer·rquicamente sobre la selecciÛn de un evento histÛrico. Ahora, al invocar \`onClick\` sobre un registro, el estado de transmisiÛn se detiene forzosamente (\`setVerEnVivo(false)\`) para priorizar la visualizaciÛn de la evidencia fotogr·fica.
    2. **IteraciÛn Sem·ntica:** Se modificÛ la jerga tÈcnica en el panel de detalle de la IA (ej. "Metadatos de la IA" -> "An·lisis de Vestimenta", "Prendas Faltantes" -> "Motivo de Alerta", "Rostros Detectados" -> "Personas en cuadro") para garantizar un lenguaje de diseÒo enfocado en la operaciÛn del usuario final (personal de porterÌa).

**[2026-05-31 23:21]**
*   **MÛdulo:** Frontend (OptimizaciÛn de Rendimiento y Memoria)
*   **Resumen TÈcnico:** 
    Se mitigÛ un riesgo latente de fuga de memoria (Memory Leak) en el DOM provocado por el flujo continuo del WebSocket. En \`DashboardView.jsx\`, se implementÛ una estrategia de truncamiento circular (\`.slice(0, 100)\`) sobre el array de estado de \`eventos\`. Esto asegura que el cliente de React en la porterÌa retenga un m·ximo de 100 nodos histÛricos en pantalla de forma rotativa, garantizando un rendimiento estable y sin lag incluso tras sesiones ininterrumpidas de operaciÛn 24/7.
