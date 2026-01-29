'use client'

import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useProjectStore } from '@/stores/project'
import { useUIStore } from '@/stores/ui'

export function HistoryPanel() {
  const {
    name,
    setName,
    history,
    historyIndex,
    createSnapshot,
    restoreSnapshot,
    exportProject,
    importProject,
    undo,
    redo,
    canUndo,
    canRedo,
  } = useProjectStore()
  const { closeAllPanels } = useUIStore()

  const [isNaming, setIsNaming] = useState(false)
  const [snapshotName, setSnapshotName] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSaveSnapshot = () => {
    if (snapshotName.trim()) {
      createSnapshot(snapshotName.trim())
      setSnapshotName('')
      setIsNaming(false)
    }
  }

  const handleExport = () => {
    const json = exportProject()
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${name.replace(/\s+/g, '-').toLowerCase()}.labil.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const json = event.target?.result as string
        importProject(json)
      }
      reader.readAsText(file)
    }
  }

  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }

  const formatDate = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }

  // Agrupar por fecha
  const groupedHistory = history.reduce((acc, entry, index) => {
    const date = formatDate(entry.timestamp)
    if (!acc[date]) acc[date] = []
    acc[date].push({ ...entry, index })
    return acc
  }, {} as Record<string, (typeof history[0] & { index: number })[]>)

  return (
    <motion.div
      initial={{ opacity: 0, x: 20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 20, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className="fixed top-4 right-4 z-50 w-80 glass-panel rounded-lg flex flex-col overflow-hidden"
    >
      {/* Header con Import/Export */}
      <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          Historial
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={handleExport}
            className="p-1.5 text-text-tertiary hover:text-text hover:bg-surface/50 rounded transition-colors"
            title="Exportar"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-1.5 text-text-tertiary hover:text-text hover:bg-surface/50 rounded transition-colors"
            title="Importar"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleImport}
            className="hidden"
          />
          <div className="w-px h-4 bg-border-subtle mx-1" />
          <button
            onClick={closeAllPanels}
            className="p-1.5 text-text-tertiary hover:text-text hover:bg-surface/50 rounded transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4 max-h-[400px] overflow-y-auto">
        {/* Nombre del proyecto */}
        <div>
          <label className="text-xs text-muted block mb-1">Proyecto</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-surface/50 border border-muted/30 rounded px-2 py-1 text-sm text-text focus:outline-none focus:border-primary"
          />
        </div>

        {/* Guardar versión */}
        <button
          onClick={() => setIsNaming(true)}
          className="w-full px-3 py-2 bg-primary/10 text-primary text-sm rounded hover:bg-primary/20 transition-colors"
        >
          + Guardar versión
        </button>

        {/* Modal para nombrar snapshot */}
        {isNaming && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2"
          >
            <input
              value={snapshotName}
              onChange={(e) => setSnapshotName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSaveSnapshot()}
              placeholder="Nombre de la versión..."
              autoFocus
              className="flex-1 bg-surface/50 border border-primary/50 rounded px-2 py-1 text-sm focus:outline-none"
            />
            <button
              onClick={handleSaveSnapshot}
              className="px-3 py-1 bg-primary text-white text-sm rounded"
            >
              Guardar
            </button>
            <button
              onClick={() => setIsNaming(false)}
              className="px-2 py-1 text-muted text-sm"
            >
              Cancelar
            </button>
          </motion.div>
        )}

        {/* Timeline */}
        <div className="space-y-3">
          <span className="text-xs text-muted">Historial</span>

          {Object.entries(groupedHistory)
            .reverse()
            .map(([date, entries]) => (
              <div key={date}>
                <div className="text-xs text-muted/70 mb-1">{date}</div>
                <div className="space-y-1 border-l-2 border-muted/20 pl-3">
                  {entries.reverse().map((entry) => {
                    const isCurrent = entry.index === historyIndex
                    return (
                      <motion.button
                        key={entry.index}
                        onClick={() => restoreSnapshot(entry.index)}
                        className={`w-full text-left p-2 rounded transition-colors group ${
                          isCurrent
                            ? 'bg-primary/10 border border-primary/30'
                            : 'hover:bg-surface/50'
                        }`}
                        whileHover={{ x: 2 }}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted">{formatTime(entry.timestamp)}</span>
                          {entry.named && (
                            <span className="px-1.5 py-0.5 bg-primary/10 text-primary text-xs rounded">
                              {entry.named}
                            </span>
                          )}
                          {isCurrent && (
                            <span className="px-1.5 py-0.5 bg-accent/20 text-accent text-xs rounded">
                              actual
                            </span>
                          )}
                        </div>
                        {/* Título auto-generado */}
                        <p className="text-xs text-text/80 mt-0.5 font-medium truncate">
                          {entry.title}
                        </p>
                        {entry.prompt && entry.prompt !== entry.title && (
                          <p className="text-xs text-text/50 mt-0.5 truncate italic">
                            "{entry.prompt}"
                          </p>
                        )}
                      </motion.button>
                    )
                  })}
                </div>
              </div>
            ))}

          {history.length === 0 && (
            <p className="text-xs text-muted/50 text-center py-4">
              Sin historial todavía
            </p>
          )}
        </div>
      </div>
    </motion.div>
  )
}
