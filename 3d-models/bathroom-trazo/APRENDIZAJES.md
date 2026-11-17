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
| Embellecedor cromado | 3,5 mm | Estimado desde las fotos | Baja |
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
