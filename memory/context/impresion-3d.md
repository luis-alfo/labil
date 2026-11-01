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
