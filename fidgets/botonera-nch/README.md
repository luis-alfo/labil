# Botonera NocodeHackers (fidget print-in-place)

Fidget de 50 × 50 × 12 mm con las 4 formas del icono de NocodeHackers como botones.
**100 % impreso**: sin muelles, imanes ni rodamientos. Cada botón va sobre una
lengüeta de la tapa recortada en U, que flexa al pulsar y recupera sola.

| Archivo | Para qué |
|---|---|
| `botonera_nch.3mf` | Abrir directamente en Bambu Studio |
| `botonera_nch.stl` | Cualquier otro slicer |
| `generar.py` | Modelo paramétrico (regenera STL y 3MF) |
| `preview.png` | Vista previa |

## v2: clic real (`botonera_nch_v2.3mf`)
Bajo el borde libre de cada lengüeta hay una cuchilla vertical impresa con un
diente en cuña (0,5 mm de solape). Al pulsar, la lengüeta empuja el diente, la
cuchilla cede y vuelve de golpe: **clic al bajar y otro al soltar**.
Sigue siendo una sola pieza, sin muelles ni piezas extra.
Ajustes en `generar_v2.py`: `SOLAPE` (fuerza del clic), `CUCHILLA` (dureza),
`HUECO_Z` (holgura vertical; súbela a 0,6 si el diente se pega a la lengüeta).

## Imprimir en Bambu Lab A1 (PLA)
- Capa 0,2 mm, 2 paredes, relleno 15 %, **sin soportes** (los techos son puentes cortos de ~22 mm).
- Base en la cama, botones hacia arriba (orientación del archivo).
- Al terminar, pulsa cada botón con firmeza un par de veces para soltar la lengüeta.

## Ajustes (en `generar.py`)
- `TAPA` (1,2 mm): más fino = botón más blando; más grueso = más duro.
- `RANURA` (0,8 mm): holgura alrededor de la lengüeta; súbela si se queda pegada.

Regenerar: `pip install trimesh manifold3d numpy && python3 generar.py`
