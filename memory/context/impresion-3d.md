# Impresión 3D

## Equipo
| Qué | Detalle |
|-----|---------|
| Impresora | **Bambu Lab A1** (cama 256 × 256 mm). No es la A1 mini. Anotado el 1 nov 2026. |
| Boquilla | 0,4 mm |
| Multicolor | AMS lite (hasta 4 filamentos) |
| Placa | PEI texturizada (la de serie): la cara de abajo sale texturizada |
| Laminador | Bambu Studio |
| Filamento | Bambu PLA Basic |

## Cómo entregar piezas
- Proyecto `.3mf` de Bambu Studio para la A1 con perfil "Bambu Lab A1 0.4 nozzle", proceso "0.20mm Standard @BBL A1" y "Bambu PLA Basic @BBL A1".
- Cada pieza de color como parte del mismo objeto, con su filamento ya asignado.
- Ajustes para llaveros: capas de 0,2 mm, 4 perímetros, relleno 100 %, paredes Arachne, torre de purga.
- Comprobar antes de entregar: mallas cerradas, sin solapes entre colores, dentro de la cama.

## Reglas aprendidas (PLA, boquilla 0,4)
- **Trazo mínimo de 0,9 mm** en letras en relieve. Con 0,5 mm salen bolitas sueltas.
- **Hueco mínimo de 0,5 mm** entre letras. Si no, se funden.
- Un logo como el de ST26 no baja de unos 24–26 mm de ancho sin fundir letras.
- Imprimir plano; la carga a lo largo de las capas.
- **Pared mínima de 3 mm** alrededor de agujeros que cargan. Si no cabe, compensar con más grosor.
- Las capas de otro color en una zona que carga no cuentan como resistencia.
- Colocar la argolla en la dirección en la que se tira (sin palanca).
- **Agujero de la argolla:** un túnel recto y grueso impide que la anilla se incline. Una llave típica deja inclinarse ≈ 46–52°. Para igualarla en piezas de 4,4 mm: bisel de 1 mm a 45° por las dos caras y ojal alargado (3,5 × 7 mm) en la dirección del giro.
- Color en las dos caras sin rellenar por dentro: incrustación a ras en las 4 primeras capas (0,8 mm) de la cara de la cama, en espejo.
- PLA se deforma por encima de ~55 °C (coche al sol): para eso, PETG.

## Fuerzas de uso de un llavero (estimaciones)
| Situación | Fuerza |
|-----------|--------|
| Llaves colgando | 0,5–1,5 N |
| Sacarlo del bolsillo | 2–10 N |
| Enganchón fuerte | 20–50 N (sobre todo doblando) |
| Golpe de llaves al caer | 30–150 N de pico |

## Costes de impresión multicolor (estimaciones, nov 2026)
Supuesto: PLA Basic a ~25 €/kg (1 g ≈ 2,5 céntimos). Cifras aproximadas: las exactas las da Bambu Studio al laminar.

- **El coste lo marcan los cambios de color, no la pieza.** Cada cambio en la A1 con AMS lite purga ~0,2–0,75 g (de negro a blanco es el peor caso, ~600 mm³) y tarda ~1–1,5 min.
- **Llavero botella ST26** (propuesta con ojal): pieza ~7 g (~0,18 €).
  - Solo blanco: ~7 cambios, ~3,6 g de purga, ~10 min.
  - Blanco + naranja: ~15 cambios, ~7 g de purga, ~20 min.
- La purga se hace por cambio, no por pieza: **imprimir en tandas** reparte la purga. Con 10 llaveros en la placa, cada uno lleva ~0,4 g en vez de ~3,6 g.
- Un relieve negro (la cápsula) en las mismas capas que las letras blancas obliga a cambiar de color en cada capa. Un relieve del color de la base no cuesta purga si no coincide en altura con otro color.
- Bajar de 4 a 3 capas de incrustación no ahorra cambios (se alterna igual). Con 2 capas sí, pero el negro se transparenta.
- Relleno: el cuerpo de la botella al 20 % (con modificador al 100 % en cuello y tapón) ahorra ~2,3 g sin tocar la zona que carga.

### Datos reales de Bambu Studio (1 nov 2026)
Proyecto `ST26_llavero_botella_A1_blanco_naranja` laminado por Luis en la A1, 1 llavero por placa:

| Concepto | Valor |
|----------|-------|
| Modelo | 6,89 g |
| Purga | 5,95 g |
| Torre de purga | 1,59 g |
| **Total** | **14,43 g · 0,36 €** (Bambu Studio usa ~25 €/kg) |
| Cambios de filamento | 16 |
| Tiempo | 43 min 45 s de impresión, 51 min 36 s en total |

- La purga y la torre (7,5 g) pesan más que el propio llavero: el 52 % del filamento se tira.
- Las estimaciones previas acertaron: se calcularon ~15 cambios y ~7 g de purga.
- El proyecto `.3mf` generado a mano se abrió y laminó bien en Bambu Studio con la A1, los tres filamentos y los ajustes asignados.

### Cuántos caben en la placa de la A1
- Llavero botella (20,2 × 75,9 mm): **28–29 por placa** (3 filas × 10 columnas, menos el hueco de la torre de purga; 3–5 mm de separación).
- Rendimiento decreciente: la purga ya queda repartida con ~10. Estimación con datos reales: 1 → 0,36 €/u y 52 min/u; 10 → ~0,19 €/u y ~28 min/u; 29 → ~0,18 €/u y ~26 min/u (placa de ~12,5 h).
- Una placa larga arriesga más: si falla, se pierden todas. Para las primeras tiradas, 10–15 por placa.

## Piezas combadas o despegadas (1 nov 2026, causas probables sin confirmar)
Luis vio llaveros botella combados y despegados durante la impresión en la A1. Causas probables, de más a menos:
- **Poca superficie en la cama en la punta del cuello.** El bisel de la boca y el avellanado del ojal por la cara de la cama dejan solo ~1,6 mm de apoyo a cada lado del ojal. Quitar el bisel de la cara de la cama solo baja la inclinación de la anilla de 55° a 52°, que sigue por encima de una llave.
- **Relleno al 100 % en una pieza plana y larga (76 mm).** Al enfriarse, el PLA macizo encoge más y tira de las esquinas hacia arriba.
- **Placa sucia.** Huellas o grasa: lavar con agua y jabón de platos, no solo alcohol.
- **Corrientes de aire o habitación fría.** La A1 es abierta; los extremos de las piezas largas se levantan.
- **Sin borde (brim).** El perfil no lo fuerza para PLA; las orejas en la punta del cuello y las esquinas ayudan.
- Una vez combada, la boquilla choca con la esquina levantada y arranca la pieza.
- La cama ya está a 65 °C (perfil de PLA Basic en placa texturizada); el ventilador entra al 60 % desde la capa 2.
- **Confirmado (1 nov 2026):** había una ventana abierta con viento cerca, la placa no estaba bien limpia y se levantó sobre todo la punta del cuello.

## Más relleno en una zona que en el resto (Bambu Studio)
- **Modificador:** en el objeto, clic derecho → «Añadir modificador» → caja. Colocarla sobre la zona (cuello y tapón) y, en sus ajustes, poner la densidad de relleno al 100 %. El resto usa la densidad global (p. ej. 20 %). Un proyecto `.3mf` puede traer el modificador ya colocado: es una pieza `modifier_part` con su propio `sparse_infill_density`.
- **Truco de paredes:** con 4 perímetros (~1,8 mm por lado), una pared de menos de ~3,5 mm entre dos bordes sale maciza solo con perímetros, sea cual sea el relleno. En el llavero botella, las paredes del ojal (2,6 mm) y encima del ojal (2,4 mm) ya salen macizas; el modificador hace falta para la raíz del cuello (8,7 mm de ancho).
- El «rango de altura» no sirve para esto: cambia ajustes por capas (eje Z), no por zonas de la pieza.

## Brim en multicolor (Bambu Studio)
- El **brim** es una franja de una sola capa alrededor de la pieza para que no se levante. Se quita con la mano al terminar.
- Bambu Studio lo imprime con el **primer filamento de la primera capa**. En automático empieza por el de menos superficie, que en el llavero ST26 es el naranja del «26», y por eso el brim salía naranja.
- Arreglo: fijar el orden de la primera capa en la placa («First layer filament sequence» → Customize, negro primero). En el `.3mf` va como `first_layer_print_sequence` = `1 2 3` en la placa de `model_settings.config`.
