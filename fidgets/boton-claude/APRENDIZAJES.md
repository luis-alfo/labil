# Botón Claude — aprendizajes

Botón de mesa impreso en la A1: una palanca de plástico pulsa directamente el botón BOOT de un
ESP32-C3 Super Mini (sin interruptor aparte). Alimentado por USB-C desde un Mac.
Estado: **entrevista** (21 nov 2026). Sin geometría todavía.

## La placa (ESP32-C3 Super Mini, comprada en Diotronic)

- Medidas nominales: 22,5 × 18 mm, USB-C en un extremo, 8 pines por lado. **Sin medir aún
  con calibre**: posición y altura de los botones pendientes de la placa real de Luis.
- Fotos: `proceso/boton-claude/`.

## Cómo se relaciona este chip con el ordenador

1. **Los dos botones no son iguales.**
   - **BOOT** va al pin GPIO9. El programa lo lee como cualquier pulsador. Su otro papel:
     si está pulsado *en el momento de arrancar*, el chip entra en modo de carga de programa.
   - **RST** va a la pata de encendido del chip (EN). Pulsarlo lo apaga y lo arranca: el programa
     no llega a «ver» la pulsación. Solo sirve como botón con truco (mandar algo al arrancar,
     2-3 s de retraso, y se dispara también al enchufar).
2. **El USB del C3 es solo un puerto serie.** El chip trae dentro un «USB Serial/JTAG» fijo:
   el ordenador lo ve como un puerto por el que pasan textos (y por el que se le carga el programa).
   **No puede hacerse pasar por teclado ni ratón USB.** Eso (USB «HID») lo hacen los chips con
   USB programable: ESP32-S2, ESP32-S3, RP2040 (Raspberry Pi Pico), ATmega32U4 (Pro Micro).
3. **Tres caminos para que un botón haga algo en el ordenador:**
   | Camino | Qué ve el ordenador | Instalar algo | Qué puede hacer |
   | --- | --- | --- | --- |
   | Teclado USB (HID) | un teclado | no | solo teclas. **El C3 no puede.** |
   | Teclado Bluetooth (BLE HID) | un teclado inalámbrico | no (emparejar) | solo teclas |
   | Serie USB + programa en el ordenador | un puerto serie | sí, un script siempre arrancado | lo que sea: mirar qué app está delante, abrirla, teclear |
4. **Regla para elegir chip en futuros diseños:** si tiene que funcionar en cualquier ordenador
   sin instalar nada → chip con USB HID (S3, RP2040) o Bluetooth. Si el botón tiene que
   *decidir según lo que pasa en el ordenador* → serie + programa, y entonces vale el chip más barato.

## Decisiones de Luis (entrevista, 21 nov 2026)

- **Una sola palanca sobre BOOT.** RST queda tapado (accesible con un clip si acaso).
- **Serie USB + programa en el Mac.**
- **Un botón que depende del contexto:** si Claude no está activo, lo trae al frente en la última
  sesión en la que estaba Luis; si Claude ya está activo, acepta. (Interpretación de Claude de una
  respuesta dictada; pendiente de confirmar, y de saber si «Claude» es la app o Claude Code.)
- **En la mesa, con cable. Mac.**

## Códigos compartidos

- *palanca*: la pieza impresa que flexa y pulsa el botón de la placa.
- *BOOT* / *RST*: los dos pulsadores de la placa (programable / reinicio).
- *serie*: el canal de texto por USB entre placa y ordenador.
- *HID*: lo que hace que un aparato sea «teclado» para el ordenador.
