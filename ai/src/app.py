from __future__ import annotations

import logging
import os
import threading
import time
import warnings
from typing import Optional

os.environ.setdefault("NUMPY_EXPERIMENTAL_ARRAY_FUNCTION", "0")
warnings.filterwarnings("ignore", category=RuntimeWarning)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from alertas import AlertaSonora, FiltroNovedad, NotificadorBackend
from configuracion import ConfiguracionIA
from detector import (
    CensorPrivacidad,
    DetectorVestimenta,
    EstabilizadorVentana,
    ResultadoDeteccion,
)
from streamer import StreamerLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("ia.motor")

_FRAME_INTERVAL = 1.0 / 30.0

class CapturadorAsync:
    """Captura continua de frames en segundo plano para latencia cero."""

    def __init__(self, fuente: int, ancho: int, alto: int) -> None:
        self._cap = cv2.VideoCapture(fuente)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._activo = True
        self._hilo = threading.Thread(target=self._capturar, daemon=True)
        self._hilo.start()

    def _capturar(self) -> None:
        while self._activo:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
                time.sleep(0.008)
            else:
                time.sleep(0.05)

    def leer(self) -> tuple[bool, Optional[np.ndarray]]:
        with self._lock:
            if self._frame is None:
                return False, None
            return True, self._frame.copy()

    def liberar(self) -> None:
        self._activo = False
        self._hilo.join(timeout=1)
        self._cap.release()

    def esta_abierta(self) -> bool:
        return self._cap.isOpened()

class InferenciaAsync:
    """Procesamiento asíncrono del modelo YOLOv8 en segundo plano."""

    def __init__(self, detector: DetectorVestimenta) -> None:
        self._detector = detector
        self._frame_entrada: Optional[np.ndarray] = None
        self._ultimo_resultado = ResultadoDeteccion()
        self._lock_entrada = threading.Lock()
        self._lock_resultado = threading.Lock()
        self._activo = True
        self._hay_trabajo = threading.Event()
        self._hilo = threading.Thread(target=self._worker, daemon=True)
        self._hilo.start()

    def enviar_frame(self, frame: np.ndarray) -> None:
        with self._lock_entrada:
            self._frame_entrada = frame
        self._hay_trabajo.set()

    def obtener_resultado(self) -> ResultadoDeteccion:
        with self._lock_resultado:
            return self._ultimo_resultado

    def _worker(self) -> None:
        while self._activo:
            self._hay_trabajo.wait(timeout=0.5)
            self._hay_trabajo.clear()
            with self._lock_entrada:
                frame = self._frame_entrada
                self._frame_entrada = None
            if frame is not None:
                resultado = self._detector.inferir(frame)
                with self._lock_resultado:
                    self._ultimo_resultado = resultado

    def detener(self) -> None:
        self._activo = False
        self._hay_trabajo.set()
        self._hilo.join(timeout=2)

class CensorAsync:
    """Procesamiento asíncrono del difuminado de rostros por privacidad."""

    def __init__(self, censor: CensorPrivacidad) -> None:
        self._censor = censor
        self._frame_entrada: Optional[np.ndarray] = None
        self._ultimo_frame: Optional[np.ndarray] = None
        self._ultima_cantidad: int = 0
        self._lock_entrada = threading.Lock()
        self._lock_salida = threading.Lock()
        self._activo = True
        self._hay_trabajo = threading.Event()
        self._hilo = threading.Thread(target=self._worker, daemon=True)
        self._hilo.start()

    def enviar_frame(self, frame: np.ndarray) -> None:
        with self._lock_entrada:
            self._frame_entrada = frame
        self._hay_trabajo.set()

    def obtener_resultado(self) -> tuple[Optional[np.ndarray], int]:
        with self._lock_salida:
            return self._ultimo_frame, self._ultima_cantidad

    def _worker(self) -> None:
        while self._activo:
            self._hay_trabajo.wait(timeout=0.5)
            self._hay_trabajo.clear()
            with self._lock_entrada:
                frame = self._frame_entrada
                self._frame_entrada = None
            if frame is not None:
                frame_censurado, cantidad = self._censor.censurar_rostros(
                    frame, recalcular=True
                )
                with self._lock_salida:
                    self._ultimo_frame = frame_censurado
                    self._ultima_cantidad = cantidad

    def detener(self) -> None:
        self._activo = False
        self._hay_trabajo.set()
        self._hilo.join(timeout=2)

class MotorVisionIA:
    """Orquestador principal con pipeline de video asíncrono y HUD multipersona."""

    SALTO_INFERENCIA = 3
    SALTO_CENSOR = 6

    def __init__(self, config: Optional[ConfiguracionIA] = None) -> None:
        self._config = config or ConfiguracionIA()
        self._captura: Optional[CapturadorAsync] = None

        self._detector = DetectorVestimenta(
            ruta_modelo=self._config.ruta_modelo,
            umbral_confianza=self._config.umbral_confianza,
            clases_objetivo=self._config.clases_objetivo,
        )
        self._inferencia = InferenciaAsync(self._detector)

        self._censor_base = CensorPrivacidad(
            intensidad_blur=self._config.intensidad_blur,
        )
        self._censor = CensorAsync(self._censor_base)

        self._estabilizador = EstabilizadorVentana(
            ventana=self._config.ventana_estabilizacion,
            fraccion_minima=self._config.fraccion_estabilizacion,
        )
        self._filtro = FiltroNovedad(
            cooldown_segundos=self._config.cooldown_alerta_seg,
        )
        self._alerta_sonora = AlertaSonora(
            frecuencia=self._config.frecuencia_beep,
            duracion_ms=self._config.duracion_beep_ms,
        )
        self._notificador = NotificadorBackend(
            url_eventos=self._config.url_completa_eventos,
            timeout=self._config.timeout_conexion,
        )
        self._streamer = StreamerLocal(puerto=8001)

        self._ultimo_frame_censurado: Optional[np.ndarray] = None
        self._contador_frames = 0
        self._fps = 0.0
        self._contador_fps = 0
        self._tiempo_fps = time.monotonic()

        log.info("Motor de Visión IA inicializado correctamente.")

    def iniciar(self) -> None:
        self._captura = CapturadorAsync(
            fuente=self._config.fuente_camara,
            ancho=self._config.ancho_frame,
            alto=self._config.alto_frame,
        )

        if not self._captura.esta_abierta():
            log.error(
                "No se pudo abrir la cámara (fuente: %d).",
                self._config.fuente_camara,
            )
            return

        self._streamer.iniciar()
        log.info("Pipeline de video iniciado. Presiona 'q' para detener.")

        try:
            self._bucle_principal()
        except KeyboardInterrupt:
            log.info("Interrupción por teclado detectada.")
        except Exception as exc:  # noqa: BLE001
            log.error("Error crítico en el pipeline: %s", exc, exc_info=True)
        finally:
            self._liberar_recursos()

    def _bucle_principal(self) -> None:
        while True:
            t_inicio = time.monotonic()

            ret, frame = self._captura.leer()
            if not ret or frame is None:
                time.sleep(0.002)
                continue

            self._contador_frames += 1

            if self._contador_frames % self.SALTO_INFERENCIA == 0:
                self._inferencia.enviar_frame(frame)

            if self._contador_frames % self.SALTO_CENSOR == 0:
                self._censor.enviar_frame(frame)

            frame_censurado, cantidad_rostros = self._censor.obtener_resultado()
            if frame_censurado is None:
                frame_censurado = frame

            self._ultimo_frame_censurado = frame_censurado

            resultado_crudo = self._inferencia.obtener_resultado()
            resultado_crudo.rostros_detectados = cantidad_rostros
            resultado = self._estabilizador.actualizar(resultado_crudo)

            ahora = time.monotonic()
            self._contador_fps += 1
            transcurrido_fps = ahora - self._tiempo_fps
            if transcurrido_fps >= 1.0:
                self._fps = self._contador_fps / transcurrido_fps
                self._contador_fps = 0
                self._tiempo_fps = ahora

            frame_renderizado = self._dibujar_hud(frame_censurado, resultado, self._fps)
            self._gestionar_alertas(resultado, frame_censurado)

            self._streamer.actualizar_frame(frame_renderizado)

            cv2.imshow("UNEFA - Sistema de Validacion de Vestimenta", frame_renderizado)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                log.info("Detenido por el usuario (tecla 'q').")
                break

            transcurrido = time.monotonic() - t_inicio
            tiempo_restante = _FRAME_INTERVAL - transcurrido
            if tiempo_restante > 0.001:
                time.sleep(tiempo_restante)
            else:
                time.sleep(0.001)

    def _gestionar_alertas(
        self, resultado: ResultadoDeteccion, frame_censurado: np.ndarray
    ) -> None:
        if not self._filtro.es_novedad(resultado.cumple_normativa):
            return
        if not resultado.cumple_normativa:
            self._alerta_sonora.emitir()
            self._notificador.enviar_evento(resultado, frame_censurado)
            log.info(
                "ALERTA: Escena con incumplimiento detectado. Notificación enviada."
            )
        else:
            log.info("Estado: Cumplimiento verificado globalmente.")

    def _dibujar_hud(
        self,
        frame: np.ndarray,
        resultado: ResultadoDeteccion,
        fps: float = 0.0,
    ) -> np.ndarray:
        try:
            if frame is None or frame.size == 0:
                return np.zeros((480, 640, 3), dtype=np.uint8)

            frame_hud = frame.copy()
            alto, ancho = frame_hud.shape[:2]

            # 1. Dibujar panel de diagnóstico general en la esquina superior izquierda
            cant_estudiantes = len(resultado.estudiantes)
            ancho_panel, alto_panel = 230, 75
            px1, py1 = 15, 15
            px2, py2 = px1 + ancho_panel, py1 + alto_panel

            overlay = frame_hud.copy()
            cv2.rectangle(overlay, (px1, py1), (px2, py2), (14, 14, 14), -1)
            cv2.addWeighted(overlay, 0.70, frame_hud, 0.30, 0, frame_hud)

            estado_global = resultado.cumple_normativa
            color_global = (45, 160, 45) if estado_global else (30, 30, 200)
            cv2.rectangle(frame_hud, (px1, py1), (px2, py1 + 25), color_global, -1)
            
            titulo = " MONITOREO MULTIPERSONA"
            cv2.putText(
                frame_hud, titulo, (px1 + 5, py1 + 18),
                cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1
            )
            
            txt_diag = f"Estudiantes en escena: {cant_estudiantes}"
            cv2.putText(
                frame_hud, txt_diag, (px1 + 10, py1 + 45),
                cv2.FONT_HERSHEY_DUPLEX, 0.4, (220, 220, 220), 1
            )
            
            txt_estado = f"Estado General: {'OK' if estado_global else 'ALERTA'}"
            cv2.putText(
                frame_hud, txt_estado, (px1 + 10, py1 + 63),
                cv2.FONT_HERSHEY_DUPLEX, 0.4, (150, 255, 150) if estado_global else (120, 120, 255), 1
            )

            # 2. Dibujar cajas envolventes y etiquetas flotantes individuales
            for i, est in enumerate(resultado.estudiantes):
                color = (45, 160, 45) if est.cumple_normativa else (30, 30, 200)
                
                # Bounding box envolvente de la persona
                cv2.rectangle(frame_hud, (est.x1, est.y1), (est.x2, est.y2), color, 2)

                # Construir etiqueta individual
                if est.cumple_normativa:
                    msg = f"E{i+1}: ACCESO PERMITIDO"
                else:
                    faltantes = []
                    if not est.uniforme_superior and not est.chaqueta_unefa:
                        faltantes.append("Uniforme")
                    if not est.pantalon_oscuro:
                        faltantes.append("Pantalon")
                    if not est.carnet:
                        faltantes.append("Carnet")
                    msg = f"E{i+1}: DENEGADO - Faltantes: {', '.join(faltantes)}"

                # Dibujar fondo de la etiqueta flotante sobre su cabeza
                lbl_y = max(18, est.y1 - 10)
                lbl_x = max(10, est.x1)
                
                # Ajustar tamaño del fondo de etiqueta según texto
                (lbl_w, lbl_h), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_DUPLEX, 0.38, 1)
                cv2.rectangle(
                    frame_hud, 
                    (lbl_x - 3, lbl_y - lbl_h - 4), 
                    (lbl_x + lbl_w + 3, lbl_y + 3), 
                    color, 
                    -1
                )
                cv2.putText(
                    frame_hud, msg, (lbl_x, lbl_y),
                    cv2.FONT_HERSHEY_DUPLEX, 0.38, (255, 255, 255), 1
                )

            # 3. Dibujar indicador de FPS
            cv2.putText(
                frame_hud, f"{fps:.1f} FPS", (ancho - 75, alto - 15),
                cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 185, 255), 1,
            )
            return frame_hud
        except Exception as exc:  # noqa: BLE001
            log.error("Error al dibujar HUD: %s", exc)
            return frame

    @staticmethod
    def _obtener_resumen_faltantes(resultado: ResultadoDeteccion) -> str:
        faltantes = []
        if not resultado.uniforme_superior:
            faltantes.append("Uniforme")
        if not resultado.pantalon_oscuro:
            faltantes.append("Pantalon")
        if not resultado.carnet:
            faltantes.append("Carnet")
        return ", ".join(faltantes) if faltantes else "Ninguno"

    def _liberar_recursos(self) -> None:
        if self._captura:
            self._captura.liberar()
        self._inferencia.detener()
        self._censor.detener()
        if hasattr(self, '_streamer'):
            self._streamer.detener()
        cv2.destroyAllWindows()
        log.info("Recursos liberados correctamente.")

if __name__ == "__main__":
    configuracion = ConfiguracionIA()
    motor = MotorVisionIA(configuracion)
    motor.iniciar()
