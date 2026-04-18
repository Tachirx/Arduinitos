import base64
import logging
import time
import winsound
from datetime import datetime, timezone
from threading import Thread

import cv2
import httpx
import numpy as np

from detector import ResultadoDeteccion

log = logging.getLogger("ia.alertas")


class FiltroNovedad:
    """Evita saturación de red emitiendo eventos solo ante cambio de estado."""

    def __init__(self, cooldown_segundos: float = 3.0):
        self._estado_anterior: bool | None = None
        self._ultimo_envio: float = 0.0
        self._cooldown = cooldown_segundos

    def es_novedad(self, cumple_actual: bool) -> bool:
        ahora = time.monotonic()
        cambio_estado = self._estado_anterior is None or cumple_actual != self._estado_anterior

        if cambio_estado and (ahora - self._ultimo_envio) >= self._cooldown:
            self._estado_anterior = cumple_actual
            self._ultimo_envio = ahora
            return True
        return False

    def reiniciar(self):
        self._estado_anterior = None
        self._ultimo_envio = 0.0


class AlertaSonora:
    """Capa 1: Alerta local de latencia cero usando Windows API."""

    def __init__(self, frecuencia: int = 1000, duracion_ms: int = 500):
        self._frecuencia = frecuencia
        self._duracion = duracion_ms
        self._activa = False

    def emitir(self):
        if not self._activa:
            self._activa = True
            hilo = Thread(target=self._reproducir, daemon=True)
            hilo.start()

    def _reproducir(self):
        try:
            winsound.Beep(self._frecuencia, self._duracion)
        except RuntimeError:
            log.warning("No se pudo emitir beep (entorno sin audio).")
        finally:
            self._activa = False


class NotificadorBackend:
    """Capa 2: Envío asíncrono de eventos al Backend FastAPI."""

    def __init__(self, url_eventos: str, timeout: float = 5.0):
        self._url = url_eventos
        self._timeout = timeout

    def enviar_evento(
        self,
        resultado: ResultadoDeteccion,
        frame_censurado: np.ndarray,
    ):
        hilo = Thread(
            target=self._enviar_async,
            args=(resultado, frame_censurado),
            daemon=True,
        )
        hilo.start()

    def _enviar_async(self, resultado: ResultadoDeteccion, frame: np.ndarray):
        try:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            imagen_b64 = base64.b64encode(buffer).decode("utf-8")

            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cumple_normativa": resultado.cumple_normativa,
                "clases_faltantes": self._obtener_faltantes(resultado),
                "confianzas": resultado.confianzas,
                "rostros_detectados": resultado.rostros_detectados,
                "evidencia_b64": imagen_b64,
            }

            with httpx.Client(timeout=self._timeout) as cliente:
                respuesta = cliente.post(self._url, json=payload)
                if respuesta.status_code == 200:
                    log.info("Evento enviado al Backend correctamente.")
                else:
                    log.warning(f"Backend respondió con código {respuesta.status_code}")

        except httpx.ConnectError:
            log.warning("Backend no disponible. Evento descartado (Capa Local sigue activa).")
        except Exception as exc:
            log.error(f"Error enviando evento al Backend: {exc}")

    @staticmethod
    def _obtener_faltantes(resultado: ResultadoDeteccion) -> list[str]:
        faltantes = []
        if not resultado.uniforme_superior:
            faltantes.append("Uniforme_superior_reglamentario")
        if not resultado.pantalon_oscuro:
            faltantes.append("Pantalon_oscuro")
        if not resultado.carnet:
            faltantes.append("Carnet")
        return faltantes
