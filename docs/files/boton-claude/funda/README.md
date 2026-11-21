# Botón Claude

Un botón de mesa para Claude. Dos piezas impresas (base y tapa, 23,2 × 29,5 × 7,4 mm, 3,3 g) alojan un
ESP32-C3 Super Mini; la palanca de la tapa pulsa directamente el botón BOOT de la placa.

| Gesto | Qué hace |
| --- | --- |
| Toque, con Claude detrás | trae la app de Claude al frente, donde la dejaste |
| Toque, con Claude delante | Enter (aceptar) |
| Mantener pulsado (más de 0,4 s) | F18 mientras dure: dictado en Wispr Flow |

## Tres pasos

1. **Imprimir** `boton_modular.3mf` (proyecto de Bambu Studio para la A1: PLA, 0,20 mm, 4 paredes,
   PEI texturizada, sin soportes; 3,3 g). Trae la tapa boca abajo, la base y la galga.
2. **Cargar el programa de la placa**: `firmware/boton_claude/boton_claude.ino` con Arduino IDE
   (placa «ESP32C3 Dev Module», «USB CDC On Boot: Enabled»), o `pio run -t upload` desde `firmware/`.
3. **En el Mac**: `python3 mac/boton_claude.py` para probar; `mac/instalar.sh` para que arranque solo.
   macOS pedirá permiso de Accesibilidad (Ajustes → Privacidad y seguridad → Accesibilidad).
   En Wispr Flow, poner F18 como atajo de «mantener para hablar».

## Montaje

- Dejar caer la placa en la base, con los componentes hacia arriba y el USB entre los dos postes.
- Tapa: meter primero las dos uñas de detrás bajo la base y bajar el frente hasta el clic.
- Para abrir: empujar con la uña el diente que asoma por la ventana del frente y levantar.

## Qué medir con la base sola (antes de poner la tapa)

```
[ ] La placa cae en la base sin forzar. ¿Baila? ¿Cuánto, a lo largo y a lo ancho?
[ ] Muescas de los lados: ¿el centro del botón BOOT queda frente a la muesca honda?
    Si no: hacia el USB o hacia el frente, y cuánto (una muesca = 1 mm, de muesca a muesca = 2 mm)
[ ] Muescas del frente: lo mismo, a izquierda o derecha
[ ] Galga apoyada en la tira de pines, junto al botón: ¿qué escalón enrasa con el pulsador?
    (del más bajo al más alto: 1,8 · 2,0 · 2,2 · 2,4 · 2,6 · 2,8 mm)
[ ] El conector del cable entra del todo entre los postes
```

## Qué mirar con la tapa puesta

```
[ ] La tapa hace clic y no se levanta
[ ] Tirando del cable, nada se mueve
[ ] Sin tocar, el LED azul está apagado (el botón no queda pulsado)
[ ] Al pulsar la palanca se nota el clic del pulsador y se enciende el LED azul
```

| Si pasa esto | Pieza que se repite | Cambiar |
| --- | --- | --- |
| La placa no entra o baila | base | `HOLGURA`, `CAJ_L` en `generar_modular.py` |
| El botón queda pulsado siempre | tapa | `TETON_Z += 0.3` en `generar.py` |
| Hay que apretar mucho o no llega | tapa | `TETON_Z -= 0.3` |
| El tetón cae al lado del botón | tapa | `BOOT_X` / `BOOT_USB` con lo leído en las muescas |
| La tapa no cierra o se suelta | base | `DIENTE`, `JUEGO` |

La versión anterior, de una pieza (`generar.py`, `boton_claude.3mf`), sigue en la carpeta.

Ojo: si la palanca está pulsada **al enchufar**, el chip arranca en modo de carga de programa y
no hace nada. Se desenchufa y se vuelve a enchufar sin tocarla.
