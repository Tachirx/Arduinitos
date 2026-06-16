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


class EstabilizadorVentana:
    _CAMPOS = [
        "carnet",
        "chaqueta_unefa",
        "pantalon_oscuro",
        "uniforme_superior",
    ]

    def __init__(self, ventana: int = 12, fraccion_minima: float = 0.55, umbral_tracking: int = 160) -> None:
        self._ventana = ventana
        self._fraccion = fraccion_minima
        self._umbral_tracking = umbral_tracking
        self._historial_rostros: deque = deque(maxlen=ventana)
        self._personas_trackeadas: list[dict] = []

    def actualizar(self, resultado: ResultadoDeteccion) -> ResultadoDeteccion:
        # Envejecer tracks para limpiar los que ya no están en escena
        for t in self._personas_trackeadas:
            t["edad"] += 1

        estabilizado = ResultadoDeteccion(estudiantes=[])
        
        # Procesar detecciones crudas del frame actual
        for est in resultado.estudiantes:
            track_match = None
            min_dist = 9999
            for t in self._personas_trackeadas:
                dist = abs(t["cx"] - est.centro_x)
                if dist < self._umbral_tracking and dist < min_dist:
                    min_dist = dist
                    track_match = t
                    
            if track_match:
                track_match["edad"] = 0
                track_match["cx"] = est.centro_x
                track_match["box"] = (est.x1, est.y1, est.x2, est.y2)
                for c in self._CAMPOS:
                    track_match["hist"][c].append(int(getattr(est, c)))
            else:
                track_match = {
                    "cx": est.centro_x,
                    "edad": 0,
                    "box": (est.x1, est.y1, est.x2, est.y2),
                    "hist": {c: deque([int(getattr(est, c))], maxlen=self._ventana) for c in self._CAMPOS}
                }
                self._personas_trackeadas.append(track_match)
                
        # Reconstruir la escena desde la memoria del Tracker
        for t in self._personas_trackeadas:
            if t["edad"] < 5:  # Tolerar hasta 5 frames "ciegos" de YOLO
                x1, y1, x2, y2 = t["box"]
                nuevo_est = EstudianteDetectado(
                    x1=x1, y1=y1, x2=x2, y2=y2, centro_x=t["cx"]
                )
                for c in self._CAMPOS:
                    hist = t["hist"][c]
                    # Si el historial tiene pocos elementos, confiaremos en lo poco que tenemos
                    if len(hist) > 0:
                        proporcion = sum(hist) / len(hist)
                        setattr(nuevo_est, c, proporcion >= self._fraccion)
                estabilizado.estudiantes.append(nuevo_est)

        # Limpiar tracks de personas que salieron de la cámara (>5 frames ausentes)
        self._personas_trackeadas = [t for t in self._personas_trackeadas if t["edad"] < 5]

        # Estabilización de rostros se mantiene global
        self._historial_rostros.append(resultado.rostros_detectados)
        if self._historial_rostros:
            valores = sorted(self._historial_rostros)
            n = len(valores)
            estabilizado.rostros_detectados = valores[n // 2]

        return estabilizado

    def reiniciar(self) -> None:
        self._personas_trackeadas.clear()
        self._historial_rostros.clear()


class DetectorVestimenta:
    def __init__(
        self,
        ruta_modelo: str,
        umbral_confianza: float,
        clases_objetivo: dict,
        umbrales_clases: dict[str, float] = None,
        umbral_agrupamiento: int = 160,
    ) -> None:
        self._modelo = YOLO(ruta_modelo)
        self._modelo.fuse()
        self._umbral_base = umbral_confianza
        self._clases = clases_objetivo
        self._umbrales_clases = umbrales_clases or {}
        self._umbral_agrupamiento = umbral_agrupamiento
        log.info(
            "Modelo YOLO cargado y fusionado: %s | Umbral base: %s | Umbrales dinamicos: %s | Umbral agrupamiento: %s",
            ruta_modelo,
            self._umbral_base,
            self._umbrales_clases,
            self._umbral_agrupamiento,
        )

    def inferir(self, cuadro: np.ndarray) -> ResultadoDeteccion:
        umbral_yolo = min(self._umbrales_clases.values()) if self._umbrales_clases else self._umbral_base

        # Preprocesamiento de iluminación adaptativa para YOLO
        brillo_promedio = np.mean(cuadro)
        cuadro_yolo = cuadro
        if brillo_promedio < 85:
            # Multiplica canales para forzar contraste e ilumina las sombras
            cuadro_yolo = cv2.convertScaleAbs(cuadro, alpha=1.35, beta=35)

        resultados = self._modelo(
            cuadro_yolo,
            conf=umbral_yolo,
            imgsz=640,
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
            umbral_especifico = self._umbrales_clases.get(nombre, self._umbral_base)
            if nombre and confianza >= umbral_especifico:
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
        objetos_ordenados = sorted(objetos, key=lambda x: x["cx"])
        grupos: list[list[dict]] = []

        for obj in objetos_ordenados:
            agrupado = False
            for grupo in grupos:
                centro_grupo = sum(g["cx"] for g in grupo) / len(grupo)
                if abs(obj["cx"] - centro_grupo) < self._umbral_agrupamiento:
                    grupo.append(obj)
                    agrupado = True
                    break
            if not agrupado:
                grupos.append([obj])

        # --- Instanciar EstudianteDetectado por cada grupo ---
        for grupo in grupos:
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

            for g in grupo:
                setattr(estudiante, g["nombre"], True)
                estudiante.confianzas[g["nombre"]] = g["conf"]

            resultado.estudiantes.append(estudiante)

        return resultado


class CensorPrivacidad:
    def __init__(
        self, 
        intensidad_blur: int = 51,
        escala_redimension: float = 0.5,
        factor_escala: float = 1.1,
        vecinos_minimos: int = 4,
        tamano_minimo: tuple[int, int] = (15, 15)
    ) -> None:
        self._intensidad = (
            intensidad_blur if intensidad_blur % 2 != 0 else intensidad_blur + 1
        )
        self._escala_redimension = escala_redimension
        self._factor_escala = factor_escala
        self._vecinos_minimos = vecinos_minimos
        self._tamano_minimo = tamano_minimo
        self._detector_rostros = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        if self._detector_rostros.empty():
            log.error("No se pudo cargar haarcascade_frontalface_default.xml")

        self._regiones_cache: list[tuple[int, int, int, int]] = []
        self._cantidad_cache: int = 0
        self._regiones_previas: list[tuple[int, int, int, int]] = []
        self._ciclos_sin_rostro: int = 0
        log.info("OpenCV Face Detection iniciado | Blur kernel: %d | Escala: %.2f", self._intensidad, self._escala_redimension)

    def detectar_regiones_rostros(self, cuadro: np.ndarray) -> tuple[list[tuple[int, int, int, int]], int]:
        alto, ancho = cuadro.shape[:2]

        ancho_proc = int(ancho * self._escala_redimension)
        alto_proc = int(alto * self._escala_redimension)
        
        if self._escala_redimension != 1.0:
            pequeno = cv2.resize(cuadro, (ancho_proc, alto_proc))
        else:
            pequeno = cuadro

        gris = cv2.cvtColor(pequeno, cv2.COLOR_BGR2GRAY)
        gris = cv2.equalizeHist(gris)

        rostros = self._detector_rostros.detectMultiScale(
            gris,
            scaleFactor=self._factor_escala,
            minNeighbors=self._vecinos_minimos,
            minSize=self._tamano_minimo,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        nuevas_regiones: list[tuple[int, int, int, int]] = []
        if len(rostros) > 0:
            factor_inverso = 1.0 / self._escala_redimension
            for x, y, w, h in rostros:
                x1 = int(round(x * factor_inverso))
                y1 = int(round(y * factor_inverso))
                x2 = min(int(round((x + w) * factor_inverso)), ancho)
                y2 = min(int(round((y + h) * factor_inverso)), alto)
                if x2 > x1 and y2 > y1:
                    nuevas_regiones.append((x1, y1, x2, y2))

        # --- Lógica de persistencia de rostros ---
        if nuevas_regiones:
            self._regiones_previas = nuevas_regiones
            self._ciclos_sin_rostro = 0
        else:
            if self._ciclos_sin_rostro < 3 and self._regiones_previas:
                self._ciclos_sin_rostro += 1
                nuevas_regiones = self._regiones_previas
            else:
                self._regiones_previas = []

        return nuevas_regiones, len(nuevas_regiones)

    def aplicar_desenfoque(self, cuadro: np.ndarray, regiones: list[tuple[int, int, int, int]]) -> np.ndarray:
        cuadro_salida = cuadro.copy()
        alto, ancho = cuadro_salida.shape[:2]

        for x1, y1, x2, y2 in regiones:
            ancho_caja = x2 - x1
            alto_caja = y2 - y1
            margen_x = int(ancho_caja * 0.15)
            margen_y = int(alto_caja * 0.15)

            x1_exp = max(0, x1 - margen_x)
            y1_exp = max(0, y1 - margen_y)
            x2_exp = min(x2 + margen_x, ancho)
            y2_exp = min(y2 + margen_y, alto)

            roi = cuadro_salida[y1_exp:y2_exp, x1_exp:x2_exp]
            if roi.size > 0:
                cuadro_salida[y1_exp:y2_exp, x1_exp:x2_exp] = cv2.GaussianBlur(
                    roi, (self._intensidad, self._intensidad), 30
                )

        return cuadro_salida

    def censurar_rostros(
        self, cuadro: np.ndarray, recalcular: bool = True
    ) -> tuple[np.ndarray, int]:
        if recalcular:
            self._regiones_cache, self._cantidad_cache = self.detectar_regiones_rostros(cuadro)
        cuadro_salida = self.aplicar_desenfoque(cuadro, self._regiones_cache)
        return cuadro_salida, self._cantidad_cache

    def liberar(self) -> None:
        self._regiones_cache.clear()
