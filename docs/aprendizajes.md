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
