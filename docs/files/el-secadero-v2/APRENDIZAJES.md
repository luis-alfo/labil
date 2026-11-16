# El Secadero V2: datos, decisiones y comprobaciones

## Cómo se numeran las versiones (decisión de Luis, 16 nov 2026)
- Solo cuenta como versión lo que se imprime.
- **V1** es la única impresa hasta ahora (`3d-models/sponge-holder/`).
- **V2** es este diseño.
- Todo lo que hubo entre medias fueron borradores de diseño, no versiones.
  - En la conversación y en commits antiguos se les llamó «V2» a «V5».
  - Dos de ellos están archivados en `3d-models/_borradores/` (`estropajero-v3` y `estropajero-v4`).
  - En estas notas se les llama «el borrador anterior» o «los borradores».
- El grabado y la web usan la numeración de Luis: «EL SECADERO | V2 | 161126».

Estado: diseñado y simulado el 16 nov 2026. Sin imprimir.

## De dónde sale cada medida
| Dato | Valor | Origen |
|---|---|---|
| Estropajo | 95 × 70 × 45 mm, tipo salvauñas | Confirmado por Luis |
| Columna del grifo | Ø 45 mm | La V1 se imprimió para 45 y encajó (está en las fotos) |
| Grifo → canto de la encimera | 59 mm desde el eje | El brazo de la V1 llegaba justo al canto en las fotos; ±2 mm |
| Embellecedor | ~Ø 57 × 5,5 mm | Estimado en las fotos usando la V1 como escala; ±2 mm |
| Fregadero | Ø 400, pared a ras del canto | Supuesto, sin medir |
| Espacio detrás del grifo | hacen falta unos 12 mm | Sin comprobar |

- Los borradores usaban 46 / 54 × 8 / 68 mm, que eran suposiciones mías. La distancia al canto estaba 9 mm larga.
- Lección: los datos de la V1 llevaban en el repo desde el principio (`3d-models/sponge-holder/`). Antes de suponer una medida hay que mirar lo que ya se imprimió y funcionó.

## Decisiones de Luis
- El soporte puede apoyarse en la pared interior del fregadero.
- El estropajo va de canto, apoyado en el lado largo, que es como mejor se seca.

## Cómo es la V2
- **A, brazo:**
  - Abrazadera en U con un faldón fino que rodea el embellecedor con holgura (vale hasta Ø 59 × 6,5) y agarra en la columna.
  - Brazo de 3 mm a ras de la encimera.
  - La punta engrosa a 5 mm para alojar el marco enrasado.
- **K, cuña:** entra desde arriba por detrás de la columna. Al bajarla aprieta la U contra el grifo y se queda bloqueada sola (12°). Sustituye a la llave suelta del borrador anterior, que no apretaba.
- **B, marco:**
  - Bastidor plano con forma de percha, impreso tumbado.
  - Cabalga sobre la punta del brazo: entra de frente 3,3 mm alto y cae en una ranura.
  - Sus dos esquinas de abajo, separadas 116 mm, apoyan en la pared del fregadero. Eso lo estabiliza de lado y frente al giro.
- **C, cuna:**
  - A la medida del estropajo (hueco de 49 × 101 mm), con tres nervios y el suelo abierto.
  - Gira sobre dos muñones con caras planas, alojados en las aletas del marco. Solo entra y sale a 60°.
  - Abajo descansa sobre dos tetones, con 10 mm de palanca.
  - Levantada pasa entre las patas del marco, se apoya en la pared del fregadero a unos 102° y se queda sola.

## Qué resuelve de la crítica al borrador anterior
| Problema del borrador anterior | V2 |
|---|---|
| El estropajo no cabía | Cuna a su medida; comprobado con un bloque de 95 × 70 × 45 |
| Se ladeaba (apoyo de 10 mm) | Apoyo de 116 mm en la pared; el estropajo solo puede descentrarse 3 mm |
| Nada bloqueado | La cuña aprieta; el marco no sale tirando ni basculando (hay que subirlo 3,3 mm); la cuna solo sale a 60° |
| Bisagra en medio de la bandeja | Bisagra en los laterales, fuera del hueco |
| Abrazadera maciza de 13 cm³ | Cáscara de 2–3 mm |
| Sobresalía 84 mm (36 levantada) | 68 mm abajo y 32 levantada |

## Comprobado en simulación (mallas ideales, sin tolerancias de impresión)
- Las cuatro piezas son sólidos cerrados. No hay voladizos de más de 45°, salvo dos puentes cortos: el techo de 8 mm de los alojamientos de los muñones, y la base de muñones y tetones contra la cama.
- En posición final nada se solapa: ni las piezas entre sí, ni con el grifo (también con embellecedor de Ø 59 × 6,5), ni con la encimera, la pared o el estropajo.
- Montaje sin choques:
  - A deslizando hacia la pared;
  - K desde arriba;
  - B de frente y bajando;
  - C a 60° por las ranuras.
- La cuna gira libre de 0° a 102°.
  - A −1° ya hace tope.
  - Levantada, su centro de gravedad queda 5,8 mm por detrás del eje. Hay que girarla unos 20° hacia abajo para que caiga.
- La cuna no se puede sacar a 0°, 30° ni 100°, ni hacia arriba, ni por la ranura, ni hacia el fregadero.
- Cargas, con fórmulas de mano:

| Punto | Estropajo (1 N) | 20 N en el borde |
|---|---|---|
| Tracción en el brazo | 0,4 N | 13 N |
| Pata del marco (en el plano de capa) | 0,4 MPa | 17 MPa |
| Repisa del tope (entre capas) | 0,1 MPa | 6 MPa |
| Brazo sobre el canto | 0,5 MPa | 11 MPa |

- Material y tiempo (perfil parecido al de A1 + PLA Basic):

| Pieza | Filamento | Tiempo |
|---|---|---|
| A brazo | 15,6 g | 26 min |
| K cuña | 2,5 g | 6 min |
| B marco | 14,7 g | 33 min |
| C cuna | 11,2 g | 23 min |
| **Total** | **~44 g** | **~1 h 30 min** |

  El borrador anterior eran ~45 g y ~1 h 30 min. Antes del rediseño estético este diseño eran ~39 g: las formas redondeadas y los refuerzos para no perder resistencia cuestan unos 5 g.

## Lo que la simulación no cubre
- Las holguras reales de impresión: el muñón de 3,6 mm en la ranura de 4,2 y la cuña.
- El rozamiento de la cuña sobre el cromo.
- La pared real del fregadero. Si está a ±5 mm de lo supuesto, el marco se inclina unos ±3,5°.
- El cuerpo horizontal del grifo, que no está modelado. La abrazadera mide 22 mm de alto y la de la V1 llegaba a 27,5.

## Orden de impresión recomendado
Cada paso valida un encaje antes de gastar más.
1. A y K (18 g, 32 min).
   - [ ] El faldón rodea el embellecedor sin tocarlo.
   - [ ] La cuña baja y aprieta, y queda más o menos enrasada.
   - [ ] La ranura de la punta queda justo por fuera del canto.
2. B (15 g, 33 min).
   - [ ] Entra de frente y cae en la ranura.
   - [ ] Cuelga vertical, con las dos esquinas tocando la pared.
3. C (11 g, 23 min).
   - [ ] Entra a 60°.
   - [ ] Abajo queda horizontal.
   - [ ] Levantada se queda sola.
   - [ ] El estropajo entra de canto.

## Estética: lo que pidió Luis (16 nov 2026)
- La abrazadera le parecía poco estética y todo demasiado cuadrado.
- Quiere un objeto bonito, no solo funcional, que se integre en la cocina de forma elegante. Pidió repensar todas las esquinas.
- Quiere un grabado en hendidura con el texto «EL SECADERO | V2 | 161126» en JetBrains Mono: nombre del objeto, versión y fecha (ddmmaa). Le vale en la abrazadera o en el brazo. Primero pidió «V5»; después lo corrigió a «V2» por la regla de numeración de arriba.
- El objeto se llama **El Secadero**. El grabado lleva la versión y la fecha, así que hay que actualizarlo en cada versión (parámetro `label` del `.scad`).

### Nombres de las piezas
- **A, brazo:** una sola pieza con dos zonas, el anillo que abraza el grifo (antes «abrazadera») y el brazo plano que va hasta el fregadero.
- **K, cuña:** la pieza pequeña que cierra el anillo por detrás.
- **B, marco:** la percha que cuelga de la punta del brazo.
- **C, cuna:** donde va el estropajo.

### Qué se cambió
- Anillo:
  - Perfil acampanado, como el embellecedor de un grifo: base ancha, curva en S y banda recta arriba, con el canto superior redondeado.
  - Planta en herradura, con las colas redondeadas.
- Grabado: va en la banda recta del anillo, mirando al fregadero.
  - Mayúsculas de 3 mm y 0,6 mm de fondo.
  - En el brazo no cabe: el texto mide 61 mm y el brazo, 31.
  - En una cara vertical se imprime más nítido y no acumula agua.
- Brazo:
  - Nace del anillo con un cuello curvo de radio 8.
  - Tiene el canto matado.
  - Sube a la punta con una rampa larga.
  - La cartela triangular se sustituyó por un cuello en media caña (ver «Resistencia tras el rediseño»).
- Cuña: lleva una visera curva que, vista desde arriba, cierra el contorno por detrás y sirve de uñero.
- Marco: rincones con radio 4, esquinas con radio 2 y canto delantero matado.
- Cuna:
  - Esquinas de radio 7.
  - Ventanas en cápsula en vez de rombos.
  - Borde trasero en arco.
- La fuente va en `fonts/` para que el grabado salga igual en cualquier máquina y en CI.
- Lección: probar el aspecto con capturas del visor antes de darlo por bueno. Un primer nervio «redondeado» salió facetado y hubo que quitarlo.

## Resistencia tras el rediseño (aviso de Luis: «que no pierda resistencia»)
Se compararon secciones cortando las mallas de antes y de después del rediseño. W es el módulo resistente: a igual carga, más W es menos tensión.

| Sección | Antes | Primer rediseño | Corregido |
|---|---|---|---|
| Brazo junto al anillo (W) | 52,0 mm³ | 38,1 (−27 %) | 53,9 |
| Brazo a media longitud (W) | 33,0 | 36,0 | 36,0 |
| Brazo sobre el canto (W) | 49,3 | 67,6 | 67,6 |
| Unión brazo–anillo (área) | 146 mm² | 186 | 186 |
| Frente del anillo a 5 mm de altura (área) | 74 mm² | 69 (−7 %) | 90 |
| Pata del marco, fuera de plano (W) | 33,0 mm³ | 29,8 (−10 %) | 34,0 |
| Aleta junto al marco (W) | 206 mm³ | igual | 232 |
| Puente del marco y sección de la cuna | igual | igual | igual |
| Pared del anillo bajo el grabado | 2,6 mm | 2,0 | 2,6 |

- El primer rediseño perdía resistencia en tres sitios:
  - la unión del brazo con el anillo, al quitar la cartela;
  - las patas del marco, por el canto matado;
  - la banda del anillo, por el grabado.
- Correcciones:
  - Cuello en media caña de radio 7 entre el brazo y el anillo, con forma de mango de cuchara.
  - Patas y aletas de 6,2 mm en vez de 5,5.
  - Banda del anillo de 3,2 mm, para que queden 2,6 bajo las letras.
- Lección: redondear y matar cantos quita material justo en la fibra más cargada. Después de un cambio estético hay que volver a medir las secciones, no darlas por iguales.
- Son comparaciones de sección sobre mallas ideales, no ensayos.
