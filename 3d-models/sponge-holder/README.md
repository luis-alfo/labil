# Sponge holder (kitchen faucet clip + sponge pinch clip)

Soporte para esponja: clip que abraza un cilindro vertical del grifo (Ø 45 mm),
brazo horizontal por detrás, giro de 90° y **pinza en C** que sujeta la
esponja por su canto superior pellizcándola con un hueco menor de 2 cm.

## Files

- `sponge_holder.scad`    — fuente paramétrica de OpenSCAD.
- `generate_stl.py`       — generador en Python (`trimesh` + `shapely` + `manifold3d`).
- `sponge_holder.stl`     — STL completo, listo para imprimir.
- `test_faucet_clip.py`   — genera solo la abrazadera del grifo (MVP de prueba).
- `test_faucet_clip.stl`  — STL aislado de la abrazadera (40 × 53 × 22 mm, ~9 cm³).
- `test_sponge_clip.py`   — genera solo la pinza de la esponja (MVP de prueba).
- `test_sponge_clip.stl`  — STL aislado de la pinza (22 × 50 × 15 mm, ~7 cm³).

## Generar los STL

```
pip install numpy-stl trimesh shapely manifold3d
python3 generate_stl.py        # pieza completa
python3 test_faucet_clip.py    # solo abrazadera, para test de agarre
python3 test_sponge_clip.py    # solo pinza, para test de agarre de esponja
```

O con OpenSCAD:

```
openscad -o sponge_holder.stl sponge_holder.scad
```

## Flujo recomendado: probar antes de imprimir la pieza entera

Antes de comprometer 1 h 15 min de impresión en la pieza grande, imprime
los dos test pieces (≈ 15 min cada uno):

1. **`test_faucet_clip.stl`** — comprueba que la abrazadera entra a presión
   sobre el cilindro de 45 mm del grifo. Si va apretada/floja, ajusta
   `CLIP_INNER_D` y vuelve a generar.
2. **`test_sponge_clip.stl`** — comprueba que la esponja se queda bien sujeta
   en la pinza. Si se cae o cuesta meterla, ajusta `SPONGE_GAP` o
   `SPONGE_CLIP_LEN_Y`.
3. Cuando ambos test pasen, regenera y imprime `sponge_holder.stl`.

## Dimensiones actuales

- Bounding box: **88 × 53 × 42 mm**
- Volumen plástico: ~22 cm³ (≈ 27 g de PLA al 30 % gyroid)
- Giro de 90° con fillet de **8 mm** (curva en lugar de esquina viva)

## Parámetros

Edita la cabecera de cualquiera de los dos archivos.

| Parámetro              | Valor   | Significado                                                           |
| ---------------------- | ------- | --------------------------------------------------------------------- |
| `WALL_T`               | 4 mm    | grosor de pared                                                       |
| `CLIP_INNER_D`         | 45.4 mm | 45 mm + 0.4 mm de holgura para PLA                                    |
| `CLIP_HEIGHT`          | 22 mm   | altura del anillo del clip                                            |
| `CLIP_WRAP_DEG`        | 240°    | envoltura del anillo (boca = 120°). Más bajo = más flex, menos grip   |
| `ARM_LEN`              | 30 mm   | longitud del brazo horizontal (clip → inicio del fillet)              |
| `ARM_WIDTH_Y`          | 24 mm   | ancho uniforme del brazo + codo + bajada                              |
| `ELBOW_R`              | 8 mm    | radio del fillet del giro de 90° (más alto = más elegante)            |
| `DROP_LEN`             | 18 mm   | bajada vertical (fin del fillet → fondo)                              |
| `SPONGE_GAP`           | 14 mm   | hueco interior de la pinza de esponja (< 2 cm para pellizcar)         |
| `SPONGE_CLIP_LEN_Y`    | 50 mm   | longitud de la pinza a lo largo del canto de la esponja               |
| `SPONGE_CLIP_WRAP_DEG` | 220°    | envoltura de la pinza (boca = 140°)                                   |

## Recomendaciones de impresión (PLA)

- **Material:** PLA (según indicación). Ojo: PLA es rígido; ambos clips
  tienen flex limitado, por eso `CLIP_WRAP_DEG` está bajado a 240° y
  `SPONGE_CLIP_WRAP_DEG` a 220° para que abran al meter el grifo / la
  esponja sin partirse.
- **Orientación:** apoya la pieza sobre el lateral (plano XZ), con el eje
  del clip principal paralelo a la cama. Las líneas de capa quedan
  perpendiculares a la fuerza de cierre del clip, que es lo que aguanta.
- **Soportes:** sí, debajo del brazo horizontal y bajo la pinza de la
  esponja. PrusaSlicer/Cura los detectan automáticamente.
- **Perímetros / relleno:** 4 perímetros, 30–40 % gyroid.
- **Capa:** 0.2 mm.

## Cómo usarlo

1. Abrir el clip principal y meterlo a presión sobre el cilindro del grifo
   (Ø 45 mm). El brazo queda detrás del grifo.
2. Empujar la esponja hacia arriba contra la pinza inferior: el hueco de
   14 mm comprime los 25 mm de la esponja, y la fricción la sujeta.
3. Cuelga vertical, con el agua escurriendo dentro del fregadero.

## Si algo no encaja

- **Clip muy apretado** → sube `CLIP_INNER_D` en pasos de 0.2 mm.
- **Clip muy flojo** → baja `CLIP_INNER_D` o sube `CLIP_WRAP_DEG`.
- **El clip se rompe al ponerlo** → baja `CLIP_WRAP_DEG` (más flex) o
  cambia a PETG.
- **La esponja se sale** → baja `SPONGE_GAP` (más pellizco) o sube
  `SPONGE_CLIP_LEN_Y` para más superficie de fricción.
