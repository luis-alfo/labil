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
- **Herramienta**: los modelos se generan con scripts Python paramétricos (`manifold3d` + `trimesh`) para poder iterar cambiando solo números.
- **Estado**: paso 1 hecho (marco de prueba 129 × 134 × 10 mm, ≈ 11 g). Pendiente: resultado de la prueba de encaje de Luis → fijar holgura → definir la interfaz estándar (capa 2) → diseñar el cajón. Datos que faltan: profundidad del hueco, material de la estantería, cuántos huecos hay, frente enrasado o superpuesto.
