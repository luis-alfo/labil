// Botón Claude — programa de la placa (ESP32-C3 Super Mini).
//
// La placa no decide nada: solo cuenta por el puerto serie USB cuándo se pulsa
// y cuándo se suelta el botón BOOT. Una línea por suceso:
//   D  = pulsado (down)      U  = soltado (up)
// Qué significa cada pulsación lo decide el programa del Mac (mac/boton_claude.py).
//
// Arduino IDE: placa «ESP32C3 Dev Module», «USB CDC On Boot: Enabled».

const int PIN_BOOT = 9;        // botón BOOT: une GPIO9 a masa al pulsar
const int PIN_LED = 8;         // LED azul de la placa (se enciende con LOW)
const unsigned long REBOTE_MS = 15;

bool pulsado = false;          // estado ya filtrado
bool lectura = false;          // última lectura en bruto
unsigned long cambio = 0;      // cuándo cambió la lectura en bruto

void setup() {
  pinMode(PIN_BOOT, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);
  Serial.begin(115200);
  Serial.setTxTimeoutMs(0);    // si nadie escucha, no se queda esperando
}

void loop() {
  bool ahora = digitalRead(PIN_BOOT) == LOW;
  if (ahora != lectura) {
    lectura = ahora;
    cambio = millis();
  }
  if (lectura != pulsado && millis() - cambio >= REBOTE_MS) {
    pulsado = lectura;
    digitalWrite(PIN_LED, pulsado ? LOW : HIGH);
    Serial.println(pulsado ? "D" : "U");
  }
  delay(1);
}
