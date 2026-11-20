# Aprendizajes — Trazo (barra de baño)

Notas del diseño: de dónde sale cada dato, qué se decidió y por qué, y qué
queda por comprobar. Léelo antes de tocar `generate_stl.py`.

## Qué es

Una línea plana de PLA que cuelga del grifo empotrado del baño. Pasa por
encima del caño y de la manilla, se engancha a cada uno con un lazo abierto
hacia abajo y se alarga un palmo a cada lado, con las puntas hacia arriba.
Los ganchos («jinetes») se apoyan sobre su canto superior y se cambian a mano.

## Datos

| Dato | Valor | De dónde sale | Seguridad |
| --- | --- | --- | --- |
| Diámetro del caño | 29 mm | Medido por Luis (1 may 2026) | Alta |
| Diámetro de la manilla | 42 mm | Medido por Luis | Alta en el número; **falta saber si es el casquillo fijo o el mando que bascula** |
| Separación | 49 mm de borde a borde → 84,5 mm entre ejes | Medido por Luis | Alta |
| Altura de los ejes | Alineados | Luis: «los centros están alineados» | Alta |
| Fondo de los cilindros | 15-20 mm | Luis, a ojo | Media |
| Embellecedor del caño | ~6 mm | Luis, con la prueba impresa (20 nov 2026) | Media («aproximadamente») |
| Embellecedor de la manilla | ~2 mm | Luis, con la prueba impresa | Media |
| Placa negra | ~158 × 81 mm | Estimado desde las fotos | Baja (solo se usa para el visor) |
| Palanca | Cuelga hacia abajo y a la derecha | Fotos | Media |
| Largo de cada brazo | 200 mm | Luis: «un palmo por lado» | Media |
| Material | PLA | Luis | Alta |
| Carga | Menos de 1 kg en total | Luis | Alta |
| Impresora | Bambu A1 (256 × 256 mm) | Perfil del repo | Alta |

Las fotos del baño que subió Luis solo llegaron dentro de la conversación:
no están guardadas en `proceso/`. Hay que pedirlas de nuevo para enseñarlas
en la web.

## Decisiones y por qué

1. **Una línea, no una barra.** Luis: «no la entiendo como barra sino como
   una línea». Es un perfil de 8 mm de fondo que afina de 14 mm junto al
   grifo a 6 mm en las puntas.
2. **Lazos boca abajo.** La pieza entra desde arriba y el peso aprieta la
   parte maciza del lazo contra el cilindro. Los brazos del lazo solo
   retienen el tirón hacia arriba que aparece en el lazo contrario cuando la
   carga está descompensada. En los tres borradores la boca miraba hacia
   arriba y el peso tiraba de la pieza hacia fuera.
3. **La línea va por arriba y pegada a la pared.** Ocupa de 3,5 a 11,5 mm
   desde la placa: apoya en el embellecedor y queda detrás del mando y de la
   palanca. En hilo y carril la barra pasaba por donde baja la palanca.
4. **Todo plano.** Cada pieza es un perfil extruido. Se imprime tumbada, sin
   soportes, y las capas quedan en el plano en el que flexan los lazos y
   trabaja la línea, que es la dirección fuerte del PLA.
5. **Partida por el centro.** Mide 485 mm y no cabe entera. Se parte entre
   los dos cilindros con una cola de milano; ahí la línea engorda hacia
   abajo para alojarla. Cada mitad (253 mm) entra en diagonal en la A1.
6. **Jinetes.** Una U que cae sobre el canto de la línea. Gancho y repisa se
   imprimen de canto; horquilla y aro, con la placa abajo. La pata trasera
   mide 7 mm para no asomar donde la línea solo tiene 6.
7. **Todo PLA.** Sin varilla de aluminio ni tornillos.

## Números (estimados, no ensayados)

PLA con E ≈ 3000 MPa. Los imprime `generate_stl.py`.

| Caso | Resultado |
| --- | --- |
| Encajar el lazo del caño | Abre 1,2 mm por brazo, deformación 0,9 % |
| Encajar el lazo de la manilla | Abre 2,0 mm por brazo, deformación 1,0 % |
| Límite prudente de deformación | 1,2 % |
| Soltar un lazo hacia arriba | Unos 25 N |
| 300 g a 150 mm del grifo | 1 mm de flecha, 5 N sobre el lazo contrario |
| 500 g en la punta | 4 mm de flecha, 12 N sobre el lazo contrario |

## Qué falta comprobar (con las tres pruebas)

- `test_clip_manilla`: que los 42 mm son del casquillo fijo y que el mando
  no roza la pieza al abrir el agua a tope. Es la prueba que más importa.
- `test_clip_cano`: el clic sobre el tubo y el ajuste de un jinete.
- `test_union`: que la cola de milano entra a mano y no cabecea. Su holgura
  decide cuánto caen las puntas.
- El diámetro del aro (62 mm) contra el secador de Luis.

## Lo aprendido

- **Mirar el modelo antes de enseñarlo.** Los tres borradores nunca se
  renderizaron. Al hacerlo se vio que salían tumbados, en espejo y mil
  veces más grandes, y que la barra cruzaba la palanca.
- **Marco del GLB.** El modelo se piensa con x a la derecha, y hacia quien
  mira y z arriba. Ese marco es a izquierdas; glTF es a derechas, con Y
  arriba y en metros. `export_glb()` hace el cambio.
- **Encadenar `buffer()` deja vértices casi repetidos** que rompen la
  triangulación al extruir. Se arregla con `simplify(0.01)` antes.
- **La web de artefactos de Claude no sirve `.glb`.** Para verlo allí hubo
  que pasar el modelo en base64 dentro de un `.json`.

## Coste (calculado por la web, perfil A1, 20 €/kg)

| Qué | Gramos | Euros |
| --- | --- | --- |
| El diseño entero (dos mitades y cinco jinetes) | 74 g | 1,49 € |
| Prueba manilla | 7,6 g | 0,15 € |
| Prueba caño | 7,0 g | 0,14 € |
| Prueba unión | 4,4 g | 0,09 € |
| Las tres pruebas | 19 g | 0,38 € |

Las pruebas van aparte del precio del diseño.

## 20 nov 2026 · Pruebas impresas y relleno de 4 mm

- Luis imprimió `test_clip_cano` y `test_clip_manilla`. **Los dos lazos entran y se quedan.**
  El de la manilla abraza el casquillo fijo, por detrás de la rótula cromada: los 42 mm eran
  de la parte fija.
- **No quedan a la misma distancia de la pared.** El caño tiene un embellecedor de unos 6 mm
  y la manilla de 2 mm; se había supuesto 3,5 mm en los dos.
- Decisión de Luis: sumar 4 mm por detrás a la pieza de la manilla, «para que estén
  alineadas y entonces empujando al fondo vayan bien».
- Cómo queda: `CANO_GAP = 6`, `MANI_GAP = 2`. La línea vive en el plano del caño. El lazo de
  la manilla lleva un relleno (`MANI_PAD = 4`) solo en su parte alta (±45° desde arriba), de
  modo que los brazos del clic siguen con los 8 mm de fondo que ya se probaron.
- La mitad derecha se imprime con la cara de delante sobre la cama: el relleno es lo último
  y no pide soportes.
- **Por comprobar con la prueba nueva de la manilla:** con el relleno, el lazo llega hasta
  14 mm de la placa (antes 10). Hay que ver que el mando no lo roza al abrir el agua.
- En las fotos las pruebas se ven con el relleno al aire, sin capa de arriba. Para la pieza
  final hacen falta capas macizas arriba y abajo: es lo que da rigidez a la línea.
- Colores: línea en gris claro y enganches en naranja, «rollito Braun Dieter Rams» (Luis).
- Las imágenes `trazo_en_el_bano_*.jpg` son el modelo colocado sobre las fotos de Luis: la
  cámara se saca de las cuatro esquinas de la placa negra (`cv2.solvePnP`) y el grifo tapa
  lo que queda detrás.

## 20 nov 2026 · Siete objetos, brazos de 250 mm y cálculo de cargas

Luis quiere colgar siete cosas, una por enganche, y dio sus pesos:

| Objeto | Peso | Enganche | Lado |
| --- | --- | --- | --- |
| Colonia Boss | 370 g | bandeja con reborde, abierta por los lados | izquierda, junto a la placa |
| Desodorante Sanex | 65 g | aro: cae de arriba y apoya en la panza | izquierda |
| Pasta Colgate | 100 g | horquilla: cuelga boca abajo por el hombro | izquierda |
| Cepillo de dientes | 20 g | horquilla | izquierda, en la punta |
| Secador | 250 g | gancho hondo, por la anilla del mango | derecha, junto a la placa |
| Cepillo del pelo | 120 g | horquilla ancha, bajo la cabeza | derecha |
| Oral-B | 125 g | vasito: aro, cuatro postes y suelo en cruz | derecha, en la punta |

**Dos criterios de Luis** que mandan sobre el reparto:
- Usabilidad: son objetos de uso diario, se cogen y se dejan con una mano. Los enganches se
  abren hacia delante.
- Estética: «todo debería a nivel visual librar la placa de grifo y manilla». Nada encima
  de la placa; la colonia no va entre grifo y manilla, como propuse al principio.

**Rediseño**: fuera de la placa hacen falta unos 185 mm útiles por lado. Los brazos pasan
de 200 a 250 mm (decisión de Luis), la curva de la punta se acorta a 24 mm y la línea sube
de 14 a 16 mm de alto. Cada mitad mide 303 mm y, girada, cabe en un cuadrado de 222 mm.

**Cálculo** (`estado()` y `cargas()` en `generate_stl.py`; resultado en `cargas.json`).
La barra es una viga sobre dos apoyos, los lazos. Un lazo que «apoya» descansa sobre el
grifo; uno del que «tiran» depende de su clic.

| Qué | Valor | Aguanta | Margen |
| --- | --- | --- | --- |
| Todo puesto | caño apoya 5.2 N, manilla apoya 5.1 N | — | — |
| Peor tirón en el caño (solo lo de la derecha) | 7.2 N | 24 N | ×3.4 |
| Peor tirón en la manilla (solo lo de la izquierda) | 6.9 N | 25 N | ×3.6 |
| Tensión en el arranque de un brazo | 1.8 MPa | 15 MPa | ×8.4 |
| Caída de una punta | 1.7 mm | el doble con los años | — |

Se han probado las 128 combinaciones de objetos puestos y quitados.

**Lo que no está comprobado**
- Lo que aguanta cada lazo es un cálculo. Las pruebas impresas encajan, pero no se ha
  medido la fuerza para soltarlas.
- Los tamaños de los objetos salen de la foto. Colonia (68 × 30 mm de base), desodorante
  (Ø 42), Oral-B (Ø 28) y los cuellos de pasta (15), cepillo (8) y cepillo del pelo (21)
  hay que medirlos antes de imprimir sus enganches.
- No está calculado el tirón al coger el secador ni la torsión por lo que sobresale cada
  objeto.
- La pasta queda de pie sobre la horquilla, apoyada hacia atrás. Si se cae hacia delante,
  la alternativa es una pinza para el extremo plano.
- El suelo del vasito del Oral-B son dos puentes de 30 mm: hay que ver cómo salen.

El artefacto «Trazo en uso» (https://claude.ai/artifact/TpyqDXyHMkNxnL79vbWcUZ) enseña esto
mismo de forma interactiva: se pone y se quita cada objeto y cambian las fuerzas.

