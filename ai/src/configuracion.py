from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConfiguracionIA:
    """Parámetros centralizados del motor de visión artificial."""

    # --- Modelo YOLO ---
    ruta_modelo: str = "yolov8n.pt"
    umbral_confianza: float = 0.65
    clases_objetivo: dict = field(default_factory=lambda: {
        0: "Uniforme_superior_reglamentario",
        1: "Pantalon_oscuro",
        2: "Carnet",
    })

    # --- Cámara ---
    fuente_camara: int = 0
    ancho_frame: int = 640
    alto_frame: int = 480
    fps_objetivo: int = 20

    # --- MediaPipe (Privacidad) ---
    confianza_rostro_min: float = 0.5
    intensidad_blur: int = 99

    # --- Backend (Comunicación) ---
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
