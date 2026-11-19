# Aprendizajes y códigos compartidos — Labil

Registro vivo de explicaciones, decisiones y convenciones acordadas.

## 2026-11-16 · Identidad visual y favicon

- **Wordmark**: `labil` en minúscula, Plus Jakarta Sans semibold, verde `#6BCB77`
  (`src/app/page.tsx`, `LoginModal.tsx`). El verde es el color de *marca*.
- **Acento de UI**: violeta `#8B5CF6` (selección, foco, IA). Se usa como color
  secundario en el logo/favicon, nunca como principal.
- **Neutros "Warm Clarity"**: fondo `#FAFAFA`, superficie `#F3F2EE`, texto `#1A1919`.
- **Lenguaje gráfico**: Labil = diagramas → los iconos se construyen con nodos,
  conectores y formas de flujo (rect, rombo, círculo), no con letras sueltas.
  Una "l" sola a 16px se lee como "!" — evitarlo.
- Primera ronda de favicons (verde `#6BCB77` + violeta) descartada: Luis pidió
  usar el DS **LG Señal** (ver abajo). Queda en el historial de git.
- **Cómo activar una en Next.js (App Router)**: copiar `X.svg` → `src/app/icon.svg`
  y `X-180.png` → `src/app/apple-icon.png`. Next genera los `<link>` solo.

## 2026-11-16 · Design system de referencia: LG Señal

- **El DS que manda es LG Señal** (https://claude.ai/artifact/5Rrn4fTxHfgcLRTrFg4XEz),
  el sistema de **Lagu**: la marca rápida (día a día, facturas, cobros, trading).
  Hermana de **La Guarida**, cuyo DS es **LG Casa**. «La Casa permanece, la Señal cambia».
- Reglas clave: **siempre en oscuro**; fósforo `signal #24e824` = lo vivo/lo elegido;
  `surface #2b312b`, `surface-raised #333a33`, `ink #f3fbf1`, `ink-muted #c9e1c9`
  (Verde La Guarida), `ink-faint/line-strong #86a08a`; píxeles apagados
  `rgba(201,225,201,.07)`. Rejilla de **4px**, radios 0/2/4px, **sin sombras**.
  Una sola letra: **JetBrains Mono**; **minúsculas siempre**. Movimiento a saltos (`steps`).
- **Logo de Lagu** = hexágono con «l a g u» del FigJam. **No se dibuja a mano**:
  ningún favicon/icono debe usar un hexágono hasta que se exporte el SVG oficial.
- ⚠️ El código de Labil aún usa la paleta "Warm Clarity" (claro, violeta `#8B5CF6`,
  Plus Jakarta) y el wordmark verde `#6BCB77`. Pendiente decidir si Labil migra a LG Señal.
- **Favicons LG Señal** en `public/favicon-options/` (8×8 píxeles de 4px, gesto `BitFigure`):
  - **A · Bitfigura**: la «l» de labil en bitmap fósforo + nodo `ink`, sobre rejilla apagada.
  - **B · Flujo**: nodo → arista (`ink-faint`) → nodo, en píxeles.
  - **C · Capa encima**: marcas de esquina de `Panel` + nodo de fósforo, sobre `surface-raised`.

## 2026-11-16 · Reencuadre: «de la letra al objeto»

- **Tesis de Luis**: *diseño objetos desde la escritura, con IA*. Labil no es "un editor
  de diagramas con IA": la **escritura es el material** y el objeto es una forma que toma.
- **El nombre ya lo dice**: *lábil* = inestable, que cambia de estado con facilidad.
  Labil es el estado intermedio entre letra y objeto. Encaja con LG Señal
  («la Señal cambia», «ruido que se ordena»).
- **Lo que el código ya demuestra**: `mermaidToFlow` / `flowToMermaid` hacen
  texto ⇄ objeto en ambos sentidos. Ese ida y vuelta es el núcleo; el canvas es una vista.
- **Respuestas de Luis (2026-11-16)**:
  - **Objeto** = *descripciones digitales que crean objetos reales*. La escritura genera
    una descripción (modelo, plano, fichero de fabricación) y esa descripción se fabrica.
  - **Quién escribe**: Luis. Labil es su herramienta/taller, no (de momento) un producto para terceros.
  - **Labil es parte de Lagu** → usa **LG Señal** entero (oscuro, fósforo, píxel, JetBrains Mono, minúsculas).
- **Cadena de Labil**: `letra (lo que escribe Luis) → descripción digital (la IA la genera) → objeto real`.
  Hoy la "descripción" es Mermaid y el "objeto" un diagrama; mañana la descripción puede ser
  un modelo paramétrico (p. ej. OpenSCAD/CadQuery) o un plano de corte (SVG) y el objeto, una pieza.
- **Implicaciones** (iniciales):
  - La fuente de verdad es el texto; el objeto se regenera y se puede volver a escribir.
  - "Objeto" hoy = diagrama. ¿Mañana: documentos, interfaces, piezas físicas?
  - Gesto de marca: una letra que se reordena hasta ser forma (animación de descifrado).
  - El favicon muestra la transición letra → objeto. Propuestas actuales (LG Señal, 8×8 píxeles):
    - **A · Extrusión**: la «l» en fósforo gana volumen (extrusión en `ink-faint`): la letra se vuelve sólido.
    - **B · Capa a capa**: arriba, renglones de escritura; abajo, el objeto fabricándose por capas (impresión 3D).
    - **C · Ruido que se ordena**: píxeles sueltos (letras) que se compactan en un bloque de fósforo.
  - Las rondas anteriores (Warm Clarity y LG Señal "diagrama") quedan en el historial de git.

## 2026-11-16 · Favicon elegido

- **Luis eligió C · Ruido que se ordena**: píxeles sueltos (letras) que se compactan en un
  bloque de fósforo `#24e824`. Es el gesto de LG Señal aplicado a «de la letra al objeto».
- Activo en `src/app/icon.svg` (pestaña) y `src/app/apple-icon.png` (180px, iOS).
  Next.js App Router genera los `<link>` automáticamente; no hace falta tocar `layout.tsx`.
- Las alternativas siguen en `public/favicon-options/` como referencia.

## 2026-11-16 · Web v2: una página por objeto (LG Señal)

- **Qué pidió Luis**: pasar la web a LG Señal sin perder lo anterior; guardar la web actual
  como archivo y tener el histórico; que cada objeto tenga su página con sus versiones y
  borradores; pensar el paso entre borradores en el móvil; y el coste de cada uno a 20 €/kg.
- **Dónde estaba "el site"**: GitHub Pages sale de `docs/` y lo despliega
  `.github/workflows/pages.yml` en cada push a `main` o a `claude/**` que toque esas carpetas.
  **El último push gana**: si otra sesión empuja una rama con la web vieja, la pisa.
  Lo seguro es fusionar a `main` y desplegar solo desde `main`.
- **El histórico**: el trabajo estaba repartido en ramas. Se unieron (merge, con su historia):
  estropajero + barra de baño, botonera NCH y cajones de la isla. El llavero de la habitación 26
  se copió (su rama tocaba la app Next.js). La web anterior queda en `docs/v1/`.
- **Vocabulario de la web**: *objeto* (el secadero, la botonera…) → *estados* en orden.
  Tipos: **impresa** (versión, verde fósforo), **por imprimir** (versión aún no impresa, ámbar),
  **prueba** (pieza para validar un encaje), **borrador** (diseño sin imprimir, cuadro hueco).
- **Móvil, entre un borrador y otro**: un estado por pantalla. Arriba, un raíl con todos los
  estados (el actual en fósforo, centrado). Abajo, en la zona del pulgar, «← anterior · n/N ·
  siguiente →» con el nombre del vecino. Se puede deslizar sobre la ficha, no sobre el visor
  (ahí el dedo gira el modelo). Cada estado dice qué cambia en gramos y euros respecto al anterior.
- **Coste (cómo se calcula)**: los 3MF del repo solo traen geometría (sin datos del laminador),
  así que `3d-models/costes.py` corta cada pieza en capas de 0,2 mm y suma pared, techos/suelos
  macizos y relleno al 15 % (PLA 1,26 g/cm³). Con la pared de 2 perímetros salía un 25 % corto;
  con una pared efectiva de 4 líneas coincide con el laminador real: **error medio 4 %, máximo 9 %**
  en 8 piezas. Contrastes: cajón 102 g (notas: 109), botonera 2×2 20 g (≈19), marco 11 g (11).
  **No incluye la purga** de los cambios de color (en el llavero ST26 fue el 52 % del filamento).
- **Cifras (16 nov 2026)**: imprimir todo el archivo ≈ 722 g ≈ 14,46 €. El Secadero v2 ≈ 43 g ≈ 0,86 €.
- **Respuestas de Luis (16 nov 2026)**: la web se publica **solo desde `main`**. De los cajones
  de la isla y de la barra de baño **no se ha impreso nada**: siguen como borradores y pruebas sin imprimir.
- El **llavero «habitación 26»** (tipo motel, «Room 26» grabado detrás, mayo 2026) **se imprimió**.
- **Prueba en CI (16 nov 2026)**: la generación entera pasa en GitHub, incluido el paso de la web v2.
  El paso de publicar falló en 3 s y GitHub no guarda su registro. Lo más probable es que el entorno
  `github-pages` solo deje publicar desde ciertas ramas, sin confirmar. La web v2 sale al fusionar en `main`.

## 2026-11-16 · Página de objeto limpia (boceto de Luis en la pizarra)

- **El modelo ocupa toda la pantalla** y encima solo va lo imprescindible:
  - **arriba a la izquierda**, el icono de labil, que lleva al inicio con el listado de objetos;
  - **arriba en el centro**, el nombre del objeto;
  - **arriba a la derecha**, el precio del estado que se ve, en bitmap y sin tarjeta;
  - **abajo a la izquierda (fijo)**, el desplegable de **versiones**. Es un `<select>` nativo:
    en el móvil abre el selector del sistema, el más cómodo con el pulgar;
  - **abajo a la derecha (fijo)**, las **posiciones**: las vistas del modelo (abajo, levantada,
    placa a1…) o, si el estado solo tiene imágenes, las imágenes. Con más de 3 se compactan en
    cuadros numerados con el nombre de la activa encima;
  - **una banda abajo, «↑ detalles»**, que sube una hoja con el resto: tipo, fecha, texto, coste,
    diferencia con el anterior, piezas, imágenes, descargas y anterior/siguiente.
    Se abre tocando o deslizando hacia arriba, y se cierra hacia abajo, tocando fuera o con Esc.
- En escritorio, la hoja de detalles se abre como panel lateral.
- **Vocabulario**: *posición* = una vista o colocación del mismo estado (no es otra versión).

## 2026-11-16 · Proceso y memoria en la web

- **Qué pidió Luis**: que la web enseñe también su **proceso de diseño** (las imágenes que sube:
  bocetos, pizarras, capturas) y una **memoria** de cómo cambia de una versión a otra, con las
  razones (diseño, resistencia del clic, montaje…). Quedó como norma en `CLAUDE.md`.
- **Dónde**: imágenes en `proceso/<objeto>/` (con `proceso/guardar.py`, que reduce y quita el GPS).
  La memoria va en cada estado de `3d-models/objetos.json`. En la web, la hoja de detalles muestra
  «qué cambia y por qué» y «proceso», y `#/<objeto>/memoria` lo cuenta todo seguido.
- **Vocabulario**: *proceso* = el camino (lo que dibuja o fotografía Luis); *imágenes* = el resultado
  (renders, capturas finales); *memoria* = el porqué de cada cambio, por temas.
- **La web es un objeto más** (`labil-web`): v1 beige → v2 LG Señal → página limpia (boceto de la pizarra).
  Para la web, «versión» se dice «publicada».
- Una imagen que Luis pegó en la conversación (su captura de la v2) no llegó como archivo al repositorio.
  Se rehízo la misma captura y el pie lo dice. Si vuelve a pasar, se le avisa.
- **Autonomía (16 nov 2026)**: Luis autorizó a fusionar en `main` yo mismo cuando esté todo listo.

## 2026-11-16 · Desplegable de versiones con la marca

- **Por qué**: el `<select>` nativo abría el selector del sistema (iOS/Android), fuera de LG Señal.
  Luis lo marcó: los controles de la web tienen que ser de la marca, no del sistema.
- **Cómo es**: botón abajo a la izquierda (estado, nombre, «7/7», flecha de píxeles). Al tocarlo
  sube una lista con cada versión: cuadro de estado, nombre, tipo · fecha y precio. La elegida va
  en fósforo, con esquinas rectas. Los nombres se descifran al abrir.
- **Lo que no se pierde del nativo**: filas de 52 px para el pulgar; teclado (↑ ↓, Inicio, Fin,
  Intro, Esc); se cierra tocando fuera; el lector de pantalla lo anuncia como lista de opciones (`listbox`).
- **Norma aplicada**: el cambio entra como estado nuevo de «labil · la web», con su captura y su memoria.
- **Caché del móvil (16 nov 2026)**: justo después de fusionar, Luis seguía viendo el desplegable del
  sistema. Había dos motivos: la publicación tarda unos 3 min y GitHub Pages deja que el móvil guarde
  `app.js` y `app.css` hasta 10 min. Arreglo: `web.py` añade `?v=<commit>` a esos dos archivos en cada
  publicación. `index.html` puede tardar hasta 10 min en refrescarse; si corre prisa, se recarga la página.

## 2026-11-16 · Portada, burbujas y versiones plegadas

- **Safari sí, Chrome no**: el mismo motor lo pintaba bien. Era la caché: Pages deja guardar los
  archivos 10 min y Chrome seguía con el `index.html` viejo. Arreglo de raíz: `index.html` pide
  `version.json` sin caché y carga `app.js`/`app.css` con esa versión. Lo escribe `web.py` en cada publicación.
- **Desplegable**: solo versiones a la vista. Los borradores y las pruebas entre dos versiones van
  plegados en una línea («2 borradores · 31 oct – 1 nov»). Un objeto sin versiones los enseña todos.
- **Burbujas** (vocabulario): *qué cambió* · *feedback* (de Luis o de una *revisión*) · *nos llevó a*
  (el estado siguiente). Dos líneas como mucho, entran por la derecha y se cierran con la ×.
- **Memoria**: línea de tiempo de lo más reciente a lo más antiguo, con flecha grande para volver.
- **Portada**: explica qué es labil, sin precio total. Animación en píxeles: escribes → la IA modela →
  calcula resistencias → evalúa el montaje → prototipa → se imprime. El historial pasa al pie.
- **Realidad aumentada**: en Android aparecía el botón del visor como un círculo blanco. Ahora es
  «ver en tu espacio», con la marca.

## 2026-11-16 · Portada en movimiento (menos texto)

- **Luis: «demasiado texto»** en la portada. Ahora solo quedan la marca, una palabra por fase y la flecha.
- **Secuencia** (unos 14 s, en bucle): *escribes* (la frase) → *se diseña* (las letras se ordenan
  en la pieza, en la rejilla de píxeles) → *se calcula* (mapa de tensiones) → *se imprime* (impresora 3D
  con la placa real de El Secadero v2) → *objeto*.
- **Librería**: three.js 0.160, con versión fija y cargada solo en la portada (importmap en `index.html`).
  La impresión es un plano de corte que sube, y la capa activa es una copia en verde.
- **Lección técnica**: los GLB de trimesh no traen normales; en three.js hay que calcularlas
  (`computeVertexNormals`) o las caras salen negras. model-viewer las calcula solo.

## 2026-11-16 · Portada: fases con nombre, cálculo legible y montaje

- **Vocabulario de las fases** (Luis: nada de «se» impersonal): **definición → diseño → cálculo →
  impresión → montaje**.
- **Cálculo legible**: una flecha de 20 N cae sobre la cuna, la tensión viaja por la estructura hasta
  la unión brazo-pata, el valor sube a 17 MPa y un medidor lo compara con el límite (20 MPa ✓).
- **Montaje**: las piezas salen de la placa y se montan en el grifo en orden: brazo, cuña, marco y cuna.
  El movimiento exacto lo calcula `3d-models/montaje.py`, que alinea la malla de cada pieza en la placa
  con la del modelo montado (error 0,000 mm) y lo guarda en `docs/models/el_secadero_v2_montaje.json`.
  CI lo recalcula en cada publicación.
- **Lecciones técnicas**: (1) el mismo número de vértices no significa el mismo orden; para emparejar
  dos mallas hace falta ICP, no el índice. (2) trimesh necesita `rtree` para su ICP; se escribió uno con
  `scipy` para no añadir dependencias. (3) three.js guarda el color del GLB sin convertir: se compara tal cual.

## 2026-11-16 · Portada: montaje real, estropajo y transiciones

- **Montaje con movimientos reales** (Luis: «que no esté atravesando la pieza»). Cada pieza hace dos tramos:
  sale de la placa hasta su punto de entrada y luego hace su movimiento de montaje. El brazo se desliza
  hacia la pared, la cuña baja, el marco entra a 50° y cae a vertical, y la cuna entra a 60° y baja girando.
  Los ejes y ángulos los calcula `3d-models/montaje.py` a partir del `.scad`.
- **Estropajo realista**: salvauñas con espuma amarilla porosa y una capa verde de fibra, cantos redondeados.
- **Suavidad**: la rejilla conserva el píxel, pero los movimientos ya no van a saltos. Hay fundidos entre fases
  y al reiniciar. Regla para la marca: *a saltos* en la UI, *suave* en el movimiento 3D.

## 2026-11-17 · Barra de baño: de tres borradores a «Trazo»

- Luis pidió repensar el modelo entero: «creo que podemos mejorar mucho». Los tres
  borradores (hilo, carril, rama) se quedan como borradores y el diseño actual es
  **Trazo** (`3d-models/bathroom-trazo/`, con su `APRENDIZAJES.md`).
- **Código compartido**: un modelo no se enseña sin haberlo renderizado y mirado antes.
  `is_volume` solo dice que la malla está cerrada.
- **Código compartido**: la boca de un clip va al lado contrario de la carga.
- **Marco de los GLB**: Y arriba, a derechas y en metros. Para modelos pensados con
  «x derecha, y hacia ti, z arriba» se usa `export_glb()` de `3d-models/_bathroom_context.py`.
- **Realidad de Luis**: sigue el trabajo desde el móvil. La web solo se publica desde `main`,
  así que para verlo antes de fusionar hace falta otra vía (un artefacto de Claude sirvió).
- Las fotos del baño llegaron solo dentro de la conversación; faltan en `proceso/`.

## 2026-11-17 · La web: precio de la prueba bajo el precio del diseño

- Luis vio que al pasar a una pieza de prueba el precio de arriba no cambiaba. No quiere que
  cambie: quiere **el precio del diseño siempre arriba y, debajo, el de la prueba que se ve**,
  con su nombre.
- **Código compartido**: una prueba no es parte del precio del diseño; se enseña aparte.
- Cómo se marca: en `3d-models/objetos.json`, el modelo lleva `"prueba": "<ruta al STL>"`.
  `web.py` le calcula gramos y euros; `app.js` los pinta bajo el precio y en «pruebas antes
  de imprimir», dentro de detalles.

## 2026-11-17 · Regresión: una rama vieja publicó el visor antiguo encima de la web v2

- Qué pasó: Luis pidió poner en la web las fotos de El Secadero ya impreso. Claude trabajaba
  en `claude/3d-model-generation-IEA7l`, una rama que no se había actualizado desde `main`.
  Seguía con el `pages.yml` antiguo, que desplegaba desde cualquier rama `claude/**`, y con el
  visor v1 en `docs/`. Al hacer push, publicó el visor viejo encima de la web v2. Luis lo vio:
  «está la web vieja, no la nueva».
- Cómo se arregló: se relanzó el despliegue de `main` (`workflow_dispatch`) y la web v2 volvió
  en unos dos minutos. La rama se rehízo desde `main` y las fotos se añadieron con el sistema
  de la web v2 (`proceso/guardar.py` y `3d-models/objetos.json`).
- **Código compartido**: antes de tocar la web o hacer push, `git fetch` y mirar si `main` ha
  cambiado. Si ha cambiado, la rama se rehace desde `main` antes de seguir. Otras sesiones
  trabajan en paralelo y la web puede no ser la que la sesión recuerda.
- **Código compartido**: «he comprobado que la web carga» no basta. Hay que comprobar que es
  **la web que toca** (aquí, que siguiera siendo la v2), no solo que responde 200.
- Ninguna otra rama remota conserva el disparador antiguo (comprobado el 17 nov). Para que no
  pueda repetirse ni con una rama vieja, Luis puede limitar el entorno `github-pages` a `main`
  en los ajustes del repo (Settings → Environments → github-pages → Deployment branches).

## 2026-11-19 · larc hq: cajonera del elevador de pantalla

- **larc hq** = la oficina de Luis. Es el nombre del objeto y lo que se graba en él.
- **Luis mide con tarjetas**: pone tarjetas estándar (85,6 × 54 mm) junto a la pieza y hace la foto.
  Las medidas se leen contando tarjetas; lo que no toca una tarjeta es estimado y se dice.
- **El grabado sigue una fórmula**: `NOMBRE | VERSIÓN | FECHA DE DISEÑO (ddmmaa)`, en JetBrains Mono,
  como El Secadero. Luis lo pide con «v1» aunque no esté impreso: en la web va como versión por imprimir.
- **Fotos con datos personales** (nombre, números de socio o de identificación): se publican con
  los datos tapados (decisión de Luis, 19 nov 2026).
- Detalle del diseño en `3d-models/larc-hq/APRENDIZAJES.md`.
- **Curvas, regla común a LG Casa y a los objetos**: los radios de LG Casa (1–6 px) y de LG Señal
  (0/2/4 px) son cortos a propósito; no son la fuente de las curvas. La curva está en el **arco de
  La Guarida**: una línea de grosor constante que dobla con radio ≈ 4 × su grosor y acaba en punta
  redonda. Para piezas: «lámina que se dobla, radio = 4 × grosor»; cantos pequeños en 2 / 4 / 6 mm.
- **Del DS digital al objeto** (Luis, 19 nov 2026: «son DS para el mundo digital, tenemos que saber
  traerlo al físico»): no se leen píxeles como milímetros. En un objeto hay tres escalas de curva:
  **canto** (1–2 mm, lo que nota el dedo; ahí viven los radios de LG Casa y LG Señal), **esquina**
  (4–8 mm, quita lo afilado) y **gesto** (20–45 mm, lo que el ojo llama curvo). De un logo o de un
  DS se copia la proporción, no la medida.
