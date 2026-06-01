from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field

import cv2
import numpy as np
from ultralytics import YOLO

log = logging.getLogger("ia.detector")

@dataclass
class EstudianteDetectado:
    """Representa a un estudiante detectado individualmente en la escena."""
    x1: int
    y1: int
    x2: int
    y2: int
    carnet: bool = False
    chaqueta_unefa: bool = False
    pantalon_oscuro: bool = False
    uniforme_superior: bool = False
    confianzas: dict = field(default_factory=dict)
    centro_x: float = 0.0

    @property
    def cumple_normativa(self) -> bool:
        """Determina si este estudiante específico cumple con la vestimenta de la Unefa."""
        combinaciones_validas = [
            {"carnet", "pantalon_oscuro", "uniforme_superior"},
            {"carnet", "pantalon_oscuro", "uniforme_superior", "chaqueta_unefa"},
            {"carnet", "pantalon_oscuro", "chaqueta_unefa"},
        ]
        elementos_activos: set[str] = set()
        if self.carnet:
            elementos_activos.add("carnet")
        if self.chaqueta_unefa:
            elementos_activos.add("chaqueta_unefa")
        if self.pantalon_oscuro:
            elementos_activos.add("pantalon_oscuro")
        if self.uniforme_superior:
            elementos_activos.add("uniforme_superior")
        return elementos_activos in combinaciones_validas

@dataclass
class ResultadoDeteccion:
    """Resultado global de la inferencia, con soporte para múltiples estudiantes."""
    estudiantes: list[EstudianteDetectado] = field(default_factory=list)
    rostros_detectados: int = 0

    @property
    def cumple_normativa(self) -> bool:
        """La escena es válida si todos los estudiantes presentes cumplen las normas."""
        if not self.estudiantes:
            return True
        return all(est.cumple_normativa for est in self.estudiantes)

    @property
    def confianzas(self) -> dict:
        """Retorna las confianzas del primer estudiante detectado (retocompatibilidad)."""
        if self.estudiantes:
            return self.estudiantes[0].confianzas
        return {}

    # Propiedades de compatibilidad retrospectiva con alertas.py y backend
    @property
    def carnet(self) -> bool:
        return all(est.carnet for est in self.estudiantes) if self.estudiantes else False

    @property
    def chaqueta_unefa(self) -> bool:
        return any(est.chaqueta_unefa for est in self.estudiantes) if self.estudiantes else False

    @property
    def pantalon_oscuro(self) -> bool:
        return all(est.pantalon_oscuro for est in self.estudiantes) if self.estudiantes else False

    @property
    def uniforme_superior(self) -> bool:
        return all(est.uniforme_superior for est in self.estudiantes) if self.estudiantes else False


_UMBRALES_POR_CLASE: dict[str, float] = {
    "carnet": 0.65,
    "chaqueta_unefa": 0.65,
    "pantalon_oscuro": 0.65,
    "uniforme_superior": 0.65,
}

class EstabilizadorVentana:
    _CAMPOS = [
        "carnet",
        "chaqueta_unefa",
        "pantalon_oscuro",
        "uniforme_superior",
    ]

    def __init__(self, ventana: int = 12, fraccion_minima: float = 0.55) -> None:
        self._ventana = ventana
        self._fraccion = fraccion_minima
        self._historiales: dict[str, deque] = {
            campo: deque(maxlen=ventana) for campo in self._CAMPOS
        }
        self._historial_rostros: deque = deque(maxlen=ventana)

    def actualizar(self, resultado: ResultadoDeteccion) -> ResultadoDeteccion:
        for campo in self._CAMPOS:
            self._historiales[campo].append(int(getattr(resultado, campo)))
        self._historial_rostros.append(resultado.rostros_detectados)

        estabilizado = ResultadoDeteccion(estudiantes=resultado.estudiantes)
        
        # Copiar y promediar estados globales estabilizados para alertas generales
        for campo in self._CAMPOS:
            hist = self._historiales[campo]
            if len(hist) == 0:
                continue
            proporcion = sum(hist) / len(hist)
            estado_estabilizado = proporcion >= self._fraccion
            for est in estabilizado.estudiantes:
                setattr(est, campo, estado_estabilizado)

        if self._historial_rostros:
            valores = sorted(self._historial_rostros)
            n = len(valores)
            estabilizado.rostros_detectados = valores[n // 2]

        return estabilizado

    def reiniciar(self) -> None:
        for hist in self._historiales.values():
            hist.clear()
        self._historial_rostros.clear()


class DetectorVestimenta:
    def __init__(
        self,
        ruta_modelo: str,
        umbral_confianza: float,
        clases_objetivo: dict,
    ) -> None:
        self._modelo = YOLO(ruta_modelo)
        self._modelo.fuse()
        self._umbral_base = umbral_confianza
        self._clases = clases_objetivo
        log.info(
            "Modelo YOLO cargado y fusionado: %s | Umbral base: %s | Umbrales por clase: %s",
            ruta_modelo,
            self._umbral_base,
            _UMBRALES_POR_CLASE,
        )

    def inferir(self, frame: np.ndarray) -> ResultadoDeteccion:
        umbral_yolo = min(_UMBRALES_POR_CLASE.values())

        resultados = self._modelo(
            frame,
            conf=umbral_yolo,
            imgsz=480,
            verbose=False,
        )
        resultado = ResultadoDeteccion()

        if not resultados or not resultados[0].boxes:
            return resultado

        cajas = resultados[0].boxes
        cls_array = cajas.cls.cpu().numpy().astype(int)
        conf_array = cajas.conf.cpu().numpy()
        xyxy_array = cajas.xyxy.cpu().numpy()

        objetos = []
        for clase_id, confianza, coords in zip(cls_array, conf_array, xyxy_array):
            nombre = self._clases.get(clase_id)
            if nombre and confianza >= _UMBRALES_POR_CLASE.get(nombre, 0.65):
                x1, y1, x2, y2 = coords
                cx = float((x1 + x2) / 2)
                objetos.append({
                    "nombre": nombre,
                    "cx": cx,
                    "conf": float(confianza),
                    "coords": (int(x1), int(y1), int(x2), int(y2))
                })

        if not objetos:
            return resultado

        # --- Algoritmo de Clustering Espacial 1D por Proximidad Horizontal ---
        #  objetos detectados de izquierda a derecha por coordenada X central
        objetos_ordenados = sorted(objetos, key=lambda x: x["cx"])
        grupos: list[list[dict]] = []

        for obj in objetos_ordenados:
            agrupado = False
            for grupo in grupos:
                # Centro horizontal promedio del grupo actual, verificar esto xfa
                centro_grupo = sum(g["cx"] for g in grupo) / len(grupo)
                # Agrupar si están a menos de 110 píxeles de distancia horizontal
                if abs(obj["cx"] - centro_grupo) < 110:
                    grupo.append(obj)
                    agrupado = True
                    break
            if not agrupado:
                grupos.append([obj])

        # --- Instanciar EstudianteDetectado por cada grupo ---
        for grupo in grupos:
            # Calcular la caja envolvente que unifica todas las prendas de la persona
            x1_env = min(g["coords"][0] for g in grupo)
            y1_env = min(g["coords"][1] for g in grupo)
            x2_env = max(g["coords"][2] for g in grupo)
            y2_env = max(g["coords"][3] for g in grupo)
            centro_x_env = sum(g["cx"] for g in grupo) / len(grupo)

            estudiante = EstudianteDetectado(
                x1=x1_env,
                y1=y1_env,
                x2=x2_env,
                y2=y2_env,
                centro_x=centro_x_env
            )

            # Asignar los elementos detectados al estudiante
            for g in grupo:
                setattr(estudiante, g["nombre"], True)
                estudiante.confianzas[g["nombre"]] = g["conf"]

            resultado.estudiantes.append(estudiante)

        return resultado

class CensorPrivacidad:
    def __init__(self, intensidad_blur: int = 51) -> None:
        self._intensidad = (
            intensidad_blur if intensidad_blur % 2 != 0 else intensidad_blur + 1
        )
        self._detector_rostros = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        if self._detector_rostros.empty():
            log.error("No se pudo cargar haarcascade_frontalface_default.xml")

        self._regiones_cache: list[tuple[int, int, int, int]] = []
        self._cantidad_cache: int = 0
        log.info("OpenCV Face Detection iniciado | Blur kernel: %d", self._intensidad)

    def censurar_rostros(
        self, frame: np.ndarray, recalcular: bool = True
    ) -> tuple[np.ndarray, int]:
        frame_salida = frame.copy()
        alto, ancho = frame.shape[:2]

        if recalcular:
            pequeno = cv2.resize(frame, (ancho // 3, alto // 3))
            gris = cv2.cvtColor(pequeno, cv2.COLOR_BGR2GRAY)
            gris = cv2.equalizeHist(gris)

            rostros = self._detector_rostros.detectMultiScale(
                gris,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(40, 40),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            nuevas_regiones: list[tuple[int, int, int, int]] = []
            if len(rostros) > 0:
                for x, y, w, h in rostros:
                    x1 = x * 3
                    y1 = y * 3
                    x2 = min((x + w) * 3, ancho)
                    y2 = min((y + h) * 3, alto)
                    if x2 > x1 and y2 > y1:
                        nuevas_regiones.append((x1, y1, x2, y2))

            self._regiones_cache = nuevas_regiones
            self._cantidad_cache = len(nuevas_regiones)

        for x1, y1, x2, y2 in self._regiones_cache:
            x2c = min(x2, ancho)
            y2c = min(y2, alto)
            roi = frame_salida[y1:y2c, x1:x2c]
            if roi.size > 0:
                frame_salida[y1:y2c, x1:x2c] = cv2.GaussianBlur(
                    roi, (self._intensidad, self._intensidad), 30
                )

        return frame_salida, self._cantidad_cache

    def liberar(self) -> None:
        self._regiones_cache.clear()
