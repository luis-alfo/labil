'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useUIStore } from '@/stores/ui'
import { useDiagramStore } from '@/stores/diagram'

const DIAGRAM_TYPES = [
  { id: 'flowchart', label: 'Flujo de producto', description: 'Swimlanes, pasos, decisiones' },
  { id: 'erDiagram', label: 'Modelo de datos', description: 'Entidades y relaciones' },
  { id: 'sequenceDiagram', label: 'Secuencia', description: 'Interacciones temporales' },
] as const

export function NewPanel() {
  const [selectedType, setSelectedType] = useState<string>('flowchart')
  const { expandedPanel, closeAllPanels, openPanel } = useUIStore()
  const { setDiagramType, setMermaidCode } = useDiagramStore()
  const isExpanded = expandedPanel === 'new'

  const handleCreate = () => {
    const typeMap: Record<string, 'flowchart' | 'erDiagram' | 'sequenceDiagram'> = {
      flowchart: 'flowchart',
      erDiagram: 'erDiagram',
      sequenceDiagram: 'sequenceDiagram',
    }

    const templates: Record<string, string> = {
      flowchart: `flowchart LR
  subgraph Actor1[Actor 1]
    A[Paso 1] --> B[Paso 2]
  end`,
      erDiagram: `erDiagram
  ENTITY1 ||--o{ ENTITY2 : has
  ENTITY1 {
    string id
    string name
  }`,
      sequenceDiagram: `sequenceDiagram
  participant A as Actor 1
  participant B as Actor 2
  A->>B: Mensaje`,
    }

    setDiagramType(typeMap[selectedType])
    setMermaidCode(templates[selectedType])
    closeAllPanels()
    openPanel('agent')
  }

  if (!isExpanded) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className="fixed bottom-4 left-4 z-50 w-64 glass-panel rounded-lg overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          Nuevo diagrama
        </span>
        <button
          onClick={closeAllPanels}
          className="text-text-tertiary hover:text-text transition-colors text-lg leading-none"
        >
          ×
        </button>
      </div>

      {/* Type selection */}
      <div className="p-3 space-y-2">
        {DIAGRAM_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedType(type.id)}
            className={`
              w-full px-3 py-2 rounded-md text-left
              transition-colors duration-100
              ${
                selectedType === type.id
                  ? 'bg-accent-subtle border border-accent text-accent'
                  : 'hover:bg-white/50 border border-transparent'
              }
            `}
          >
            <div className="text-sm font-medium">{type.label}</div>
            <div className="text-xs text-text-tertiary">{type.description}</div>
          </button>
        ))}
      </div>

      {/* Create button */}
      <div className="p-3 border-t border-border-subtle">
        <button
          onClick={handleCreate}
          className="
            w-full px-4 py-2 rounded-md
            bg-accent text-white text-sm font-medium
            hover:bg-accent/90
            transition-colors duration-100
          "
        >
          Crear
        </button>
      </div>
    </motion.div>
  )
}
