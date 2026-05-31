from __future__ import annotations

import base64
import logging
import sys
import time
from datetime import datetime, timezone
from queue import Empty, Queue
from threading import Thread

import cv2
import httpx
import numpy as np

from detector import ResultadoDeteccion

log = logging.getLogger("ia.alertas")

class FiltroNovedad:
    """Evita saturación de red emitiendo eventos solo ante cambio de estado y cooldown."""

    def __init__(self, cooldown_segundos: float = 3.0) -> None:
        self._estado_anterior: bool | None = None
        self._ultimo_envio: float = 0.0
        self._cooldown = cooldown_segundos

    def es_novedad(self, cumple_actual: bool) -> bool:
        ahora = time.monotonic()
        cambio_estado = (
            self._estado_anterior is None
            or cumple_actual != self._estado_anterior
        )
        if cambio_estado and (ahora - self._ultimo_envio) >= self._cooldown:
            self._estado_anterior = cumple_actual
            self._ultimo_envio = ahora
            return True
        return False

    def reiniciar(self) -> None:
        self._estado_anterior = None
        self._ultimo_envio = 0.0

def _emitir_beep_sistema(frecuencia: int, duracion_ms: int) -> None:
    try:
        if sys.platform == "win32":
            import winsound  # pylint: disable=import-outside-toplevel
            winsound.Beep(frecuencia, duracion_ms)
        else:
            sys.stdout.write("\a")
            sys.stdout.flush()
    except Exception:  # noqa: BLE001
        log.warning("No se pudo emitir beep (entorno sin audio).")

class AlertaSonora:
    """Capa local de alertas de latencia cero usando la API del sistema operativo."""

    def __init__(self, frecuencia: int = 1000, duracion_ms: int = 500) -> None:
        self._frecuencia = frecuencia
        self._duracion = duracion_ms
        self._activa = False

    def emitir(self) -> None:
        if not self._activa:
            self._activa = True
            Thread(target=self._reproducir, daemon=True).start()

    def _reproducir(self) -> None:
        try:
            _emitir_beep_sistema(self._frecuencia, self._duracion)
        finally:
            self._activa = False

class NotificadorBackend:
    """Capa de red que encola y transmite asíncronamente eventos al backend FastAPI."""

    def __init__(self, url_eventos: str, timeout: float = 5.0) -> None:
        self._url = url_eventos
        self._timeout = timeout
        self._cola: Queue = Queue(maxsize=10)
        self._hilo_worker = Thread(target=self._worker, daemon=True)
        self._hilo_worker.start()

    def enviar_evento(
        self, resultado: ResultadoDeteccion, frame_censurado: np.ndarray
    ) -> None:
        _, buffer = cv2.imencode(
            ".jpg", frame_censurado, [cv2.IMWRITE_JPEG_QUALITY, 70]
        )
        imagen_b64 = base64.b64encode(buffer).decode("utf-8")

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cumple_normativa": resultado.cumple_normativa,
            "clases_faltantes": self._obtener_faltantes(resultado),
            "confianzas": resultado.confianzas,
            "rostros_detectados": resultado.rostros_detectados,
            "evidencia_b64": imagen_b64,
        }

        if self._cola.full():
            try:
                self._cola.get_nowait()
            except Empty:
                pass
        self._cola.put_nowait(payload)

    def _worker(self) -> None:
        with httpx.Client(timeout=self._timeout) as cliente:
            while True:
                try:
                    payload = self._cola.get(timeout=1)
                    respuesta = cliente.post(self._url, json=payload)
                    if respuesta.status_code == 200:
                        log.info("Evento enviado al backend correctamente.")
                    else:
                        log.warning(
                            "Backend respondió con código %s",
                            respuesta.status_code,
                        )
                except Empty:
                    continue
                except httpx.ConnectError:
                    log.warning("Backend no disponible. Evento descartado.")
                except Exception as exc:  # noqa: BLE001
                    log.error("Error enviando evento: %s", exc)

    @staticmethod
    def _obtener_faltantes(resultado: ResultadoDeteccion) -> list[str]:
        faltantes = []
        if not resultado.carnet:
            faltantes.append("carnet")
        if not resultado.pantalon_oscuro:
            faltantes.append("pantalon_oscuro")
        if not resultado.uniforme_superior and not resultado.chaqueta_unefa:
            faltantes.append("uniforme_superior_o_chaqueta")
        return faltantes
