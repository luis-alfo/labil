# Botón Claude — aprendizajes

Botón de mesa impreso en la A1: una palanca de plástico pulsa directamente el botón BOOT de un
ESP32-C3 Super Mini (sin interruptor aparte). Alimentado por USB-C desde un Mac.
Estado: **borrador «funda», sin imprimir** (21 nov 2026). Fuente: `generar.py`. Uso y ajustes: `README.md`.

## La placa (ESP32-C3 Super Mini, comprada en Diotronic)

- Luis pidió buscar las medidas en internet en vez de medir (21 nov 2026). Lo que hay:
  | Dato | Valor | De dónde sale | Incertidumbre |
  | --- | --- | --- | --- |
  | Contorno | 22,5 × 18,0 mm | varias fichas (mischianti, espboards) | ±0,2; cambia algo según fabricante |
  | Alto total con componentes | 4,5 mm | ficha | manda el USB-C (~3,2 mm sobre la placa) |
  | Grosor de la placa | ~1,0 mm | fichas, dato ambiguo (0,8–1,2) | ±0,2 |
  | Centro de BOOT | 5,6 mm del borde largo izquierdo, 8,7 mm del borde del USB | **medido por Claude sobre la foto de Diotronic** (15,1 px/mm) | ±0,5 |
  | Centro de RST | 12,2 mm y 8,7 mm | ídem | ±0,5 |
  | Separación BOOT–RST | 6,6 mm | ídem | ±0,3 |
  | Alto del pulsador | ~2 mm sobre la placa (pulsador SMD típico de 3×4×2) | supuesto | ±0,5 |
- **No hay plano mecánico publicado con la posición de los botones.** Por eso el diseño absorbe
  ±0,7 mm (apoyo ancho en la palanca, holgura en el alojamiento) y antes de la pieza final se imprime
  una **prueba de encaje**. «Izquierda» = con el USB arriba y los componentes hacia ti.
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
  sesión en la que estaba Luis; si Claude ya está activo, acepta. Confirmado por Luis.
- **Pulsación larga = F18**, que Luis configura en Wispr Flow para dictar (Luis, 21 nov 2026).
- **«Claude» = la app de escritorio de Claude para Mac.**
- **Sin soldar los pines. PLA.**
- **En la mesa, con cable. Mac.**

## El diseño «funda»

- **Una pieza, 21,6 × 25,8 × 7,4 mm, 2,1 g, 0,04 €.** La placa entra deslizando por detrás.
- **Palanca**: lengüeta del techo recortada en U (1,0 mm de grosor, 11 de ancho, 12,8 de brazo),
  con la bisagra en el frente y un **tetón** de 3 mm sobre BOOT. Taladros de alivio en la raíz.
- **Pestañas**: los últimos 9 mm de cada pared lateral van sueltos del techo y del suelo, y acaban
  en un diente de 0,45 mm que se cierra detrás de la placa. Sin ellas, al desenchufar el cable
  la placa saldría con él (un USB-C agarra 8–20 N).
- **El techo y el suelo acaban donde acaba la placa.** El conector del cable mide unos 12 × 6,5 mm
  y el hueco interior 4,8 mm de alto: si la funda siguiera, el cable no entraría del todo.
- **Boca abajo en la placa**: techo y palanca en la primera capa (capas en el plano de la flexión),
  el tetón crece hacia arriba y el suelo es un puente de 18,4 mm. Sin soportes.
- **Por qué no hay pieza de prueba aparte**: la pieza entera son 2 g. Ella es la prueba de encaje.

### Cálculo (viga en voladizo, PLA: E 2300 MPa, rotura 55 MPa)

| Caso | Flecha | Tensión | Margen | Fuerza |
| --- | --- | --- | --- | --- |
| Palanca, botón de 2,5 mm de alto | 0,45 mm | 9 MPa | ×5,8 | 1,4 N + pulsador |
| Palanca, botón de 2,25 mm (supuesto) | 0,70 mm | 15 MPa | ×3,7 | 2,1 N + pulsador |
| Palanca, botón de 2,0 mm | 0,95 mm | 20 MPa | ×2,7 | 2,9 N + pulsador |
| Pestaña, al meter la placa | 0,25 mm | 18 MPa | ×3,1 | 6,5 N por lado |

### Qué está comprobado y qué no

- Comprobado: malla cerrada y de un cuerpo; cortes con la placa, los botones y el USB dentro, sin
  choques; vista en la web; el programa de la placa **compila** (PlatformIO, ESP32-C3); la lógica
  del programa del Mac, con un puerto simulado (toque detrás → abre Claude; toque delante → Enter;
  larga → F18 abajo y arriba).
- **Sin comprobar** (no hay Mac ni placa en la sesión): el envío real de teclas en macOS, que
  Wispr Flow acepte un F18 sintético, y el identificador de la app (`com.anthropic.claudefordesktop`).
- **Supuestos que la primera impresión dirá**: alto del pulsador, posición de BOOT, grosor y
  ancho reales de la placa.

## Cómo reparten el trabajo placa y Mac

- La placa solo manda `D` (pulsado) y `U` (soltado). No sabe qué es un toque corto o largo.
- El Mac mide el tiempo y decide. Así, cambiar un gesto es editar un archivo de texto en el Mac,
  sin volver a cargar la placa.
- Para enviar teclas, macOS exige permiso de **Accesibilidad** al programa que las envía.
- Si BOOT está pulsado al enchufar, el chip arranca en modo de carga y no ejecuta el programa.

## Códigos compartidos

- *funda*: la pieza entera. *tetón*: el cilindro bajo la palanca que toca el botón.
- *pestaña*: el tramo suelto de pared que retiene la placa. *diente*: su resalte. *labio*: el apoyo bajo la placa.
- *toque* / *larga*: pulsación de menos / más de 0,4 s.

- *palanca*: la pieza impresa que flexa y pulsa el botón de la placa.
- *BOOT* / *RST*: los dos pulsadores de la placa (programable / reinicio).
- *serie*: el canal de texto por USB entre placa y ordenador.
- *HID*: lo que hace que un aparato sea «teclado» para el ordenador.
