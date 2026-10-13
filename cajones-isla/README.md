# Cajones para los huecos de la isla de la cocina

Huecos de la estantería (pensados para botellas de vino): **130 mm de ancho × 135 mm de alto**.

## Paso 1 — Marco de prueba de encaje (`marco_prueba_130x135.stl`)

![Vista previa](marco_prueba_preview.png)

Es el "marco de puerta" del cajón: solo el contorno exterior que tendría el cuerpo del cajón, con un poco de profundidad, para meterlo en el hueco y ver cómo encaja antes de imprimir el cajón entero.

| Parámetro | Valor | Por qué |
|---|---|---|
| Exterior | 129 × 134 mm | Hueco menos 0,5 mm de holgura por lado (1 mm en total) |
| Pared | 1,6 mm | 4 líneas con boquilla de 0,4: lo mínimo para que no se doble |
| Profundidad | 10 mm | Lo justo para que entre recto en el hueco y se pueda tocar |
| Escuadras interiores | 6 mm a 45° | Mantienen el marco a 90° y lo rigidizan sin apenas material |
| Chaflán en la base | 0,4 mm | Compensa la "pata de elefante" de la primera capa |
| Material | ≈ 9 cm³ ≈ 11 g de PLA | |

### Cómo imprimirlo

- Tumbado tal cual sale (10 mm de alto), **sin soportes**, sin balsa ni borde.
- Perímetros/paredes: 4 (así la pared es maciza y no hay relleno).
- Cabe en camas de 180 × 180 mm o más.

### Cómo leer la prueba

- **Entra y baila mucho** → bajar la holgura (`--holgura 0.3`).
- **Entra justo y desliza bien** → esa holgura es la buena para el cajón.
- **No entra o roza** → subir la holgura (`--holgura 0.8`) o medir el hueco en varios puntos (la madera no siempre es recta: mide arriba, en medio y abajo, y delante y al fondo).

## Regenerar con otras medidas

```bash
pip install manifold3d trimesh
python3 marco_prueba.py --holgura 0.8 --profundidad 15 --salida marco_h08.stl
python3 marco_prueba.py --help   # todos los parámetros
```
