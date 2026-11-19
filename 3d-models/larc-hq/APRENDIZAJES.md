# larc hq · cajonera colgada del elevador de pantalla

Diseño del 19 nov 2026. **Sin imprimir.** Fuente: `larc_hq.scad` (OpenSCAD); `generate_stl.py`
saca los STL, los GLB del visor y las descargas.

## Qué es

Una cajonera que cuelga de la cara de abajo del elevador de pantalla de la oficina de Luis
(contrachapado curvado). Dos cajones lado a lado, una pinza que abraza el canto delantero del
tablero y, encima de la pinza, una bandeja para dos bolis con el grabado
`LARC HQ | V1 | 191126` en el fondo (como El Secadero: nombre | versión | fecha de diseño).

## Códigos compartidos

- **larc hq**: la oficina de Luis. Es el nombre del objeto y lo que va grabado.
- **Medir con tarjetas**: Luis mide poniendo tarjetas estándar (ISO ID-1, **85,6 × 54 mm**) junto
  a la pieza y haciendo la foto. Las medidas salen de contar tarjetas.
- **Fecha del grabado**: la de diseño, en `ddmmaa` (191126 = 19 nov 2026).

## Medidas y de dónde salen

| Dato | Valor | Origen | Fiabilidad |
| --- | --- | --- | --- |
| Fondo del tablero | 225 mm | 3 tarjetas en fila: 54 + 85,6 + 85,6 | buena |
| Alto libre bajo el tablero | 85 mm | una tarjeta de pie cabe justa | buena |
| Grosor del tablero | 12 mm | proporción en la foto con la tarjeta | **estimado: lo confirma la prueba de la pinza** |
| Pie del monitor al canto delantero | ~42 mm | foto desde arriba | estimado |
| Tramo plano del tablero | ~300 mm | foto de frente | **estimado: falta medirlo** |
| Ancho entre patas en la mesa | ~510 mm por fuera | foto de frente | estimado |

## Lo que pidió Luis (19 nov 2026)

- Colgada, «pero no necesariamente que ocupe todo el ancho». Debajo se sigue guardando el portátil.
- «Que en la parte delantera que se engancha tenga para dejar dos bolis y en el fondo ponga
  larc hq | v1 | XXXXXX (fecha de diseño) como el secadero».
- Sujeción: «pinza en el canto delantero […] y si eso con un poco de cinta de doble cara por
  debajo pero unos puntos de sujeción».
- Contenido: A5 (A4 doblados por la mitad), dos cables (portátil y móvil), un transformador,
  papelería pequeña y quizá pañuelos de papel.

## Decisiones

- **Dos cajones**: uno a medida de A5 (hueco interior 152,6 × 217 × 38 mm; A5 = 148 × 210) y uno
  pequeño (84,6 × 217 × 38 mm) con un separador a 85 mm del frente: detrás cabe un transformador
  de hasta 80 × 80 × 30 con sus cables, delante la papelería.
- **Alto total 44 mm** bajo el tablero: quedan **41 mm** libres para el portátil (mide unos 12–16).
- **La carcasa no es una caja**: es un perfil. Placa de arriba + tres paredes + carriles de 8 mm
  donde apoyan los cajones. Sin suelo ni trasera: el suelo lo pone cada cajón. Menos plástico y
  todo son paredes verticales al imprimir.
- **Pinza**: una pared de 3 mm sube por delante del canto y un labio de 33 mm entra sobre el
  tablero (el pie del monitor queda a ~42 mm). No es un clip que flexe: entra deslizando desde
  delante, con 0,4 mm de holgura sobre el grosor.
- **Cinta de doble cara**: tres asientos de 40 × 16 mm rebajados 0,5 mm al fondo de la placa.
- **Tope de los cajones**: una lengüeta flexible en la placa de arriba con un diente de 1,2 mm.
  El cajón entra por la rampa y al abrir se para a 30 mm del final; se saca del todo con un tirón
  firme (cara a 60°). El cierre lo da el frente del cajón contra la carcasa.
- **Aligerado**: ranuras a lo largo en la placa de arriba, acabadas en punta a 45° para que se
  impriman sin puentes.

## Comprobaciones

- **Pinza sin cinta**: con 1 kg colgando a 110 mm del canto, el par es 1100 N·mm; el labio
  (250 × 2,4 mm) trabaja a unos **4,6 MPa**. Con la cinta al fondo, casi nada. El PLA entre capas
  aguanta unas cuatro veces más.
- **Lengüeta de tope**: sube 0,8 mm sobre 26 mm de largo → 0,2 % de deformación. Sin riesgo.
- Las cuatro piezas son sólidos cerrados (`is_volume`). Modelo mirado en capturas de frente, en
  tres cuartos, desde abajo y cortando la bandeja a la altura del grabado.
- La holgura de la pinza y el encaje de los cajones **no están probados**: van con la impresión.

## Impresión (A1, PLA)

| Pieza | Postura | Medida en placa | Gramos y coste (estimado, 20 €/kg) |
| --- | --- | --- | --- |
| A carcasa | de pie sobre su cara delantera | 250 × 64 × 222 mm | 224 g · 4,48 € |
| B cajón A5 | suelo en la placa | 158,5 × 221 × 41 mm | 107 g · 2,14 € |
| C cajón pequeño | suelo en la placa | 90,5 × 221 × 41 mm | 76 g · 1,51 € |
| prueba de la pinza | de pie, como A | 25 × 17 × 43 mm | ~6 g |

- La carcasa mide 250 mm en una placa de 256: **el borde (brim) no puede pasar de 3 mm**.
  Va en una placa sola; los dos cajones, cada uno en la suya (juntos hacen 254 mm).
- La carcasa de pie: capas perpendiculares al fondo. La pared delantera trabaja a tracción dentro
  de la capa (fuerte); el labio flexa entre capas, por eso se le pide poco (4,6 MPa).
- Sin soportes. La pared trasera de la bandeja y las puntas de las ranuras van a 45°.

Total: **407 g, 8,14 €** de PLA.

## Primero, la prueba

`prueba_pinza.stl` es una rebanada de 25 mm de la pinza. Se imprime en 10 minutos y dice si el
grosor del tablero es 12 mm:

- [ ] Entra en el canto delantero empujando con la mano, sin forzar.
- [ ] No baila arriba y abajo (más de ~0,5 mm de juego = bajar `board_t`).
- [ ] El labio no toca el pie del monitor.

Si aprieta: `board_t += 0.3`. Si baila: `board_t -= 0.3`.

## Pendiente de Luis

1. Grosor real del tablero (o imprimir la prueba).
2. Ancho del tramo plano del tablero, para confirmar que caben 250 mm.
3. Dónde va a lo ancho: centrada, o a un lado para dejar libres los enchufes.
4. Material y colores.

## Curvas: qué se puede sacar de LG Casa (19 nov 2026)

Luis ve la primera propuesta «demasiado recta» y pregunta qué sacar de los radios de LG Casa.

- **Los radios de LG Casa son cortos a propósito**: 1, 2, 3, 4 y 6 px. Su norma: «la forma la dan
  el canto y el color, no la curva». Lo redondo del todo (50 %) solo para puntos. LG Señal dice lo
  mismo (0 / 2 / 4 px). La escala de radios no da curvas grandes; da **esquinas matadas**.
- **La curva de LG Casa está en el arco de La Guarida** (el logo): una sola línea de grosor
  constante, con las puntas redondas, que dobla con dos radios. Hombros amplios (radio ≈ 23 sobre
  190 de ancho, **≈ 4 veces el grosor de la línea**), cumbre casi viva y tejado a unos 19°.
- **El elevador dobla igual**: contrachapado de 12 mm con un radio de unos 45 mm, **≈ 4 veces su
  grosor** (estimado en foto).
- **Regla que sale de ahí**: la pieza es una lámina que se dobla, y dobla con radio = 4 × grosor.
  Pared de 2 mm → R8. Los cantos pequeños siguen la escala de Casa leída en milímetros (2, 4, 6).
- **Sale gratis al imprimir**: la carcasa es un perfil extruido de pie; cualquier curva del perfil
  son paredes verticales, sin voladizos.

Propuestas (pendiente de que Luis elija):

1. Perfil de lámina doblada: esquinas de abajo de la carcasa en R8 y cajones que las siguen.
2. Pinza como un solo doblez continuo sobre el canto, con la punta del labio redonda como las
   puntas del arco.
3. Frentes de cajón con esquinas R4 y tirador circular completo en vez de media muesca.

### Del DS digital al objeto (corrección de Luis, 19 nov 2026)

«Son DS para el mundo digital, tenemos que saber traerlo al físico» (Luis). Leer píxeles como
milímetros no vale. Probado en un borrador con radio = 4 × grosor (R8): suaviza las esquinas pero
la cajonera se sigue leyendo como una caja. Lo que se aprende:

- **En pantalla el radio se mide contra el píxel; en un objeto, contra la mano y contra el tamaño
  de la pieza.** Tres escalas distintas, que no se sustituyen entre sí:
  - **canto** (1–2 mm): lo que nota el dedo. Es el equivalente real de los radios de LG Casa.
  - **esquina** (4–8 mm): quita lo afilado, no cambia la silueta.
  - **gesto** (20–45 mm): es lo que el ojo llama «curvo». En el elevador es el doblez de R45.
- **Del arco se copia la proporción, no la medida**: sus hombros son un 12 % del ancho y casi un
  20 % del alto. En una pieza de 44 mm de alto eso pide radios de 20 mm o más.
- Pendiente: decidir con Luis de dónde sale el gesto (ver conversación).
