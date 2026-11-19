# Llavero ST26 — aprendizajes

Llavero de la marca **ST26** con forma de botella de vino. Diseñado entre el 20 de octubre y el
1 de noviembre de 2026 a partir de la imagen del logo (335 px).

> **Rehecho el 19 nov 2026.** El trabajo original no llegó a subirse: GitHub rechazó la subida y
> el contenedor de la sesión se renovó. Los modelos y proyectos se han rehecho desde las siluetas
> guardadas (`fuente/siluetas_artefacto.json`, sacadas del artefacto «Evolución llavero ST26») con
> `fuente/rehacer.py` y `fuente/make_a1.py`. Medidas y volúmenes coinciden con los originales
> (v1 45 × 34 × 4,2 mm; v3 20,2 × 75,9 × 5,2 mm, 6,9 g maciza). Las resistencias son las del
> cálculo original. Faltan las fotos del proceso, salvo el logo.

## Qué es ST26

- Marca o proyecto de Luis. El material gráfico habla de «una nueva añada», así que
  probablemente es un vino de 2026 (**sin confirmar**).
- Logo «ST26» en letra gótica pixelada: ST en blanco, 26 en salmón (`#E8A07F`), sobre negro.
- En el logo original la S remata arriba en un **rombo** y llega a la T por un **hilo de 1 px**.
  En las piezas impresas la S y la T van **separadas**, con 0,5 mm de hueco.
- Solo existe esta imagen de 335 px. Un vectorial (SVG, PDF, AI) haría las letras exactas.

## Versiones y borradores

Solo cuenta como versión lo impreso.

| Estado | Tipo | Silueta guardada | Qué |
| --- | --- | --- | --- |
| v1 silueta | **impresa** | `v1` | Silueta de las letras con aro arriba, 45 × 34 × 4,2 mm |
| aro reforzado | borrador | `v2` | Pared del aro de 3,2 mm |
| aro lateral | borrador | `lat` | Aro en el lateral izquierdo, en la dirección del tirón |
| trazo mínimo | borrador | `v5` | Trazos de 0,9 mm sin perder el rombo de la S |
| primeras botellas | borrador | `bot1` | Tres formas de botella; no parecían de vino |
| botella de 75 cl | borrador | `botB` | Proporciones reales, cápsula; Luis elige la B serigrafiada |
| doble cara | borrador | `doble` | Argolla en el tapón, logo incrustado detrás |
| tapón macizo / bisel | borradores | `final` | Letras blancas, tapón negro macizo, primer `.3mf`; bisel de 1 mm: la anilla pasa de 23° a 35° |
| v2 botella con ojal | **impresa** | `prop` | 20,2 × 75,9 mm, ojal de 3,5 × 7 mm, blanco y naranja |
| v3 primera capa | por imprimir | (= `prop`) | Sin biseles abajo, brim, relleno 70 %, placa de 16 |

Las siluetas están en milímetros: `base` (cuerpo negro, con su agujero), `white` (ST),
`salmon` (26), `capsule` si la hay, y `hole` (centro del agujero), como trazados SVG.

## Datos de la v3 (la que toca imprimir)

| Dato | Valor |
| --- | --- |
| Medidas | 20,2 × 75,9 × 5,2 mm (botella de 4,4 mm + 0,8 mm de relieve) |
| Peso | ~6,1 g con relleno al 70 % (macizo 6,9 g; al 20 % 4,7 g) |
| Ojal | 3,5 × 7 mm en el tapón, alargado hacia el cuerpo, pared lateral de 2,6 mm y 2,4 mm encima |
| Biseles | 1 mm a 45° solo por la cara de arriba (agujero y boca) |
| Logo | Vertical, 30,5 mm; relieve de 0,8 mm delante; detrás incrustado a ras en 4 capas (0,8 mm), **misma forma que delante**: se ve en espejo, como si las letras atravesaran |
| Colores | Filamento 1 negro, 2 blanco (ST), 3 naranja (26). Para todo blanco, bobina blanca en el 3 |
| Resistencia (cálculo) | Tirón ~233 N (~186 N con anilla fina), doblar el tapón ~51 N |
| Anilla | Un alambre de 1,5 mm se inclina ~52° (una llave típica, ~46°) |
| Primera capa | Brim de 4 mm solo por fuera, orden negro → blanco → naranja, pata de elefante a 0 |
| Relleno | 70 % rectilíneo; modificador al 100 % en cuello y tapón |
| Placa | 16 por placa (2 filas × 8), máximo que pidió Luis |

## Decisiones de Luis (con sus palabras)

- Silueta de las letras, no un rectángulo; unos 4,5 cm de ancho.
- «Por direccionalidad de tiro al sacarlo de un bolsillo es mejor a la izquierda, no en la esquina.»
- «Pf no parece una botella de vino» → proporciones de una botella de 75 cl.
- «La argolla tiene que estar en el tapón; la que más me gusta es la B» (serigrafiada).
- Por detrás, que no sea todo negro y sin imprimir el color por dentro → incrustación a ras.
- Letras todas blancas (luego: blanco y naranja, que él puede cambiar a blanco).
- «Choca un poco porque la argolla es recta» → bisel, y después su idea: agujero ovalado y
  llavero algo mayor para que «se ponga como una llave más».
- «Por detrás lo que quiero es que se lea como si estuviese viéndose las letras por detrás,
  como si esas letras atravesasen, no que se lea bien.»
- «Relleno 100 no, quizá 70 o así pero que se sienta el peso.»
- Placa con 16 llaveros como máximo.

## Resistencia (método y cifras)

- PLA impreso plano, resistencia de cálculo 35 MPa. Elementos finitos 2D (tensión plana, con
  grosor variable donde hay bisel) para el tirón; cálculo a mano para doblar el tapón hacia fuera.
- Dos casos de tirón: contacto amplio (la anilla apoya en media vuelta del agujero) y anilla
  fina (±30°), que es el realista.
- Las capas de otro color en una zona que carga **no cuentan** como pared (la unión entre
  colores en la misma capa es débil). En la «doble cara» la cápsula salmón del reverso llegaba
  al agujero y se sobrestimó la resistencia (201 → 160 N); se corrigió dejando el tapón negro macizo.

| Estado | Tirón (amplio / fina) | Doblar |
| --- | --- | --- |
| v1 silueta | ~150 N | ~23 N |
| aro reforzado | ~230 N | ~43 N |
| tapón macizo | ~221 / ~183 N | ~46 N |
| bisel | ~170 / ~140 N | ~35 N |
| v2 botella con ojal | ~201 / ~143 N | ~47 N |
| v3 primera capa | ~233 / ~186 N | ~51 N |

## Inclinación de la anilla

- Un túnel recto de 4,4 mm con agujero de 3,5 mm deja inclinarse un alambre de 1,5 mm solo 23°:
  el llavero chocaba y no se ponía paralelo a las llaves.
- Con bisel de 1 mm por las dos caras, 35° (con 45° el bisel nunca deja pasar de 45°).
- El ojal alargado da holgura justo en la dirección del giro (a lo largo de la botella): 55°.
  De lado sigue en 35°.
- Quitar el bisel de la cara de la cama (v3) solo baja de 55° a 52°.
- Una llave típica (2,2 mm, agujero de 4,5 mm) deja ~46°; una fina (2,0 mm, 5 mm), ~52°.
- Criterio: un alambre recto de grosor d cruza el agujero biselado a un ángulo φ si, en el corte,
  la holgura mínima entre las paredes (contando el bisel) sigue siendo ≥ d.

## Impresión real (v2, 1 nov 2026)

- Bambu Studio: 6,89 g de llavero, 5,95 g de purga, 1,59 g de torre: 14,43 g, 16 cambios de
  filamento, 51 min 36 s, 0,36 €. La purga y la torre son el 52 % del filamento.
- Algunos se combaron y despegaron. Causas confirmadas: ventana abierta con viento, placa sin
  lavar y la punta del cuello con poco apoyo (biseles por la cara de la cama). La v3 lo corrige.
- El brim salía naranja: Bambu hace el brim con el primer filamento de la primera capa, y por
  defecto ordena por el de menos área. Se fija con `first_layer_print_sequence = "1 2 3"` en la placa.

## Cómo se regenera

Scripts en `fuente/` (Python con `trimesh`, `shapely`, `manifold3d`, `matplotlib`). No corren en CI:
los STL y `.3mf` de cada carpeta son la salida guardada. La web hace los GLB desde los STL
(`3d-models/web.py`).

```
cd llaveros/st26/fuente
python3 rehacer.py    # STL de los once estados: completo, por color y vista para la web
python3 make_a1.py    # .3mf de la v3 para la A1: un llavero y placa de 16
```

| Script | Qué hace |
| --- | --- |
| `rehacer.py` | Extruye las siluetas con el grosor, relieve, incrustación de detrás (`espejo` o `traspaso`) y biseles por capas de cada estado |
| `make_a1.py` | Proyectos de la v3: colores, relleno 70 % con modificador al 100 % en cuello y tapón, brim negro, placa de 16 y torre |
| `make_3mf.py` | Escribe el `.3mf` de Bambu Studio |
| `bbl_profiles.py` | Descarga y resuelve los perfiles oficiales de la A1 (`inherits` e `include`); caché en `bbl_cache/` |
| `siluetas_artefacto.json` | Siluetas 2D de todos los estados, en mm |

Por rehacer si hace falta cambiar el logo: el trazado desde la imagen (`referencia/logo-st26.png`)
y el cálculo de resistencia por elementos finitos. Al escribir el `.3mf`, precisión `%.9g` en los
vértices (con `%.6g` la malla deja de ser cerrada).
