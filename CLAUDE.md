# Memoria del proyecto

## Forma de trabajar con Luis

- Cada vez que Claude explique algo, debe guardarlo aquí, en "Aprendizajes": el objetivo es ir creando códigos compartidos y entender las realidades de Luis (de negocio y personales).
- Idioma de trabajo: español.

## Qué hay en este repositorio

- `src/`, `e2e/`… → Labil, editor de diagramas (Next.js + Supabase).
- `cajones-isla/` → proyecto de fabricación (impresión 3D): cajones para los huecos de la isla de la cocina. Ver su README.

## Aprendizajes

### Impresión 3D / prototipado (cajones de la isla, 2026-10)

- **Vocabulario compartido**
  - *Hueco*: el agujero de la estantería, 130 mm ancho × 135 mm alto (medido por Luis).
  - *Marco de prueba* (o "marco de puerta"): pieza que reproduce solo el contorno exterior del cajón, con poca profundidad, para probar el encaje gastando el mínimo plástico. Siempre se prototipa esto antes que el cajón entero.
  - *Holgura*: lo que se resta al hueco **por cada lado**. 0,5 mm por lado = 1 mm en total.
- **Criterios por defecto** (ajustables según la prueba)
  - Holgura de partida: 0,5 mm por lado para piezas que deslizan en madera.
  - Pared: 1,6 mm (4 líneas con boquilla 0,4) → pared maciza, sin relleno.
  - Escuadras a 45° en las esquinas interiores para que el marco no se deforme.
  - Chaflán de 0,4 mm en la base para la "pata de elefante" (la primera capa sale más ancha y falsearía la medida).
  - Imprimir tumbado, sin soportes.
- **Herramienta**: los modelos se generan con scripts Python paramétricos (`manifold3d` + `trimesh`) para poder iterar cambiando solo números.
- **Estado**: paso 1 hecho (marco de prueba 129 × 134 × 10 mm, ≈ 11 g). Pendiente: resultado de la prueba de encaje de Luis → fijar holgura → diseñar el cajón.
