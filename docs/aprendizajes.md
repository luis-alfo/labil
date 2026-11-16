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
- **Propuestas de favicon** en `public/favicon-options/`:
  - **A · Letra**: "l" blanca que termina en conector + nodo violeta, fondo verde.
  - **B · Flujo**: nodo verde → conector → rombo violeta sobre papel cálido;
    se adapta a modo oscuro (`prefers-color-scheme`).
  - **C · Nodos**: una "L" hecha de nodos y aristas sobre fondo `#1A1919`.
- **Cómo activar una en Next.js (App Router)**: copiar `X.svg` → `src/app/icon.svg`
  y `X-180.png` → `src/app/apple-icon.png`. Next genera los `<link>` solo.
