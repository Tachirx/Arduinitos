import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
from dataclasses import dataclass, field
from typing import Optional
import logging

log = logging.getLogger("ia.detector")


@dataclass
class ResultadoDeteccion:
    """Resultado de una inferencia sobre un frame."""
    uniforme_superior: bool = False
    pantalon_oscuro: bool = False
    carnet: bool = False
    rostros_detectados: int = 0
    confianzas: dict = field(default_factory=dict)

    @property
    def cumple_normativa(self) -> bool:
        return self.uniforme_superior and self.pantalon_oscuro and self.carnet


class DetectorVestimenta:
    """Ejecuta inferencia YOLOv8n sobre frames individuales."""

    def __init__(self, ruta_modelo: str, umbral_confianza: float, clases_objetivo: dict):
        self._modelo = YOLO(ruta_modelo)
        self._umbral = umbral_confianza
        self._clases = clases_objetivo
        log.info(f"Modelo YOLO cargado: {ruta_modelo} | Umbral: {self._umbral}")

    def inferir(self, frame: np.ndarray) -> ResultadoDeteccion:
        resultados = self._modelo(frame, conf=self._umbral, verbose=False)
        resultado = ResultadoDeteccion()

        if not resultados or not resultados[0].boxes:
            return resultado

        cajas = resultados[0].boxes
        for caja in cajas:
            clase_id = int(caja.cls[0])
            confianza = float(caja.conf[0])
            nombre_clase = self._clases.get(clase_id)

            if nombre_clase == "Uniforme_superior_reglamentario":
                resultado.uniforme_superior = True
                resultado.confianzas["uniforme_superior"] = confianza
            elif nombre_clase == "Pantalon_oscuro":
                resultado.pantalon_oscuro = True
                resultado.confianzas["pantalon_oscuro"] = confianza
            elif nombre_clase == "Carnet":
                resultado.carnet = True
                resultado.confianzas["carnet"] = confianza

        return resultado

    def obtener_cajas_raw(self, frame: np.ndarray):
        return self._modelo(frame, conf=self._umbral, verbose=False)


class CensorPrivacidad:
    """Aplica blur facial usando MediaPipe Face Detection."""

    def __init__(self, confianza_minima: float = 0.5, intensidad_blur: int = 99):
        self._detector_rostros = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=confianza_minima,
        )
        self._intensidad = intensidad_blur
        log.info(f"MediaPipe Face Detection iniciado | Confianza mín: {confianza_minima}")

    def censurar_rostros(self, frame: np.ndarray) -> tuple[np.ndarray, int]:
        frame_salida = frame.copy()
        alto, ancho, _ = frame_salida.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = self._detector_rostros.process(frame_rgb)

        cantidad_rostros = 0
        if resultados.detections:
            for deteccion in resultados.detections:
                bbox = deteccion.location_data.relative_bounding_box
                x_min = max(0, int(bbox.xmin * ancho))
                y_min = max(0, int(bbox.ymin * alto))
                x_max = min(ancho, int((bbox.xmin + bbox.width) * ancho))
                y_max = min(alto, int((bbox.ymin + bbox.height) * alto))

                if x_max > x_min and y_max > y_min:
                    roi = frame_salida[y_min:y_max, x_min:x_max]
                    roi_blur = cv2.GaussianBlur(roi, (self._intensidad, self._intensidad), 30)
                    frame_salida[y_min:y_max, x_min:x_max] = roi_blur
                    cantidad_rostros += 1

        return frame_salida, cantidad_rostros

    def liberar(self):
        self._detector_rostros.close()
