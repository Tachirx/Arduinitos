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
    umbrales_clases: dict[str, float] = field(
        default_factory=lambda: {
            "carnet": 0.40,
            "chaqueta_unefa": 0.55,
            "pantalon_oscuro": 0.55,
            "uniforme_superior": 0.55,
        }
    )

    def __post_init__(self) -> None:
        if not self.ruta_modelo:
            self.ruta_modelo = os.path.abspath(
                os.path.join(self.BASE_DIR, "..", "best.pt")
            )

    # --- Cámara ---
    fuente_camara: int = int(os.environ.get("CAMERA_SOURCE", "0"))
    ancho_cuadro: int = 1280
    alto_cuadro: int = 720
    fps_objetivo: int = 30

    # --- Privacidad y Rendimiento (Censor y YOLO) ---
    escala_redimension_censor: float = 0.60
    factor_escala_rostro: float = 1.1
    vecinos_minimos_rostro: int = 4
    tamano_minimo_rostro: tuple[int, int] = (15, 15)
    intensidad_blur: int = 99

    salto_inferencia: int = 3
    salto_censor: int = 6
    workers_yolo: int = 0
    ventana_estabilizacion: int = 15
    fraccion_estabilizacion: float = 0.40

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
