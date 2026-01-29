# Labil - Issues & Features Tracker

## Estado actual: v4.2 (en progreso)

---

## 🔴 BUGS CRÍTICOS

### 1. ~~Tamaño de formas fijo~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** NodeResizer habilitado, nodos se adaptan al resize manual
- Shift+Enter para saltos de línea en texto

### 2. ~~No se pueden crear swimlanes manualmente~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Botón "≡" en toolbar bottom para añadir swimlanes

### 3. ~~Conexiones solo top/bottom~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** 8 handles (4 source + 4 target) con IDs únicos, connectionMode="loose"

### 4. ~~Minimap no aparece~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** MiniMap como hijo directo de ReactFlow con position="bottom-right"

### 5. ~~Atajos de teclado no funcionan~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Handlers corregidos, skip cuando input/textarea activo

### 6. ~~Undo/Redo botones no funcionan~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Funciones locales que trabajan con state local + store sync
- saveToHistory() se llama después de cada acción (drag, add, delete, etc.)

### 7. ~~Duplicar nodo resetea posición~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Usa setNodes con callback para obtener posición actual

### 8. ~~No permite saltos de línea en texto~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Shift+Enter para nueva línea, Enter solo para confirmar
- whitespace-pre-wrap para mostrar saltos

---

## 🟡 MEJORAS UX COMPLETADAS

### 9. ~~Toolbar en posición incorrecta~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Toolbar movido a Panel position="bottom-center"

### 10. ~~Edición de forma debe ser flotante~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Toolbar flotante aparece sobre el nodo seleccionado

### 11. ~~Zoom simplificado~~ ✅ ARREGLADO
- **Estado:** Completado
- **Solución:** Solo +/- y botón de centrar/fit, sin slider

---

## ✅ COMPLETADO (v4.2)

- [x] Formas SVG (diamond, hexagon, chevron, octagon) - renderizado correcto
- [x] Panel del agente conversacional con plan + confirmación
- [x] Títulos auto-generados en historial
- [x] Estructura de paneles hover/pin
- [x] API con requestPlan y generación de títulos
- [x] NodeResizer para redimensionar nodos
- [x] Swimlanes en toolbar
- [x] Conexiones en 4 direcciones
- [x] MiniMap visible
- [x] Undo/Redo funcionando
- [x] Duplicar sin resetear posición
- [x] Toolbar en bottom
- [x] Edición flotante sobre nodo
- [x] Zoom +/- simplificado
- [x] Saltos de línea con Shift+Enter

---

## 🧪 VERIFICACIÓN

| Feature | Testeado | Funciona | Notas |
|---------|----------|----------|-------|
| Formas SVG | ✅ | ✅ | Diamond, hex, chevron OK |
| Agente chat | ✅ | ✅ | Plan + confirmación OK |
| Undo/Redo | ✅ | ✅ | Botones y atajos |
| Duplicar | ✅ | ✅ | Sin reset de posición |
| Conexiones | ✅ | ✅ | 4 direcciones |
| Minimap | ✅ | ✅ | Bottom-right |
| Shortcuts | ✅ | ✅ | Cmd+Z, Cmd+Shift+Z, Cmd+D |
| Resize nodos | ✅ | ✅ | NodeResizer activo |
| Swimlane manual | ✅ | ✅ | Botón en toolbar |
| Saltos línea | ✅ | ✅ | Shift+Enter |
| Toolbar bottom | ✅ | ✅ | Panel bottom-center |
| Edit flotante | ✅ | ✅ | Sobre nodo seleccionado |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Undo/Redo
- El historial se guarda con debounce de 500ms después de cada acción
- Funciones locales en FlowCanvas que sincronizan con store
- `isDraggingRef` evita guardar durante el drag, solo al soltar

### Conexiones
- 8 handles por nodo: 4 source + 4 target
- IDs únicos: top, left, bottom, right, top-source, left-source, etc.
- connectionMode="loose" para flexibilidad

### Texto multilínea
- Shift+Enter crea salto de línea
- Enter confirma edición
- whitespace-pre-wrap para renderizar

---

*Última actualización: 2026-01-29 22:50*
