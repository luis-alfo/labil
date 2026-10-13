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
  - *Tirador*: una muesca semicircular arriba del frente, que no gasta material extra y no sobresale.
  - *Patines*: dos carriles de ~1 mm bajo el cajón reducen el rozamiento y el polvo que frena, y fijan la holgura de abajo.
- **Herramienta**: los modelos se generan con scripts Python paramétricos (`manifold3d` + `trimesh`) para poder iterar cambiando solo números.
- **Estado**: paso 1 hecho (marco de prueba 129 × 134 × 10 mm, ≈ 11 g). Pendiente: resultado de la prueba de encaje de Luis → fijar holgura → definir la interfaz estándar (capa 2) → diseñar el cajón. Datos que faltan: qué se va a guardar (altura y tamaño de las cosas → caja, bandeja o bandeja perforada) y si los 6 huecos miden igual (probar el marco en todos).
