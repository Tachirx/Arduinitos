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

## [2026-06-06 09:15] - Estandarización Sistémica, UX y Paginación

**Archivos modificados:** `iniciar_sistema.bat`, `frontend/src/components/Auth/LoginView.jsx`, `frontend/src/components/Auth/RegisterView.jsx`, `backend/rutas/autenticacion.py`, `backend/rutas/eventos.py`, `.gitignore`

**Resumen Técnico:**
1. **Infraestructura (Batch):** Se mitigó un cierre súbito (crash) de la consola de Windows al eliminar paréntesis no escapados en una instrucción `echo` dentro de un bloque condicional en `iniciar_sistema.bat`.
5. **Endpoint de Estadísticas (KPIs Reales):** Se detectó un error matemático crítico introducido por la paginación donde los KPIs del frontend solo contabilizaban los elementos de la página actual. Se solucionó creando un nuevo endpoint en base de datos `GET /eventos/stats` para computar los totales diarios y absolutos de forma nativa en SQL (`count()` y `filter()`).
6. **Server-Side Filtering y JWT Estricto:** Se corrigió el equipo de frontend migrando el filtrado visual de JavaScript en el cliente a consultas reales en el backend mediante query params (`?tipo=alerta`), lo que garantiza la integridad de las búsquedas en las páginas antiguas. También se fortificó `App.jsx` para que valide el JWT consultando al backend, en lugar de revisar únicamente la fecha de caducidad.
7. **Fusión de Interfaces (Merge Frontend):** Se eliminó de manera segura la carpeta de código obsoleto (`frontend/src`) y se inyectó la nueva versión desarrollada por el equipo de diseño (originalmente en `frontend2`), conservando el árbol local de dependencias `node_modules` para evitar recargas completas. El proyecto está estandarizado, acoplado y optimizado para el despliegue.

## [2026-06-10 07:58] fix: errores de despliegue inicial (main.py y pyserial)

**Archivos modificados:** `iniciar_sistema.bat`, `backend/requirements.txt`

**Problema:** Al descargar el proyecto y ejecutar el script `iniciar_sistema.bat` desde ciertos entornos (o ejecutándolo como administrador o con doble clic desde accesos directos), el directorio de trabajo (CWD) no correspondía a la raíz del proyecto. Esto ocasionaba que la navegación a la subcarpeta `backend` fallara, resultando en que no se encontrara `main.py`. Además, la librería `pyserial` (usada en `backend/core/hardware.py` para la placa Arduino) faltaba en el `requirements.txt`.

**Solución:**
1. Se añadió el comando `cd /d "%~dp0"` al inicio de `iniciar_sistema.bat` para asegurar que siempre se posicione en el directorio donde reside el propio script, garantizando consistencia en las rutas relativas.
2. Se inyectó la dependencia `pyserial>=3.5` en `backend/requirements.txt` logrando su instalación automática al reconstruirse el entorno virtual (`venv`).

## [2026-06-10 11:47] fix: error de compilación de frontend en dashboard.css

**Archivo modificado:** `frontend/src/styles/dashboard.css`

**Problema:** El comando `npm run build` fallaba debido a un error de sintaxis reportado por `lightningcss` (`Invalid token in pseudo element: WhiteSpace`). Se identificó un bloque de propiedades huérfanas debajo del selector `.badge-live__dot` en `dashboard.css`.

**Solución:** Se corrigió el bloque CSS huérfano añadiendo el selector faltante `.badge-alert`, lo cual permitió que la compilación de Vite finalizara exitosamente. El proyecto ahora compila y está listo para producción.

## [2026-06-11 09:32] docs: documentación exhaustiva de arquitectura y capa UI/UX

**Archivo modificado:** `flujo_proyecto.md`

**Resumen Técnico:**
Se generó el artefacto de documentación técnica exhaustiva del sistema.
1. **Arquitectura y Código:** Se documentó el propósito de los archivos principales en las 4 capas del proyecto (IA, Backend, Frontend, Hardware), incluyendo esquemas de BD, lógicas de inferencia asíncrona y flujos de WebSockets.
2. **Capa UI/UX:** Se documentó el sistema visual detallando el uso de Design Tokens (paleta Navy+Gold), implementación en CSS puro del efecto Glassmorphism, fondos multicapa, sistema responsive (4 breakpoints) y el catálogo completo de micro-interacciones y animaciones.

## [2026-06-11 12:42] fix: reescritura de EstabilizadorVentana y tuning de detección a distancia

**Archivos modificados:** `ai/src/detector.py`, `ai/src/app.py`, `ai/src/configuracion.py`

**Problema:** Se reportó que el recuadro "carnet" parpadeaba o se marcaba rojo (como inexistente) a pesar de estar presente frente a la cámara. Adicionalmente, el KPI de "Accesos OK" en el frontend no aumentaba, y la detección general fallaba estrepitosamente a media/larga distancia (>2m).

**Solución Técnica:**
1. **Refactorización de Tracking Espacial:** El bug raíz residía en el `EstabilizadorVentana`, el cual promediaba el estado "global" de la escena usando `all(est.carnet)` y sobrescribiendo destructivamente todos los objetos `EstudianteDetectado` de forma masiva (afectando detecciones correctas por culpa de un solo parpadeo u otro estudiante sin carnet). Se reescribió `EstabilizadorVentana` implementando un algoritmo de *Tracking 1D* (por `centro_x`). El sistema ahora aísla historiales `deque` individuales para cada estudiante rastreado con inercia local independiente.
2. **Eventos Positivos al Backend:** En `app.py::MotorVisionIA._gestionar_alertas`, se incorporó la llamada silenciada a `self._notificador.enviar_evento` para el caso `cumple_normativa == True`. Esto finalmente provee un flujo de datos real hacia el frontend para alimentar el KPI de "Accesos OK".
3. **High-Res Inference y Clustering:** En `detector.py`, se aumentó el tamaño de inferencia YOLO de `imgsz=480` a `imgsz=640`. Se incrementó la holgura del clustering de prendas de `110px` a `160px`. Para mitigar la dificultad del modelo frente al objeto más pequeño (Carnet), se bajó selectivamente su umbral de `0.65` a `0.45` directo en `_UMBRALES_POR_CLASE`. 
4. **Respuesta Rápida:** En `configuracion.py`, se bajó la inercia temporal (`ventana_estabilizacion`) de 12 a 8, acelerando el switch verde/rojo visual del dashboard de ~400ms a ~260ms en 30FPS para una UI más "viva". Todo compilado exitosamente.

## [2026-06-11 13:06] hotfix: auto-ecualización YOLO y memoria temporal de Tracker

**Archivo modificado:** `ai/src/detector.py`

**Problema:** En entornos sumamente oscuros o a contraluz (ej. un usuario probando a oscuras), los bordes de la ropa se difuminan en las sombras impidiendo a YOLO detectar el carnet o el pantalón de manera estable, generando "falsas alertas" que parpadeaban frame a frame. Además, si YOLO quedaba momentáneamente ciego por una sombra severa (0 rostros y 0 prendas), el sistema descartaba todo rastro previo de la persona en el acto.

**Solución Técnica:**
1. **Auto-Brillo Dinámico (Computer Vision):** En `inferir()`, se implementó un sistema analítico de medición del brillo general del frame con `np.mean()`. Si el brillo cae por debajo de 85 (muy oscuro), se aplica de forma dinámica la función matemática `cv2.convertScaleAbs(alpha=1.35, beta=35)` que fuerza un mayor contraste y sube artificialmente el brillo *solo para la red YOLO*. Esto le permite "ver en la oscuridad" de manera excelente sin afectar el archivo fotográfico de evidencia original en el sistema.
2. **Memoria Temporal (Ghost Tracking):** Se actualizó drásticamente el `EstabilizadorVentana` para que los `EstudianteDetectado` de salida no provengan de la detección fresca del frame, sino de los propios "tracks" reconstruidos de memoria. Ahora, si YOLO queda ciego en un frame oscuro, el Tracker mantendrá a la persona "viva" y con su estado "suavizado" hasta por 5 frames (150ms).

## [2026-06-12 17:15] fix: optimizacion de desenfoque a distancia y estabilizacion por inclinacion

**Archivos modificados:** `ai/src/configuracion.py`, `ai/src/detector.py`, `ai/src/app.py`

**Problema:** El sistema perdía capacidad de desenfocar rostros a distancias mayores a 2 metros o múltiples rostros, y el video en vivo sufría tirones (1 cuadro fluido por cada 5 congelados). Adicionalmente, leves inclinaciones en la cámara de la laptop provocaban inestabilidad y "parpadeo" pasando a estado DENEGADO por falsos negativos repetitivos en la ventana de estabilización.

**Solución Técnica:**
1. **Detección a Larga Distancia (High-Res Blur):** Se eliminó el diezmado rígido de resolución a 1/3 en el sensor de privacidad. Se parametrizó (`escala_redimension_censor=0.60`) junto con el refinado del escaneo en pirámide (`factor_escala_rostro=1.1`), reteniendo suficientes píxeles en el cuadro para localizar rostros distantes con precisión.
2. **Streaming Fluido (Zero-Lag Blur):** Se desvinculó el cómputo de rostros de su renderizado. El hilo asíncrono (`CensorAsincrono`) ahora solo computa coordenadas de las cajas limítrofes, permitiendo al bucle principal de la aplicación aplicar el `cv2.GaussianBlur` sobre los cuadros frescos de forma síncrona, recuperando un streaming fluido real a 30 FPS.
3. **Inercia de Detección Genuina:** Se detuvo la inyección de cuadros de inferencia duplicados al historial de `EstabilizadorVentana` validando contra un nuevo rastreador `id_inferencia`. El filtro temporal ahora procesa exclusivamente datos nuevos de YOLO. Los umbrales base (`umbrales_clases`) se externalizaron a `ConfiguracionIA` para suavizar y calibrar detecciones esquinadas o anguladas con la laptop. Todo compilado exitosamente.

## [2026-06-13 07:48] feat: modernización de responsividad y streaming full-screen

**Archivos modificados:** `ai/src/configuracion.py`, `frontend/src/styles/dashboard.css`, `frontend/src/components/Dashboard/DashboardView.jsx`

**Problema:** La interfaz limitaba la experiencia de usuario: la cámara de 640x480 no era suficiente para detectar sujetos lejanos completos, no se podía visualizar la transmisión en pantalla completa, y el historial infinito forzaba un scroll hasta el fondo de la página perdiendo de vista los controles de la aplicación en monitores anchos.

**Solución Técnica:**
1. **Up-scaling Nativo del Sensor (Resolución HD):** Se subió la resolución base de captura de OpenCV (`ancho_cuadro` y `alto_cuadro`) en `configuracion.py` de `640x480` a `1280x720` (720p). Esto expande dramáticamente el rango de visión permitiendo a la IA rastrear estudiantes de cuerpo entero desde mayor distancia física sin perder precisión en el blur.
2. **Streaming Inmersivo (Fullscreen API):** Se integró un botón superpuesto de "Pantalla Completa" en los contenedores de video usando `requestFullscreen()` nativo de HTML5 a través de referencias `useRef` en React. Se acopló su diseño con CSS (`.btn-fullscreen`) logrando un escalado inteligente (`object-fit: contain`) sin distorsión geométrica de la imagen.
3. **Paginación Anclada (Flex Layout):** Se resolvió el desbordamiento infinito restringiendo la altura de la columna principal a `calc(100vh - 120px)`. Esto obliga al contenedor interno de historial a proveer barras de desplazamiento independientes, conservando anclada permanentemente la botonera de paginación a la vista del administrador.


## [2026-06-13 07:58] - Responsividad en Landing (Login, Registro, Recuperación) y Dashboard

**Archivos modificados:** `frontend/src/components/Auth/AuthContainer.jsx`, `frontend/src/components/Auth/RegisterView.jsx`, `frontend/src/styles/style.css`, `frontend/src/styles/dashboard.css`

**Resumen Técnico:**
1. **Landing Responsivo (Especificidad de ID):** Se identificó que el selector `#viewLogin` invalidaba los paddings responsivos de la clase `.view` en resoluciones pequeñas debido a la jerarquía de especificidad de CSS. Se incorporaron explícitamente overrides responsivos para `#viewLogin` en las media queries (`@media (max-width: 780px)` y `@media (max-width: 480px)`), reduciendo el padding a límites proporcionales en pantallas móviles y tablets.
2. **Footer Adaptativo:** Se removió el posicionamiento rígido inline (`position: 'absolute'`) en el componente `AuthContainer.jsx` para el pie de página. Se delegó el comportamiento a la clase `.site-footer` en `style.css`, configurándolo como absoluto centrado en escritorio, y dinámico/relativo con `margin-top` en resoluciones inferiores a 780px. Esto evita la superposición del footer sobre los botones e inputs de los formularios de registro y recuperación.
3. **Escalado del Logo:** Se modificó la regla del logo en móvil para forzar `height: auto` en lugar de `height: 100px` fijos, lo que elimina cualquier riesgo de distorsión geométrica en el escudo UNEFA.
4. **Preguntas de Seguridad Multi-línea:** En `RegisterView.jsx`, se refactorizó el sub-contenedor de preguntas y respuestas de seguridad aplicando `flexWrap: 'wrap'` junto a un ancho base flexible `flex: '1 1 200px'` en los elementos hijos. En resoluciones inferiores a 400px (móviles), los campos `<select>` e `<input>` se apilan verticalmente, garantizando una usabilidad perfecta y previniendo el desbordamiento horizontal.
5. **Dashboard en Móvil (Scroll Natural):** Se agregó una regla en `dashboard.css` dentro de la media query `@media (max-width: 768px)` para definir `.dashboard__col-left { max-height: none; }`. Esto remueve el límite de altura estricto de la columna izquierda que forzaba un scroll interno incómodo en dispositivos móviles, permitiendo al usuario scrollear de manera nativa toda la página.
