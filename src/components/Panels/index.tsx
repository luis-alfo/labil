'use client'

import { useEffect, useRef, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import { useUIStore, PanelId } from '@/stores/ui'
import { PanelBubble } from './PanelBubble'
import { ListPanel } from './ListPanel'
import { NewPanel } from './NewPanel'
import { AgentPanel } from './AgentPanel'
import { HistoryPanel } from './HistoryPanel'

// Icons as simple SVGs
const ListIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
  </svg>
)

const PlusIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12h14" />
  </svg>
)

const ChatIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
)

const HistoryIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

export function Panels() {
  const { expandedPanel, togglePanel, closeAllPanels, openPanel, pinPanel, isPinned } = useUIStore()
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const closeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  const isListExpanded = expandedPanel === 'list'
  const isNewExpanded = expandedPanel === 'new'
  const isAgentExpanded = expandedPanel === 'agent'
  const isHistoryExpanded = expandedPanel === 'history'

  // Manejar hover sobre bubble - abre el panel después de un pequeño delay
  const handleBubbleHover = useCallback((panel: PanelId) => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current)
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)

    hoverTimeoutRef.current = setTimeout(() => {
      openPanel(panel)
    }, 150) // Pequeño delay para evitar aperturas accidentales
  }, [openPanel])

  // Manejar salida del hover
  const handleBubbleLeave = useCallback(() => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current)
  }, [])

  // Manejar entrada al panel - cancela el cierre
  const handlePanelEnter = useCallback(() => {
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)
  }, [])

  // Manejar salida del panel - cierra después de un delay si no está pinneado
  const handlePanelLeave = useCallback((panel: PanelId) => {
    if (isPinned(panel)) return // No cerrar si está pinneado

    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)
    closeTimeoutRef.current = setTimeout(() => {
      closeAllPanels()
    }, 300) // Delay antes de cerrar
  }, [closeAllPanels, isPinned])

  // Click en bubble - pinnea el panel
  const handleBubbleClick = useCallback((panel: PanelId) => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current)
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)

    openPanel(panel)
    pinPanel(panel)
  }, [openPanel, pinPanel])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modKey = isMac ? e.metaKey : e.ctrlKey

      // Cmd/Ctrl + 1: Toggle list
      if (modKey && e.key === '1') {
        e.preventDefault()
        togglePanel('list')
        pinPanel('list')
      }
      // Cmd/Ctrl + 2: Toggle new (cambiado de N para no colisionar con navegador)
      if (modKey && e.key === '2') {
        e.preventDefault()
        togglePanel('new')
        pinPanel('new')
      }
      // Cmd/Ctrl + 3: Toggle agent (cambiado de J)
      if (modKey && e.key === '3') {
        e.preventDefault()
        togglePanel('agent')
        pinPanel('agent')
      }
      // Cmd/Ctrl + 4: Toggle history (cambiado de H para no colisionar con historial del navegador)
      if (modKey && e.key === '4') {
        e.preventDefault()
        togglePanel('history')
        pinPanel('history')
      }
      // Escape: Close all
      if (e.key === 'Escape') {
        closeAllPanels()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [togglePanel, closeAllPanels, pinPanel])

  // Limpiar timeouts al desmontar
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current)
      if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)
    }
  }, [])

  return (
    <>
      {/* Bubbles - top left: Lista de diagramas */}
      <AnimatePresence>
        {!isListExpanded && (
          <PanelBubble
            icon={<ListIcon />}
            label="Diagramas"
            shortcut="⌘1"
            isExpanded={isListExpanded}
            onClick={() => handleBubbleClick('list')}
            onMouseEnter={() => handleBubbleHover('list')}
            onMouseLeave={handleBubbleLeave}
            position="top-left"
          />
        )}
      </AnimatePresence>

      {/* bottom-left: Nuevo diagrama */}
      <AnimatePresence>
        {!isNewExpanded && (
          <PanelBubble
            icon={<PlusIcon />}
            label="Nuevo"
            shortcut="⌘2"
            isExpanded={isNewExpanded}
            onClick={() => handleBubbleClick('new')}
            onMouseEnter={() => handleBubbleHover('new')}
            onMouseLeave={handleBubbleLeave}
            position="bottom-left-offset"
          />
        )}
      </AnimatePresence>

      {/* top right: Historial */}
      <AnimatePresence>
        {!isHistoryExpanded && (
          <PanelBubble
            icon={<HistoryIcon />}
            label="Historial"
            shortcut="⌘4"
            isExpanded={isHistoryExpanded}
            onClick={() => handleBubbleClick('history')}
            onMouseEnter={() => handleBubbleHover('history')}
            onMouseLeave={handleBubbleLeave}
            position="top-right"
          />
        )}
      </AnimatePresence>

      {/* bottom right: Agente */}
      <AnimatePresence>
        {!isAgentExpanded && (
          <PanelBubble
            icon={<ChatIcon />}
            label="Agente"
            shortcut="⌘3"
            isExpanded={isAgentExpanded}
            onClick={() => handleBubbleClick('agent')}
            onMouseEnter={() => handleBubbleHover('agent')}
            onMouseLeave={handleBubbleLeave}
            position="bottom-right"
          />
        )}
      </AnimatePresence>

      {/* Expanded panels con hover handlers */}
      <AnimatePresence>
        {isListExpanded && (
          <div
            onMouseEnter={handlePanelEnter}
            onMouseLeave={() => handlePanelLeave('list')}
          >
            <ListPanel />
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isHistoryExpanded && (
          <div
            onMouseEnter={handlePanelEnter}
            onMouseLeave={() => handlePanelLeave('history')}
          >
            <HistoryPanel />
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isAgentExpanded && (
          <div
            onMouseEnter={handlePanelEnter}
            onMouseLeave={() => handlePanelLeave('agent')}
          >
            <AgentPanel />
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isNewExpanded && (
          <div
            onMouseEnter={handlePanelEnter}
            onMouseLeave={() => handlePanelLeave('new')}
          >
            <NewPanel />
          </div>
        )}
      </AnimatePresence>
    </>
  )
}
