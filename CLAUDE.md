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
  - **Frente elegido para ver en detalle: agujero de dedo** (imagen `cajones-isla/cajon_agujero.png`, despiece y montado sin cubos): frente 42 g + tramo 1 32 g + tramo 2 45 g = **≈ 119 g ≈ 2,38 €** por cajón.
  - **Uniones (v2): "llave de mariposa" bajo los patines** (`cajones-isla/uniones.png`, modelo en `cajones-isla/conceptos/cajon.py`):
    - Bajo la base corren **2 patines** de 6 × 3 mm, colocados justo bajo los nervios longitudinales de la base (x = ±21), para que la carga baje recta. Sirven también de patines de deslizamiento y de larguero.
    - **Todas las piezas llevan el mismo alojamiento hembra** (media cola de milano abierta por abajo, 2,6 mm de hondo y techo de 0,4) en cada extremo. Una **llave suelta** (doble cola de milano: cuello 7, cabeza 11, 2 × 7 mm de largo, 2,4 mm de grueso, 0,4 g) cruza cada junta. Son 4 llaves por cajón.
    - Montaje: con las piezas boca abajo se meten las llaves y se da la vuelta al cajón. En el hueco, el estante encierra las llaves por debajo y no se pueden caer. Tirar del cajón no lo separa.
    - Ventaja frente a la v1 (lengüeta macho en una pieza y hembra en otra): **cualquier tramo encaja con cualquiera, en cualquier orden**. Para otro fondo basta con añadir tramos. La llave es la pieza estándar barata de la *capa 2*.
    - Juego por defecto: 0,2 mm por lado en el alojamiento. **Probeta** `cajones-isla/prueba_union_llave_mariposa.stl`: 3 juntas (0,1 / 0,2 / 0,3 mm, marcadas con 1, 2 o 3 muescas), con los alojamientos contra la cama como en los tramos, ≈ 4 g / 0,08 €.
    - Coste: cajón completo ≈ **149 g ≈ 2,98 €** (frente ≈ 45 g, tramo 1 ≈ 44 g, tramo 2 ≈ 59 g, llaves 1,5 g).
  - **Investigación: cómo se unen otros sistemas Gridfinity** (pregunta de Luis, 2026-10-13):
    1. *Tornillos*: la base "screw together" original de Zack Freedman (tornillo 4-40 + inserto), gridfinity-rebuilt de kennetek (estilo screw_together) y Modular Baseplates (M3×8 + tuerca, el tornillo hace de imán para los cubos). Muy firme, pero necesita herrajes.
    2. *Colas de milano integradas en la pieza*: Clickfinity (conectores M y W en los lados; importa la orientación; tornillo autorroscante M2/M2,5 opcional).
    3. *Conector suelto*: Pressure-fit collection (bordes macho, hembra o liso, y una pieza suelta que une dos hembras) y GRIPS (pestañas entrelazadas).
    4. *Conectores X por debajo*: los generadores de base partida para cajones (MakerWorld "Drawer Baseplate Auto-Split") parten la base al tamaño de la cama y la unen con piezas en X bajo los cruces, sin herramientas.
    5. *Cajoneras Gridfinity completas* (GEN2 Classic Drawer, Gridfinity Hardware Storage System, generadores paramétricos): usan carriles y armazón propio. No aplican a un hueco existente.
    - Conclusión: nuestra llave de mariposa bajo los patines es la idea de los puntos 3 y 4 (conector suelto, por debajo y sin herramientas), adaptada a un cajón que desliza.
  - **Decisión de Luis (2026-10-14): base Clickfinity real + frente de 3 voltes sin vigas** ("para que no inventes nada"). Luis pasó el ZIP oficial (NoWarrenty, remix de jerrymk; licencia **CC BY-NC-SA 4.0**: uso personal y remezcla con atribución, sin uso comercial). Analizado con su geometría real:
    - La placa mide **4 mm de alto**: es el perfil Gridfinity estándar (0,7 + 1,8 mm) truncado arriba (1,5 en vez de 2,15). Sujeta los cubos con **4 brazos elásticos por celda** ("clic"), sin imanes.
    - **Cada placa lleva nervios completos también en el borde exterior** y orejas de cola de milano: orejas M de 5,5 mm en los lados y W de 3 mm arriba y abajo. Por eso dos placas no se pueden poner pegadas: **se unen dejando una fila o columna libre**, que cierran los conectores (`join_*`), y esa fila también tiene brazos de clic. Verificado: el conector encaja con holgura 0 (cualquier desplazamiento de 0,3 mm ya interfiere).
    - **Choque con el hueco**: una placa de 3 columnas mide 131,7 mm sin orejas (137 con orejas) y el hueco mide 130. Solución: recortar a x ∈ [-0,2; 126,2]. Se quita el medio nervio exterior, que solo serviría para una celda vecina inexistente, y se conservan el chaflán interior y los brazos de cada celda. Los laterales de la bandeja bajan a 1,0 mm (interior de 127).
    - Reparto de las 8 filas: **placa 3x4 + fila de conectores + placa 3x3** (ninguna pieza supera los 256 mm de la A1). Los 4 conectores van en la fila libre; los 2 exteriores, recortados igual que las placas.
    - **El autor pide PETG/ABS/ASA, no PLA**: el PLA cede con carga constante (*creep*) y los brazos pierden agarre. → Placas y conectores en PETG; bandeja y frente pueden ir en PLA.
    - Las mallas derivadas de Clickfinity **no se suben al repo** (licencia): se generan con `conceptos/cajon_click.py <zip>` en `cajones-isla/clickfinity_local/` (ignorada por git).
  - **Cajón v1 para imprimir** (`cajones-isla/stl/`, imagen `cajon_clickfinity.png`, modelo `conceptos/cajon_click.py`):
    - Bandeja propia: suelo de tiras de 6 × 1,2 mm bajo todas las líneas de la rejilla (las placas apoyan sus nervios), patines y llaves de mariposa como antes, reborde de 20 mm, laterales de 1,0 mm. Tramo A de 192 mm y tramo B de 154 mm: la junta va en mitad de la fila de conectores (y = 194,3).
    - Frente `revoltons3` con línea de sombra; los nervios traseros empiezan por encima de la placa (z ≥ 8,6) y tienen 3 mm de fondo para no tocar sus orejas.
    - Peso: frente 43 g + tramo A 30 g + tramo B 35 g + llaves 1,5 g ≈ **109 g de PLA (2,19 €)** + Clickfinity ≈ **35 g de PETG (0,69 €)** ≈ **2,9 € por cajón**.
    - Comprobado en el modelo: ninguna pieza choca con otra (incluidas placas, conectores y llaves) y todas caben en la A1.
  - **Orientación de impresión**: el frente se imprime **boca abajo** (la cara vista sobre la cama de PEI texturizada de la A1 sale mate y uniforme). Así la tracción del tirón va entre capas, pero los esfuerzos son mínimos (un cajón se abre con 10–20 N). Los tramos se imprimen con la base sobre la cama. Ninguna pieza necesita soportes.
  - **Estética de la puerta** (`cajones-isla/puertas_estetica.png`):
    - *Línea de sombra*: radio de 2 mm en las esquinas y chaflán de 1 mm en las aristas de la cara y de la abertura. Hace que la rendija con el hueco parezca intencionada; es el truco que más mejora por menos. Es mejor chaflán que redondeo porque, boca abajo, el redondeo en la cara de la cama no se imprime bien.
    - Aberturas: óvalo, píldora fina, bolsillo (cajita trasera de 6,8 mm; no se ve el interior), onda superior, círculo, **volta** y **revoltons**.
    - **Revoltons sin vigas** (`cajones-isla/revoltons.png`, pedido por Luis): una sola abertura de base recta cuyo techo son 2, 3 o 4 voltes seguidas, con los valles redondeados (r 1,5). Caben los dedos como en la volta y se lee como el techo de revoltons. Variantes `revoltons2/3/4` en `cajon.py`; ≈ 44 g.
  - **El piso de Luis tiene voltes catalanes** (techo de bóveda tabicada). Lo usamos como lenguaje de diseño: la *volta* es un arco rebajado (flecha ≈ 1/5 de la luz) sobre arranques rectos; los *revoltons* son tres voltes pequeñas separadas por "vigas", como el techo visto desde abajo.
  - **Cuidado estructural**: con reborde bajo y frente alto, tirar desde arriba hace palanca sobre la unión frente–base. Por eso llevan nervios traseros, y cuanto más bajo está el tirador, menos esfuerzo. El *calado* va sin nervios y sería el más flojo.
  - *Tirador*: una muesca semicircular arriba del frente, que no gasta material extra y no sobresale.
  - *Patines*: dos carriles de ~1 mm bajo el cajón reducen el rozamiento y el polvo que frena, y fijan la holgura de abajo.
- **Herramienta**: los modelos se generan con scripts Python paramétricos (`manifold3d` + `trimesh`) para poder iterar cambiando solo números.
- **Estado (2026-10-14)**: diseño v1 completo con Clickfinity real y frente de 3 voltes, STL listos. Pendiente de validar en físico: (1) el marco de prueba en los 6 huecos, (2) la probeta de las llaves (juego 0,1 / 0,2 / 0,3), (3) el clic de los conectores Clickfinity en PETG. Después, imprimir un cajón completo.
