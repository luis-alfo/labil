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
