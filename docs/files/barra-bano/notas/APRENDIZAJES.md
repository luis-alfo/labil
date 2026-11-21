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

## 20 nov 2026 · Dos formas por objeto: de pie o colgado

Luis: «a nivel visual no me encanta que las cosas suban por encima de la barra», ni la pasta,
ni la colonia, ni el cepillo eléctrico. Regla que se prueba: **la línea es el techo y todo
cuelga por debajo**. No se decide todavía: se modelan las dos formas y se comparan en la
simulación de la web, con un clic por objeto (arriba → abajo → quitado).

| Objeto | De pie (arriba) | Colgado (abajo) |
| --- | --- | --- |
| Colonia | bandeja a ras de la línea | la misma bandeja, 99 mm más abajo |
| Desodorante | aro | bandeja baja, 88 mm |
| Pasta | horquilla, apoyada en el hombro | pinza: el extremo plano entra de lado en una ranura |
| Cepillo de dientes | horquilla | horquilla 34 mm más abajo |
| Cepillo del pelo | horquilla bajo la cabeza | gancho fino por el agujero del mango |
| Oral-B | vasito | horquilla baja, colgado por el cuello |
| Secador | gancho | (ya cuelga) |

- **Las cargas no cambian**: mismo peso y misma posición a lo largo de la barra.
- **Lo que sí cambia**: las bandejas bajas llevan una pared trasera grande (37 cm³ la de la
  colonia, frente a 17); las horquillas bajas se imprimen de canto y la ranura pide un
  soporte pequeño; lo colgado se balancea al cogerlo.
- **Por comprobar**: la altura hasta la encimera (secador, Oral-B y cepillo del pelo bajan
  20-25 cm) y si la pinza sujeta el tubo mojado.
- Colgado, el cepillo del pelo queda pegado al secador: habría que separarlos.

## 2026-11-20 · Secador en embudo, bandejas de nervios y radios de LG Casa

Lo pidió Luis tras ver la simulación.

### Secador
- Motivo: es eléctrico y colgado del gancho quedaba más abajo que el grifo, donde salpica.
- Ahora encaja morro abajo en un **aro en embudo** a la altura de la línea (`make_embudo`).
  Se bloquea donde el cono del secador toca el del aro. Motor e interruptor quedan arriba.
- El mango es plegable y no sirve para colgar: queda fuera, hacia quien lo coge.
- Medidas supuestas: 48 mm en el morro y 66 en el cuerpo (`SECADOR_D_MORRO`, `SECADOR_D_CUERPO`).
  El embudo va de 64 a 50 mm en 26 mm (15° por lado). **Medir antes de imprimir.**
- Se imprime con la placa abajo: el cono crece inclinado 15°, sin soportes.
- Carga: 250 g con el centro de masas a unos 85 mm de la línea. Placa 2,2 MPa y pata 2,8 MPa de 15.
- Pendiente de prueba: retuerce la línea con 208 N·mm, el doble que la colonia (103).
  El lazo tiene 0,3 mm de holgura en 8 mm de fondo, así que el aro puede cabecear 2 o 3 mm.

### Bandejas abiertas (colonia y desodorante)
- Principio de la cuna de El Secadero: nervios y suelo abierto en vez de lámina maciza.
- Pared y suelo son nervios de 8 mm de fondo (`TRAY_T`) que van del lomo al labio.
  Entre ellos, ventanas en cápsula, un travesaño cada 30–45 mm y un alma en diagonal en el codo.
- Por qué funciona: en flexión el centro de la sección casi no trabaja. Llevar el material
  lejos del centro da más módulo resistente (W) con menos plástico.

| Bandeja | Peso antes → ahora | W antes → ahora | Tensión antes → ahora | Rigidez |
|---|---|---|---|---|
| Colonia colgada | 46 → 38 g (−18 %) | 123 → 154 mm³ | 0,58 → 0,58 MPa | ×3,1 |
| Desodorante colgado | 30 → 24 g (−20 %) | 79 → 93 mm³ | 0,22 → 0,22 MPa | ×3,0 |
| Colonia a nivel de la línea | 21 → 21 g | igual que la colgada | igual | ×3,1 |

- Lo que no salió a la primera:
  - Engrosar toda la pared a 6 mm y abrirle ventanas pesaba **más** que la lámina maciza.
    Las zonas sin ventana (lomo, codo, pie del labio) crecen con el grosor y se comen el ahorro.
  - Con el mismo W la tensión subía un 24 %: el bote queda 5 mm más afuera y hace más palanca.
    Se corrigió ensanchando los nervios (2,9 → 3,6 mm en la colonia).
  - La bandeja a nivel de la línea no baja de peso: casi no tiene pared que abrir.
- Impresión: de canto, como antes. Los nervios quedan tumbados y cada ventana se cierra con
  un puente recto de menos de 30 mm. El alma del codo es el apoyo del nervio al imprimir.
- El desodorante se queda con una sola forma (bandeja colgada). Luis descartó el aro del revés.

### Radios de LG Casa en los enganches
- Regla tomada de la cajonera de LARC HQ: los píxeles no son milímetros; se copia la proporción.
- Constantes en `generate_stl.py`:
  - `R_CANTO = 2`: el canto fino del lomo, por detrás.
  - `R_ESQUINA = 4`: la esquina delantera del lomo.
  - `R_ENCUENTRO = 6`: donde la pared se encuentra con el suelo.
  - `BEND_K = 4`: una lámina se dobla a 4 veces su grosor (3,2 → 12,8 mm). Labio y codo de las bandejas.
- Las patas del lomo y las puntas de las horquillas acaban en media caña, como la punta de la línea.
- Las patas de los enganches de placa siguen el contorno redondeado de la placa.
