import cv2
import logging
import time
from typing import Optional

from configuracion import ConfiguracionIA
from detector import DetectorVestimenta, CensorPrivacidad, ResultadoDeteccion
from alertas import FiltroNovedad, AlertaSonora, NotificadorBackend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("ia.motor")


class MotorVisionIA:
    """Pipeline principal: Captura → Inferencia Paralela → Censura → Alerta."""

    def __init__(self, config: Optional[ConfiguracionIA] = None):
        self._config = config or ConfiguracionIA()
        self._captura: Optional[cv2.VideoCapture] = None

        self._detector = DetectorVestimenta(
            ruta_modelo=self._config.ruta_modelo,
            umbral_confianza=self._config.umbral_confianza,
            clases_objetivo=self._config.clases_objetivo,
        )
        self._censor = CensorPrivacidad(
            confianza_minima=self._config.confianza_rostro_min,
            intensidad_blur=self._config.intensidad_blur,
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

        log.info("Motor de Visión IA inicializado correctamente.")

    def iniciar(self):
        self._captura = cv2.VideoCapture(self._config.fuente_camara)

        if not self._captura.isOpened():
            log.error(f"No se pudo abrir la cámara (fuente: {self._config.fuente_camara}).")
            return

        self._captura.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.ancho_frame)
        self._captura.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.alto_frame)

        log.info("Pipeline de video iniciado. Presiona 'q' para detener.")

        try:
            while True:
                ret, frame = self._captura.read()
                if not ret:
                    log.warning("Frame no capturado, reintentando...")
                    time.sleep(0.05)
                    continue

                resultado = self._detector.inferir(frame)

                frame_censurado, cantidad_rostros = self._censor.censurar_rostros(frame)
                resultado.rostros_detectados = cantidad_rostros

                frame_renderizado = self._dibujar_hud(frame_censurado, resultado)

                self._gestionar_alertas(resultado, frame_censurado)

                cv2.imshow("UNEFA - Monitor de Vestimenta", frame_renderizado)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    log.info("Detenido por el usuario (tecla 'q').")
                    break

        except KeyboardInterrupt:
            log.info("Interrupción por teclado detectada.")
        except Exception as exc:
            log.error(f"Error crítico en el pipeline: {exc}", exc_info=True)
        finally:
            self._liberar_recursos()

    def _gestionar_alertas(self, resultado: ResultadoDeteccion, frame_censurado):
        if not self._filtro.es_novedad(resultado.cumple_normativa):
            return

        if not resultado.cumple_normativa:
            self._alerta_sonora.emitir()
            self._notificador.enviar_evento(resultado, frame_censurado)
            log.info(f"ALERTA: Incumplimiento detectado | Faltantes: {self._obtener_resumen_faltantes(resultado)}")
        else:
            log.info("Estado: Cumplimiento verificado.")

    def _dibujar_hud(self, frame, resultado: ResultadoDeteccion):
        frame_hud = frame.copy()
        alto, ancho, _ = frame_hud.shape

        color = (0, 200, 0) if resultado.cumple_normativa else (0, 0, 220)
        texto_estado = "CUMPLE" if resultado.cumple_normativa else "NO CUMPLE"

        cv2.rectangle(frame_hud, (10, 10), (300, 130), (0, 0, 0), -1)
        cv2.rectangle(frame_hud, (10, 10), (300, 130), color, 2)

        cv2.putText(frame_hud, texto_estado, (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        items = [
            ("Uniforme", resultado.uniforme_superior),
            ("Pantalon", resultado.pantalon_oscuro),
            ("Carnet", resultado.carnet),
        ]
        y_offset = 70
        for nombre, presente in items:
            icono = "[OK]" if presente else "[  ]"
            color_item = (0, 200, 0) if presente else (0, 0, 200)
            cv2.putText(frame_hud, f"{icono} {nombre}", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_item, 1)
            y_offset += 22

        return frame_hud

    @staticmethod
    def _obtener_resumen_faltantes(resultado: ResultadoDeteccion) -> str:
        faltantes = []
        if not resultado.uniforme_superior:
            faltantes.append("Uniforme")
        if not resultado.pantalon_oscuro:
            faltantes.append("Pantalón")
        if not resultado.carnet:
            faltantes.append("Carnet")
        return ", ".join(faltantes) if faltantes else "Ninguno"

    def _liberar_recursos(self):
        if self._captura:
            self._captura.release()
        cv2.destroyAllWindows()
        self._censor.liberar()
        self._filtro.reiniciar()
        log.info("Recursos del motor IA liberados.")


if __name__ == "__main__":
    configuracion = ConfiguracionIA()
    motor = MotorVisionIA(configuracion)
    motor.iniciar()
