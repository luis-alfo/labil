# Sponge holder (kitchen faucet clip) — 3D version

Soporte para esponja que se engancha al grifo. Clip horizontal (eje vertical,
paralelo al suelo) que aprieta a presión un elemento vertical del grifo,
un brazo horizontal corto, un giro de 90°, y una **cesta vertical** donde
la esponja se apoya **de pie** (eje largo perpendicular al suelo).

## Files

- `sponge_holder.scad` — fuente paramétrica de OpenSCAD.
- `generate_stl.py`    — generador en Python (`trimesh` + `shapely` + `manifold3d`)
                         que produce el STL sin necesidad de OpenSCAD.
- `sponge_holder.stl`  — STL listo para imprimir (regenerable).

## Generate the STL

Sin OpenSCAD instalado:

```
pip install numpy-stl trimesh shapely manifold3d
python3 generate_stl.py
```

Con OpenSCAD:

```
openscad -o sponge_holder.stl sponge_holder.scad
```

## Parámetros

Edita la cabecera de cualquiera de los dos archivos.

| Parámetro         | Valor   | Significado                                               |
| ----------------- | ------- | --------------------------------------------------------- |
| `WALL_T`          | 4 mm    | grosor de pared en toda la pieza                          |
| `CLIP_INNER_D`    | 18 mm   | diámetro interior del clip (debe ser **< 20 mm** para pinza) |
| `CLIP_HEIGHT`     | 18 mm   | altura del clip a lo largo de su eje (Z)                  |
| `CLIP_WRAP_DEG`   | 280°    | ángulo de envoltura (>180° = snap-on a presión)           |
| `ARM_LEN`         | 30 mm   | longitud del brazo horizontal del clip a la cesta         |
| `ARM_WIDTH_Y`     | 18 mm   | ancho del brazo (Y)                                       |
| `DROP_LEN`        | 22 mm   | bajada vertical (el "giro" de 90°)                        |
| `CRADLE_WIDTH_Y`  | 30 mm   | **ancho de la cesta** — más ancho que el clip             |
| `CRADLE_BACK_H`   | 80 mm   | pared trasera de la cesta (vertical, donde apoya la esponja) |
| `CRADLE_BOT_LEN`  | 32 mm   | fondo de la cesta (≈ grosor de la esponja + paredes)      |
| `CRADLE_FRONT_H`  | 37 mm   | labio frontal (sujeta la esponja para que no caiga)       |

## Recomendaciones de impresión

- **Material:** PETG o TPU 95A. PLA funciona pero el clip puede romperse al
  poner/quitar la esponja muchas veces.
- **Orientación:** apoya la pieza sobre el lateral (el plano XZ),
  con el eje del clip paralelo a la cama. Así las líneas de capa van
  perpendiculares a la fuerza de cierre del clip.
- **Soportes:** sí, debajo del brazo horizontal y el fondo de la cesta.
  Algunos slicers (PrusaSlicer, Cura) los detectan automáticamente.
- **Perímetros / relleno:** 4 perímetros, 30–40 % de relleno gyroid.
- **Capa:** 0,2 mm.

## Pendientes — qué necesito de ti para afinar

1. **Diámetro real** del elemento del grifo donde va el clip. Mídelo con
   calibre y ajusta `CLIP_INNER_D` (deja −0,3 mm de holgura para PLA/PETG, 0
   o incluso −0,5 mm para TPU).
2. **¿El brazo y la bajada van por delante, por detrás o por el lado** del
   grifo? (cambia el signo de `ARM_LEN` o rota el clip si hace falta).
3. **Tamaño de la esponja** (largo × ancho × grosor) → ajusta
   `CRADLE_WIDTH_Y`, `CRADLE_BOT_LEN` y `CRADLE_BACK_H`.
4. **Material** elegido → afecta a la holgura del clip y a si conviene
   subir/bajar `CLIP_WRAP_DEG`.
