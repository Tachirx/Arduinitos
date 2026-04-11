import cv2
import logging
from typing import Optional

# Setup logger local para IA
logging.basicConfig(level=logging.INFO, format="%(asctime)s | IA | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

class MotorVisionIA:
    """Clase principal para procesamiento de inferencia de video."""
    def __init__(self, fuente_camara: int = 0):
        self.fuente_camara = fuente_camara
        self.captura: Optional[cv2.VideoCapture] = None
        
        # Simulación de carga de modelo (ej. YOLOv8)
        log.info("Cargando modelo YOLO (simulado)...")
        # auto model = ultralytics.YOLO('yolov8n.pt')
        
    def iniciar_streaming(self):
        self.captura = cv2.VideoCapture(self.fuente_camara)
        if not self.captura.isOpened():
            log.error("No se pudo abrir la cámara.")
            return

        log.info("Iniciando procesamiento de frames...")
        try:
            while True:
                ret, frame = self.captura.read()
                if not ret:
                    log.warning("Frame no recuperado, ignorando...")
                    continue
                
                # Aquí se realizaría la inferencia
                # resultados = model(frame)
                
                # Mock de detección: dibujar un cuadro demostrativo
                cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)
                cv2.putText(frame, "Deteccion Activa", (105, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("IA - Monitor en vivo", frame)
                
                # Salir con tecla 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            log.info("Interrupción por teclado detectada.")
        except Exception as exc:
            log.error(f"Error procesando video: {exc}", exc_info=True)
        finally:
            self._limpiar_recursos()

    def _limpiar_recursos(self):
        if self.captura:
            self.captura.release()
        cv2.destroyAllWindows()
        log.info("Recursos de IA liberados.")

if __name__ == "__main__":
    motor = MotorVisionIA()
    motor.iniciar_streaming()
