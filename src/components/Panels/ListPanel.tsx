'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { usePersistenceStore } from '@/stores/persistence'

export function ListPanel() {
  const { expandedPanel, closeAllPanels } = useUIStore()
  const { user, openLoginModal } = useAuthStore()
  const {
    diagrams,
    isLoadingDiagrams,
    loadDiagrams,
    currentDiagramId,
    setCurrentDiagram
  } = usePersistenceStore()

  const isExpanded = expandedPanel === 'list'

  // Load diagrams when user is available and panel opens
  useEffect(() => {
    if (isExpanded && user) {
      loadDiagrams(user.id)
    }
  }, [isExpanded, user, loadDiagrams])

  if (!isExpanded) return null

  const handleSelectDiagram = (diagramId: string) => {
    setCurrentDiagram(diagramId)
    // TODO: Load diagram into canvas
  }

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

      {/* Diagram list */}
      <div className="p-2 max-h-80 overflow-y-auto">
        {!user ? (
          <div className="px-3 py-4 text-center">
            <p className="text-sm text-text-tertiary mb-3">
              Inicia sesión para guardar tus diagramas
            </p>
            <button
              onClick={() => { closeAllPanels(); openLoginModal() }}
              className="text-sm text-accent hover:underline"
            >
              Iniciar sesión
            </button>
          </div>
        ) : isLoadingDiagrams ? (
          <div className="px-3 py-4 text-sm text-text-tertiary text-center">
            Cargando...
          </div>
        ) : diagrams.length === 0 ? (
          <p className="px-3 py-4 text-sm text-text-tertiary text-center">
            No hay diagramas guardados
          </p>
        ) : (
          diagrams.map((diagram) => (
            <button
              key={diagram.id}
              onClick={() => handleSelectDiagram(diagram.id)}
              className={`
                w-full px-3 py-2 rounded-md
                text-left text-sm
                transition-colors duration-100
                flex items-center gap-2
                ${currentDiagramId === diagram.id
                  ? 'bg-accent/10 text-accent'
                  : 'text-text-secondary hover:text-text hover:bg-white/50'
                }
              `}
            >
              <span
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  currentDiagramId === diagram.id ? 'bg-accent' : 'bg-border'
                }`}
              />
              <span className="truncate flex-1">{diagram.name}</span>
            </button>
          ))
        )}
      </div>
    </motion.div>
  )
}
