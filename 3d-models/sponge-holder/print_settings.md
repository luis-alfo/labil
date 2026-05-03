# Settings de impresión — sponge_holder (pieza completa)

Recomendaciones para imprimir `sponge_holder.stl` o `sponge_holder.3mf`
de forma que aguante el uso real (estropajo + agua + colocar/quitar
varias veces al día) sin partirse.

## Tabla rápida

| Ajuste | PLA (recomendado) | PETG (más duradero) |
| --- | --- | --- |
| Altura de capa | 0.20 mm | 0.20 mm |
| Nozzle | 0.4 mm | 0.4 mm |
| Temperatura nozzle | **215 °C** | 240 °C |
| Temperatura cama | 60 °C | 80 °C |
| Perímetros / walls | **5** | 4 |
| Capas Top / Bottom | 4 | 4 |
| Relleno | **35 % gyroid** | 30 % gyroid |
| Velocidad perímetro externo | 30 mm/s | 25 mm/s |
| Velocidad perímetros internos / relleno | 50 mm/s | 40 mm/s |
| Velocidad primera capa | 20 mm/s | 20 mm/s |
| Ventilador | 100 % desde capa 3 | 30–50 % |
| Brim | **8 mm** | 8 mm |
| Soportes | **Árbol, touching build plate only** | igual |
| Z-distancia soporte | 0.20 mm | 0.20 mm |

Tiempo estimado: **~1 h 20 min**. Material: **~26 g**.
Bounding box: **87 × 55 × 56 mm**.

## Orientación

**Imprime tal cual viene en el STL/3MF** — el clip del grifo arriba (eje
vertical) y la pinza-tenedor abajo. Es la mejor orientación para el
componente más cargado, **el clip del grifo**:

- Las líneas de capa quedan **circunferenciales en el anillo** del clip.
  Cuando lo abres para meterlo en el grifo, la tensión va en la
  dirección de la fibra → máxima resistencia al snap.
- Las paredes finas del clip flexan sin delaminarse.

**Trade-off conocido:** los prongs de la pinza-tenedor abajo no quedan
en su orientación óptima (la flex tira de la adhesión entre capas).
Compensación:
- **5 perímetros** en lugar de 4 → cada prong tiene casi 6 mm de pared
  sólida, mucha más sección sin depender de la unión entre capas.
- **215 °C** (lado alto del rango PLA) → mejor adhesión entre capas.
- **30 mm/s en perímetro externo** → cada línea se asienta caliente
  sobre la anterior.

Si tras unas semanas notas que un prong pierde fuerza, **reimprime en
PETG** con los mismos ajustes; aguanta varios años.

## Soportes — qué soporta qué

Activa **árbol / tree supports** con "touching build plate only" y
deja que el slicer detecte automáticamente. Lo normal es que coloque
soportes en estos dos sitios:

1. **Bajo el brazo horizontal trasero** — voladizo de 30 mm casi
   plano, no se imprime sin soporte.
2. **Bajo el arco de la pinza-tenedor** — el arco semicilíndrico apoya
   sobre los prongs y la base de la cavidad necesita soporte.

El interior del clip del grifo (el hueco del anillo) **no** necesita
soporte: es un agujero pasante con eje vertical.

## Adherencia — el punto débil

Las puntas de los prongs son los únicos puntos de contacto con la
cama (10 puntas, ~115 mm² total). Si saltan:

- Asegúrate de que la cama está **bien nivelada y limpia** (alcohol
  isopropílico para quitar grasa).
- **Brim 8 mm**, todo perímetro.
- Primera capa **muy lenta** (20 mm/s) y un pelín aplastada (Live-Z
  -0.05 mm si usas Prusa).
- Si es invierno, cierra puertas y ventanas — corrientes de aire en la
  cama → warping.

## Cómo probar antes de imprimir el todo

Antes de comprometer 1 h 30 min:

1. Imprime **`test_faucet_clip.stl`** (~15 min). Comprueba snap-fit en
   el grifo Ø 45 mm. Si va apretado, sube `CLIP_INNER_D` 0.2 mm en
   `generate_stl.py` y regenera.
2. Imprime **`test_sponge_v_fork.stl`** (~12 min). Comprueba que la
   esponja entra sin partir un prong y queda agarrada. Si la pinza
   queda floja, baja `PINCH_GAP_BOTTOM` 1 mm. Si cuesta meterla,
   sube `PINCH_GAP_BOTTOM` 1 mm o baja `PINCH_NUM_PRONGS` a 4.
3. Cuando los dos test pasen, regenera y manda a imprimir
   `sponge_holder.stl` (o `.3mf`).

## Tabla de ajustes si algo falla

| Síntoma post-impresión | Ajuste primero |
| --- | --- |
| Clip del grifo crash al meterlo | Sube `CLIP_WRAP_DEG` a 220° (más boca, menos abrazo) |
| Clip del grifo se cae solo | Baja `CLIP_INNER_D` 0.2 mm |
| Prong se rompe al meter esponja | Imprime en PETG, o sube `PINCH_WALL_T` a 4 mm |
| Esponja se sale | Baja `PINCH_GAP_BOTTOM` 1 mm |
| Esponja imposible de meter | Sube `PINCH_GAP_BOTTOM` 1 mm |
| Brazo cede con peso de esponja húmeda | Sube `WALL_T` (brazo) a 5 mm — regenera |

## STL vs 3MF — cuál usar

- **`.stl`**: universal, todo slicer lo abre. Usa este si no estás
  seguro.
- **`.3mf`**: incluye unidades correctas (mm) y orientación. Slicers
  modernos (PrusaSlicer, OrcaSlicer, Bambu Studio) lo prefieren — la
  pieza llega ya orientada como se diseñó. Settings de impresión NO
  van embebidos (eso es específico de cada slicer); aplícalos
  manualmente desde esta tabla.
