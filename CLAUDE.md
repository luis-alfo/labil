# Memoria del proyecto

## Forma de trabajar con Luis

- Cada vez que Claude explique algo, debe guardarlo aquí, en "Aprendizajes": el objetivo es ir creando códigos compartidos y entender las realidades de Luis (de negocio y personales).
- Idioma de trabajo: español.

## Qué hay en este repositorio

- `src/`, `e2e/`… → Labil, editor de diagramas (Next.js + Supabase).
- `cajones-isla/` → proyecto de fabricación (impresión 3D): cajones para los huecos de la isla de la cocina. Ver su README.

## Aprendizajes

### Impresión 3D / prototipado (cajones de la isla, 2026-10)

- **Vocabulario compartido**
  - *Hueco*: el agujero de la estantería, 130 mm ancho × 135 mm alto (medido por Luis).
  - *Marco de prueba* (o "marco de puerta"): pieza que reproduce solo el contorno exterior del cajón, con poca profundidad, para probar el encaje gastando el mínimo plástico. Siempre se prototipa esto antes que el cajón entero.
  - *Holgura*: lo que se resta al hueco **por cada lado**. 0,5 mm por lado = 1 mm en total.
- **Criterios por defecto** (ajustables según la prueba)
  - Holgura de partida: 0,5 mm por lado para piezas que deslizan en madera.
  - Pared: 1,6 mm (4 líneas con boquilla 0,4) → pared maciza, sin relleno.
  - Escuadras a 45° en las esquinas interiores para que el marco no se deforme.
  - Chaflán de 0,4 mm en la base para la "pata de elefante" (la primera capa sale más ancha y falsearía la medida).
  - Imprimir tumbado, sin soportes.
- **Por qué 0,5 mm de holgura por lado (explicado a Luis)**: no es un número calculado, es un punto de partida que la prueba tiene que confirmar. Hay que absorber tres errores que se suman:
  1. *El hueco*: medido con flexómetro (±0,5 mm), y la madera no es perfectamente recta ni a escuadra, además de hincharse con la humedad.
  2. *La impresora*: suele fallar ±0,2–0,3 mm en 130 mm, y el PLA encoge un poco al enfriarse.
  3. *El deslizamiento*: sin guías, plástico contra madera necesita aire para no frenarse.
  Si es menos, se atasca con la humedad; si es más, el cajón baila y se tuerce al tirar.
- **La holgura no tiene que ser igual en todos los lados**: en vertical el cajón *se apoya* en la base del hueco, así que abajo la holgura es 0 y arriba se pone toda (1–2 mm). El marco de prueba la reparte centrada porque solo sirve para medir.
- **Frente superpuesto**: si el frente del cajón es algo más grande que el hueco, tapa la rendija y permite holguras generosas sin que se note. Es el truco de los muebles comerciales.
- **Modularidad (objetivo de Luis: que sirva al mudarse)** — se piensa en 3 capas:
  1. *Adaptador* (específico de cada mueble, barato, se reimprime al mudarse): la funda o las guías que se ajustan al hueco concreto y absorben su holgura. Va a presión o con cuñas, **sin tornillos en el mueble**.
  2. *Interfaz / enganche* (estándar fijo, no cambia nunca): el perfil de las guías y las medidas de unión. Es lo que hace intercambiables las piezas.
  3. *Módulos* (reutilizables): cuerpo del cajón en medidas de una rejilla fija, frente/tirador como pieza aparte, separadores interiores.
  - Uniones candidatas: cola de milano deslizante (estructural, sin tornillos), tornillo M3 + inserto roscado de calor (desmontable muchas veces), clips (rápidos pero se fatigan).
  - Rejilla candidata: *Gridfinity* (estándar abierto de 42 mm, con miles de organizadores ya diseñados). En un hueco de 130 mm caben justo 3 unidades por dentro (≈125,8 mm útiles con pared de 1,6 y holgura de 0,5); hay que verificarlo.
- **El mueble (foto de Luis, 2026-10-13)**: columna estrecha de 6 huecos apilados en el extremo de la isla, con estantes fijos, interior de tablero melaminado blanco y fondo cerrado. **Fondo útil: 35 cm.** Luis no sabe si pondrá cajón en todos. **Frente enrasado** (para ahorrar material).
  - El melamina es más estable que la madera maciza (apenas se hincha) y el PLA desliza bien sobre él, así que 0,5 mm por lado es razonable e incluso podría bajar.
  - El *marco de prueba* sirve también de **galga**: probarlo en los 6 huecos dice en 2 minutos si todos miden lo mismo.
- **Consecuencias de los 35 cm de fondo**
  - Un cajón entero no cabe en la cama de casi ninguna impresora (lo normal es 220–256 mm), así que hay que **partirlo en tramos**. Eso encaja con la modularidad: *frente + N tramos de cuerpo + uniones*. Al mudarse, con otro fondo se quitan o se añaden tramos.
  - Con frente enrasado hace falta un tope: el fondo del hueco hace de tope si el cajón mide 35 cm menos la holgura (hay que medir el fondo exacto).
  - Material aproximado por cajón (pared 1,6 mm): caja completa de 134 mm de alto ≈ 340 g de PLA; *bandeja* (frente completo + laterales de 60 mm) ≈ 220 g. Con fondo perforado se ahorra otro ~15–20 %.
  - **Fondo confirmado: 35 cm exactos** → el cajón mide 348 mm con el frente incluido (2 mm de aire atrás).
  - **Impresora de Luis: Bambu Lab A1** (cama de 256 × 256 × 256 mm). 348 mm no caben, así que van **2 tramos de ~174 mm**, que encajan de sobra.
  - *Bandeja con fondo perforado* (explicado a Luis, imagen en `cajones-isla/concepto_cajon_variantes.png`): el frente es completo, a la altura del hueco, para que desde fuera se vea igual que una caja. Detrás, los laterales son bajos (~60 mm) y el fondo lleva agujeros hexagonales que dejan una rejilla de nervios de unos 2,4 mm. Los hexágonos se imprimen sin soportes y rigidizan como un panal. Gasto medido: caja completa 352 g, bandeja 232 g, bandeja perforada 184 g de PLA. Cosas pequeñas (tornillos, pilas, gomas) se colarían por los agujeros de 14 mm.
  - **¿Están adaptados los conceptos a Gridfinity? No** (pregunta de Luis). Las 3 variantes se dimensionaron solo por el hueco. Así quedaría la versión Gridfinity:
    - *Ancho*: los cubos (bins) de 3 unidades ocupan 3 × 42 − 0,5 = 125,5 mm. Con pared de 1,6 mm el interior es de 125,8 mm (0,15 mm por lado: demasiado justo para la tolerancia de la impresora). Solución: laterales de 1,2 mm → interior de 126,6 mm (0,55 mm por lado), manteniendo la holgura de 0,5 con el hueco.
    - *Fondo*: interior ≈ 344 mm → caben **8 unidades (336 mm)**, y sobran ~8 mm para uniones. Cada tramo lleva 4 unidades (168 mm), así que la junta entre tramos coincide con la rejilla.
    - *Alto*: caben cubos de hasta ~17 unidades de altura (≈ 12 cm con el labio de apilado).
    - *Sinergia*: el suelo del cajón **es** la base Gridfinity (baseplate), una rejilla de celdas abiertas que ya es "fondo perforado" y gasta menos que los hexágonos. Como los cubos quedan anclados en la base, los laterales pueden bajar a un simple reborde (~20 mm). Estimación: frente + base + reborde ≈ 150 g por cajón, más los cubos.
    - *Contra*: con celdas abiertas, las cosas sueltas se caen; todo tiene que ir en cubos (o la base lleva suelo macizo, que gasta más).
    - *Encaje con la modularidad*: los cubos Gridfinity son la capa 3 más portable que existe (sirven en cajones, escritorios, cualquier casa), y hay miles de diseños gratuitos.
  - **Concepto Gridfinity modelado** (`cajones-isla/concepto_gridfinity.png`, script en `cajones-isla/conceptos/`): 3 × 8 unidades, base de celdas abiertas, reborde de 20 mm y laterales de 1,2 mm. Tramo 1 con frente de 176 mm y tramo 2 de 172 mm (la unión cae en la rejilla). **Cajón con frente gola ≈ 125 g de PLA** (sin contar los cubos).
    - El perfil de la base está aproximado a la especificación de Gridfinity (0,7 + 1,8 + 2,15 mm). Antes de imprimir el cajón hay que validarlo con un cubo Gridfinity real.
  - **Propuestas de "puerta"** (= frente enrasado; imagen `cajones-isla/propuestas_frente.png`):
    1. *Muesca*: semicírculo arriba, ≈ 45 g.
    2. *Gola*: el tercio superior va retranqueado 18 mm y los dedos entran por delante. Encaja con los muebles sin tirador de la cocina de Luis. ≈ 48 g.
    3. *Agujero de dedo*: óvalo a media altura, ≈ 42 g.
    4. *Ranura*: línea horizontal cerca del borde superior, ≈ 41 g.
    5. *Calado*: panal hexagonal, se ve el contenido, ≈ 27 g.
  - **Despiece y coste** (PLA a 20 €/kg = 0,02 €/g; gramos del modelo, el laminador suele sumar un 5–10 %):
    - Por cajón: tramo 1 (4 filas + reborde) 32,5 g / 0,65 € · tramo 2 (4 filas + reborde + tope) 44,8 g / 0,90 € · frente (pieza aparte, intercambiable): muesca 44,6 g / 0,89 €, gola 48,1 g / 0,96 €, agujero 41,7 g / 0,83 €, ranura 41,3 g / 0,83 €, calado 26,5 g / 0,53 € · uniones de cola de milano integradas en los tramos (sin modelar, ~2–3 g).
    - **Cajón con gola ≈ 125 g ≈ 2,51 €; los 6 cajones ≈ 752 g ≈ 15 €.**
    - Cubos Gridfinity (pared y suelo de 1,2 mm, pie hueco): 1×1×3u 7 g · 1×1×6u 12 g · 2×1×6u 20 g · 3×1×3u 18 g · 3×1×6u 28 g · 2×2×6u 32 g · 3×2×4u 35 g · 1×2×12u 35 g. El juego de ejemplo de la imagen pesa ≈ 159 g ≈ 3,19 €.
    - Pruebas: marco 11 g / 0,22 € · muestra (frente gola + 1 fila de base) 56,5 g / 1,13 €.
  - **Cuidado estructural**: con reborde bajo y frente alto, tirar desde arriba hace palanca sobre la unión frente–base. Por eso llevan nervios traseros, y cuanto más bajo está el tirador, menos esfuerzo. El *calado* va sin nervios y sería el más flojo.
  - *Tirador*: una muesca semicircular arriba del frente, que no gasta material extra y no sobresale.
  - *Patines*: dos carriles de ~1 mm bajo el cajón reducen el rozamiento y el polvo que frena, y fijan la holgura de abajo.
- **Herramienta**: los modelos se generan con scripts Python paramétricos (`manifold3d` + `trimesh`) para poder iterar cambiando solo números.
- **Estado**: paso 1 hecho (marco de prueba 129 × 134 × 10 mm, ≈ 11 g). Pendiente: resultado de la prueba de encaje de Luis → fijar holgura → definir la interfaz estándar (capa 2) → diseñar el cajón. Datos que faltan: qué se va a guardar (altura y tamaño de las cosas → caja, bandeja o bandeja perforada) y si los 6 huecos miden igual (probar el marco en todos).
