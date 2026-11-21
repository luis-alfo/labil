# Botón Claude

Un botón de mesa para Claude. Una funda impresa de 21,6 × 25,8 × 7,4 mm (2 g) aloja un
ESP32-C3 Super Mini; la palanca del techo pulsa directamente el botón BOOT de la placa.

| Gesto | Qué hace |
| --- | --- |
| Toque, con Claude detrás | trae la app de Claude al frente, donde la dejaste |
| Toque, con Claude delante | Enter (aceptar) |
| Mantener pulsado (más de 0,4 s) | F18 mientras dure: dictado en Wispr Flow |

## Tres pasos

1. **Imprimir** `boton_claude.3mf` (proyecto de Bambu Studio para la A1: PLA, 0,20 mm, 4 paredes,
   PEI texturizada, sin soportes; unos 2 g). Va boca abajo, tal como viene.
2. **Cargar el programa de la placa**: `firmware/boton_claude/boton_claude.ino` con Arduino IDE
   (placa «ESP32C3 Dev Module», «USB CDC On Boot: Enabled»), o `pio run -t upload` desde `firmware/`.
3. **En el Mac**: `python3 mac/boton_claude.py` para probar; `mac/instalar.sh` para que arranque solo.
   macOS pedirá permiso de Accesibilidad (Ajustes → Privacidad y seguridad → Accesibilidad).
   En Wispr Flow, poner F18 como atajo de «mantener para hablar».

Meter la placa por detrás, con los componentes hacia la palanca y el USB hacia fuera, hasta el clic.
Para sacarla, abrir las dos pestañas con las uñas y empujar desde el hueco de abajo.

## Qué mirar en la primera impresión (es también la prueba de encaje)

```
[ ] La placa entra deslizando y las pestañas hacen clic detrás de ella
[ ] Tirando del cable, la placa no se sale
[ ] Sin tocar, el LED azul está apagado (el botón no queda pulsado)
[ ] Al pulsar la palanca se nota el clic del pulsador y se enciende el LED azul
[ ] El conector del cable entra del todo
```

| Si pasa esto | Cambiar en `generar.py` |
| --- | --- |
| El botón queda pulsado siempre | `TETON_Z += 0.3` |
| Hay que apretar mucho o no llega | `TETON_Z -= 0.3` |
| El tetón cae al lado del botón | `BOOT_X` / `BOOT_USB` con la medida real |
| La placa no entra de ancho | `HOLGURA += 0.1` |
| La placa se sale | `DIENTE += 0.15` |

Ojo: si la palanca está pulsada **al enchufar**, el chip arranca en modo de carga de programa y
no hace nada. Se desenchufa y se vuelve a enchufar sin tocarla.
