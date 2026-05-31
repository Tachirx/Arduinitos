from __future__ import annotations
import os
from dataclasses import dataclass, field

@dataclass
class ConfiguracionIA:
    """Parámetros centralizados del motor de visión artificial asíncrono."""

    # --- Modelo YOLO ---
    BASE_DIR: str = field(
        default_factory=lambda: os.path.dirname(os.path.abspath(__file__))
    )

    ruta_modelo: str = "" 
    umbral_confianza: float = 0.65
    clases_objetivo: dict = field(
        default_factory=lambda: {
            0: "carnet",
            1: "chaqueta_unefa",
            2: "pantalon_oscuro",
            3: "uniforme_superior",
        }
    )

    def __post_init__(self) -> None:
        if not self.ruta_modelo:
            self.ruta_modelo = os.path.abspath(
                os.path.join(self.BASE_DIR, "..", "best.pt")
            )

    # --- Cámara ---
    fuente_camara: int = 0
    ancho_frame: int = 640
    alto_frame: int = 480
    fps_objetivo: int = 30

    # --- Privacidad y Rendimiento ---
    confianza_rostro_min: float = 0.70
    intensidad_blur: int = 99
    salto_inferencia: int = 3
    salto_censor: int = 6
    workers_yolo: int = 0
    ventana_estabilizacion: int = 12
    fraccion_estabilizacion: float = 0.55

    # --- Backend ---
    url_backend: str = "http://localhost:8000"
    endpoint_eventos: str = "/eventos/ia"
    timeout_conexion: float = 5.0

    # --- Alertas Locales ---
    frecuencia_beep: int = 1000
    duracion_beep_ms: int = 500
    cooldown_alerta_seg: float = 3.0 

    @property
    def url_completa_eventos(self) -> str:
        return f"{self.url_backend}{self.endpoint_eventos}"

    def validar(self) -> None:
        if not os.path.isfile(self.ruta_modelo):
            raise FileNotFoundError(
                f"Modelo no encontrado en: {self.ruta_modelo}"
            )
