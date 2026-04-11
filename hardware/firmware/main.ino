// Firmware Arduino - Proyecto Visión Artificial

const int PINO_ALARMA = 13;
const int PINO_SENSOR = 2; // Ejemplo de parada de emergencia o sensor auxiliar

void setup() {
  Serial.begin(9600);
  
  pinMode(PINO_ALARMA, OUTPUT);
  pinMode(PINO_SENSOR, INPUT_PULLUP);
  
  digitalWrite(PINO_ALARMA, LOW);
  
  // Enviar señal de estado al iniciar
  Serial.println("{\"estado\": \"iniciado\", \"dispositivo\": \"arduino_central\"}");
}

void loop() {
  // Procesar comandos recibidos vía Serial desde el Backend (o Gateway)
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    procesar_comando(comando);
  }
  
  // Validar sensores locales
  int estado_sensor = digitalRead(PINO_SENSOR);
  if (estado_sensor == LOW) {
    // Comunicar incidencia al backend
    Serial.println("{\"evento\": \"boton_presionado\"}");
    delay(500); // Debounce simple
  }
}

void procesar_comando(String comando) {
  if (comando == "ACTIVAR_ALARMA") {
    digitalWrite(PINO_ALARMA, HIGH);
    Serial.println("{\"respuesta\": \"alarma_ok\"}");
  } 
  else if (comando == "DESACTIVAR_ALARMA") {
    digitalWrite(PINO_ALARMA, LOW);
    Serial.println("{\"respuesta\": \"desactivacion_ok\"}");
  }
  else {
    // Manejo de error o comando desconocido
    Serial.println("{\"error\": \"comando_invalido\"}");
  }
}
