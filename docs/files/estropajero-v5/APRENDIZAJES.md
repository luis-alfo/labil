# Soporte de estropajo V5: datos, decisiones y comprobaciones

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

- Las versiones V2 a V4 usaban 46 / 54 × 8 / 68 mm, que eran suposiciones mías. La distancia al canto estaba 9 mm larga.
- Lección: los datos de la V1 llevaban en el repo desde el principio (`3d-models/sponge-holder/`). Antes de suponer una medida hay que mirar lo que ya se imprimió y funcionó.

## Decisiones de Luis
- El soporte puede apoyarse en la pared interior del fregadero.
- El estropajo va de canto, apoyado en el lado largo, que es como mejor se seca.

## Cómo es la V5
- **A, brazo:**
  - Abrazadera en U con un faldón fino que rodea el embellecedor con holgura (vale hasta Ø 59 × 6,5) y agarra en la columna.
  - Brazo de 3 mm a ras de la encimera.
  - La punta engrosa a 5 mm para alojar el marco enrasado.
- **K, cuña:** entra desde arriba por detrás de la columna. Al bajarla aprieta la U contra el grifo y se queda bloqueada sola (12°). Sustituye a la llave suelta de la V4, que no apretaba.
- **B, marco:**
  - Bastidor plano con forma de percha, impreso tumbado.
  - Cabalga sobre la punta del brazo: entra de frente 3,3 mm alto y cae en una ranura.
  - Sus dos esquinas de abajo, separadas 116 mm, apoyan en la pared del fregadero. Eso lo estabiliza de lado y frente al giro.
- **C, cuna:**
  - A la medida del estropajo (hueco de 49 × 101 mm), con tres nervios y el suelo abierto.
  - Gira sobre dos muñones con caras planas, alojados en las aletas del marco. Solo entra y sale a 60°.
  - Abajo descansa sobre dos tetones, con 10 mm de palanca.
  - Levantada pasa entre las patas del marco, se apoya en la pared del fregadero a unos 102° y se queda sola.

## Qué resuelve de la crítica a la V4
| Problema de la V4 | V5 |
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
| A brazo | 12,5 g | 19 min |
| K cuña | 1,9 g | 4 min |
| B marco | 14,1 g | 30 min |
| C cuna | 10,8 g | 22 min |
| **Total** | **~39 g** | **~1 h 15 min** |

  La V4 eran ~45 g y ~1 h 30 min.

## Lo que la simulación no cubre
- Las holguras reales de impresión: el muñón de 3,6 mm en la ranura de 4,2 y la cuña.
- El rozamiento de la cuña sobre el cromo.
- La pared real del fregadero. Si está a ±5 mm de lo supuesto, el marco se inclina unos ±3,5°.
- El cuerpo horizontal del grifo, que no está modelado. La abrazadera mide 22 mm de alto y la de la V1 llegaba a 27,5.

## Orden de impresión recomendado
Cada paso valida un encaje antes de gastar más.
1. A y K (14 g, 23 min).
   - [ ] El faldón rodea el embellecedor sin tocarlo.
   - [ ] La cuña baja y aprieta, y queda más o menos enrasada.
   - [ ] La ranura de la punta queda justo por fuera del canto.
2. B (14 g, 30 min).
   - [ ] Entra de frente y cae en la ranura.
   - [ ] Cuelga vertical, con las dos esquinas tocando la pared.
3. C (11 g, 22 min).
   - [ ] Entra a 60°.
   - [ ] Abajo queda horizontal.
   - [ ] Levantada se queda sola.
   - [ ] El estropajo entra de canto.
