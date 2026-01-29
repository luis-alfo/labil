'use client'

import { motion } from 'framer-motion'
import { useUIStore } from '@/stores/ui'

// Placeholder - will be expanded with actual project list
const MOCK_PROJECTS = [
  { id: '1', name: 'Onboarding Flow', type: 'flowchart' },
  { id: '2', name: 'Data Model v2', type: 'erDiagram' },
  { id: '3', name: 'Auth Sequence', type: 'sequenceDiagram' },
]

export function ListPanel() {
  const { expandedPanel, closeAllPanels } = useUIStore()
  const isExpanded = expandedPanel === 'list'

  if (!isExpanded) return null

  return (
    <motion.div
      initial={{ opacity: 0, x: -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: -20, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className="fixed top-4 left-4 z-50 w-56 glass-panel rounded-lg overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          Diagramas
        </span>
        <button
          onClick={closeAllPanels}
          className="text-text-tertiary hover:text-text transition-colors text-lg leading-none"
        >
          ×
        </button>
      </div>

      {/* Project list */}
      <div className="p-2">
        {MOCK_PROJECTS.map((project) => (
          <button
            key={project.id}
            className="
              w-full px-3 py-2 rounded-md
              text-left text-sm
              text-text-secondary hover:text-text
              hover:bg-white/50
              transition-colors duration-100
              flex items-center gap-2
            "
          >
            <span className="w-4 h-4 rounded bg-surface border border-border" />
            <span className="truncate">{project.name}</span>
          </button>
        ))}
      </div>
    </motion.div>
  )
}
