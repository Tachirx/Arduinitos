import cv2
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

log = logging.getLogger("ia.streamer")

class StreamHandler(BaseHTTPRequestHandler):
    streamer_instance = None 

    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
           
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            try:
                if self.streamer_instance:
                    self.streamer_instance.registrar_conexion()
                while True:
                    if self.streamer_instance:
                        frame_bytes = self.streamer_instance.obtener_frame_bytes()
                        if frame_bytes is not None:
                            self.wfile.write(b'--FRAME\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', len(frame_bytes))
                            self.end_headers()
                            self.wfile.write(frame_bytes)
                            self.wfile.write(b'\r\n')
                   
                    self.streamer_instance.esperar_nuevo_frame(timeout=0.05)
            except Exception:
               
                pass
            finally:
                if self.streamer_instance:
                    self.streamer_instance.desregistrar_conexion()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Ruta no encontrada')

    def log_message(self, format, *args):
       
        pass

class StreamerLocal:
    """Micro-servidor nativo (Zero dependencies) para stream de video MJPEG."""
    def __init__(self, puerto: int = 8001):
        self.puerto = puerto
        self._frame_bytes = None
        self.clientes_activos = 0
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._server = None
        self._hilo = None
        StreamHandler.streamer_instance = self

    def registrar_conexion(self) -> None:
        with self._lock:
            self.clientes_activos += 1
            log.info("Cliente de streaming conectado. Clientes activos: %d", self.clientes_activos)

    def desregistrar_conexion(self) -> None:
        with self._lock:
            self.clientes_activos = max(0, self.clientes_activos - 1)
            log.info("Cliente de streaming desconectado. Clientes activos: %d", self.clientes_activos)

    def iniciar(self) -> None:
        class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
            daemon_threads = True

        try:
            self._server = ThreadedHTTPServer(('0.0.0.0', self.puerto), StreamHandler)
            self._hilo = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._hilo.start()
            log.info("Micro-servidor de streaming iniciado en puerto %d", self.puerto)
        except Exception as e:
            log.error("Error iniciando streamer: %s", e)

    def detener(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._hilo:
            self._hilo.join(timeout=1)
        log.info("Servidor de streaming detenido.")

    def actualizar_frame(self, frame) -> None:
        
        with self._lock:
            hay_clientes = self.clientes_activos > 0
        if not hay_clientes:
            return

        try:
           
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 65])
            with self._condition:
                self._frame_bytes = buffer.tobytes()
               
                self._condition.notify_all()
        except Exception as e:
            log.error("Error codificando frame: %s", e)

    def obtener_frame_bytes(self) -> bytes | None:
        with self._lock:
            return self._frame_bytes

    def esperar_nuevo_frame(self, timeout: float = 0.1) -> None:
        with self._condition:
            self._condition.wait(timeout=timeout)
