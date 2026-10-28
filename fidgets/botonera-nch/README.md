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

## v6: compacta 24 mm, 2 mm de recorrido (en prueba) — `boton_v6_piezas.3mf`
Igual que la v5 (✅ probada) pero 24 × 24 mm (2×2 ≈ 48 mm) y tecla de 15 mm.
Resorte de 2 brazos de 1,0 mm que dan ~1,4 vueltas: 2 mm de recorrido con la misma
tensión que la v5 (0,5 %). Ajustes en `generar_v6.py`.

## v5: 3 piezas que encajan (✅ probada) — `boton_v5_piezas.3mf`
Tras romperse los brazos de la v4. Un botón de prueba en 3 piezas impresas:
- **Resorte**: plano sobre la cama, 3 brazos en espiral de 300° (largos = poca tensión), pensado para PLA.
- **Carcasa** y **tecla**: boca abajo; la tecla tiene una valona a 45° que la retiene bajo la tapa.
Montaje: mete la tecla por debajo de la carcasa, luego encaja el resorte a presión
(brazos hacia la tecla) haciendo entrar el pivote en el agujero del buje.
Ajustes en `generar_v5.py`: `GIRO_BRAZO`, `ANCHO_BRAZO`, `GROSOR_BRAZO` (dureza), `AJUSTE` (encaje).

## v4: mecanismo oculto (descartada: brazos rotos) — `botonera_nch_v4_color.3mf`
58 × 58 × 18 mm. Igual que la v3 pero con resorte compacto (3 brazos) y cada
forma del logo es una **tecla de 20 mm que tapa todo el mecanismo**. La tecla
se une al disco por un vástago con cono a ~55° por debajo: sin soportes.
Prueba de un botón: `prueba_boton_v4.3mf`. Ajustes en `generar_v4.py`.

## v3: botón que baja entero — `botonera_nch_v3_color.3mf`
58 × 58 × 12 mm. Cada forma va sobre un disco unido a la tapa por **4 brazos en
espiral**: al pulsar, el disco baja recto y paralelo (sin bisagra) y recupera solo.
Dos cuchillas con diente bajo el disco dan el clic al bajar y al soltar.
Ajustes en `generar_v3.py`: `BRAZO` / `ARCO_BRAZO` (dureza del resorte),
`SOLAPE` (fuerza del clic), `HOLGURA`.

## v2: clic real (`botonera_nch_v2.3mf`)
Bajo el borde libre de cada lengüeta hay una cuchilla vertical impresa con un
diente en cuña (0,5 mm de solape). Al pulsar, la lengüeta empuja el diente, la
cuchilla cede y vuelve de golpe: **clic al bajar y otro al soltar**.
Sigue siendo una sola pieza, sin muelles ni piezas extra.
Ajustes en `generar_v2.py`: `SOLAPE` (fuerza del clic), `CUCHILLA` (dureza),
`HUECO_Z` (holgura vertical; súbela a 0,6 si el diente se pega a la lengüeta).

## Bicolor (`botonera_nch_v2_color.3mf`)
Dos piezas ya asignadas: **fondo → filamento 1**, **logo → filamento 2**.
- Con AMS lite: abre y lamina, los colores ya están puestos.
- Sin AMS: el logo solo está por encima de 9 mm, así que basta un cambio de
  filamento en esa capa (clic derecho en la barra de capas → *Añadir cambio de filamento*).
Colores en `exportar_color.py` (`COLOR_BASE`, `COLOR_LOGO`).

## Imprimir en Bambu Lab A1 (PLA)
- Capa 0,2 mm, 2 paredes, relleno 15 %, **sin soportes** (los techos son puentes cortos de ~22 mm).
- Base en la cama, botones hacia arriba (orientación del archivo).
- Al terminar, pulsa cada botón con firmeza un par de veces para soltar la lengüeta.

## Ajustes (en `generar.py`)
- `TAPA` (1,2 mm): más fino = botón más blando; más grueso = más duro.
- `RANURA` (0,8 mm): holgura alrededor de la lengüeta; súbela si se queda pegada.

Regenerar: `pip install trimesh manifold3d numpy && python3 generar.py`
