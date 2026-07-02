import platform
import threading
from core.logger import log

class DespachadorHardware:
    """
    Gestiona la conexión Serial con la placa Arduino en portería.
    Si el hardware físico no se detecta, activa el modo fallback acústico de Windows.
    """
    def __init__(self, puerto: str = "COM3", baudrate: int = 9600):
        self._puerto = puerto
        self._baudrate = baudrate
        self._serial = None
        self._modo_fallback = False
        
        try:
            import serial
            self._serial = serial.Serial(self._puerto, self._baudrate, timeout=1)
            log.info(f"Conexión Arduino establecida exitosamente en el puerto {self._puerto}.")
        except ImportError:
            log.warning("Librería 'pyserial' no encontrada. Activando sonido Fallback Windows.")
            self._modo_fallback = True
        except Exception as e:
            log.warning(f"Arduino no detectado o error de conexión en {self._puerto}: {e}. Activando sonido Fallback Windows.")
            self._modo_fallback = True

    def emitir_alerta(self) -> None:
        """
        Despacha la alerta física asíncronamente para evitar latencias bloqueantes 
        hacia el motor de IA que realizó la petición POST.
        """
        threading.Thread(target=self._ejecutar_alerta, daemon=True).start()

    def _ejecutar_alerta(self) -> None:
        """
        Envía el pulso UART 'ACTIVAR_ALARMA' al hardware, o reproduce el sonido de error en Windows.
        """
        if not self._modo_fallback and self._serial and self._serial.is_open:
            try:
              
                self._serial.write(b"ACTIVAR_ALARMA\n")
                log.debug("Señal UART de alerta enviada al hardware exitosamente.")
            except Exception as e:
                log.error(f"Fallo enviando comando Serial al Arduino: {e}")
                self._ejecutar_fallback()
        else:
            self._ejecutar_fallback()

    def _ejecutar_fallback(self) -> None:
        """
        Fallback acústico nativo de Windows si falla el hardware.
        """
        if platform.system() == "Windows":
            try:
                import winsound
               
                winsound.Beep(850, 400)
                winsound.Beep(850, 400)
            except Exception as e:
                log.error(f"Fallo emitiendo sonido Fallback nativo de Windows: {e}")
        else:
            log.warning("Alerta acústica ignorada: El sistema operativo no es Windows.")


despachador = DespachadorHardware()
