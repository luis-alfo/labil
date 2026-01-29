'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useDiagramStore } from '@/stores/diagram'
import { useProjectStore } from '@/stores/project'
import { useUIStore } from '@/stores/ui'
import { mermaidToReactFlow } from '@/lib/converters'

interface PendingPlan {
  plan: string[]
  mermaidCode: string
  title: string
}

export function AgentPanel() {
  const [input, setInput] = useState('')
  const [pendingPlan, setPendingPlan] = useState<PendingPlan | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { messages, mermaidCode, isLoading, error, addMessage, setMermaidCode, setLoading, setError } =
    useDiagramStore()
  const { setDiagram } = useProjectStore()
  const { expandedPanel, closeAllPanels, pinPanel } = useUIStore()

  const isExpanded = expandedPanel === 'agent'

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, pendingPlan])

  // Focus input when panel opens and pin it
  useEffect(() => {
    if (isExpanded) {
      setTimeout(() => inputRef.current?.focus(), 100)
      pinPanel('agent') // El panel del agente siempre se pinnea
    }
  }, [isExpanded, pinPanel])

  const applyChanges = (newMermaidCode: string, title: string, userMessage: string) => {
    setMermaidCode(newMermaidCode)
    try {
      const { nodes, edges } = mermaidToReactFlow(newMermaidCode)
      setDiagram(nodes, edges, newMermaidCode, userMessage, title)
    } catch (convertError) {
      console.error('Error converting Mermaid to ReactFlow:', convertError)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    addMessage('user', userMessage)
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          currentDiagram: mermaidCode,
          requestPlan: true,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error en la API')
      }

      // Mostrar el plan para confirmación
      if (data.plan && data.plan.length > 0) {
        setPendingPlan({
          plan: data.plan,
          mermaidCode: data.mermaidCode,
          title: data.title || userMessage.slice(0, 30),
        })
        addMessage('assistant', `📋 Plan propuesto:\n${data.plan.map((s: string, i: number) => `${i + 1}. ${s}`).join('\n')}\n\n¿Confirmas estos cambios?`)
      } else {
        // Si no hay plan, aplicar directamente (fallback)
        applyChanges(data.mermaidCode, data.title || userMessage.slice(0, 30), userMessage)
        addMessage('assistant', `✅ Diagrama actualizado`)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido'
      setError(errorMessage)
      addMessage('assistant', `❌ Error: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmPlan = () => {
    if (pendingPlan) {
      applyChanges(pendingPlan.mermaidCode, pendingPlan.title, pendingPlan.title)
      addMessage('assistant', `✅ Cambios aplicados: ${pendingPlan.title}`)
      setPendingPlan(null)
    }
  }

  const handleRejectPlan = () => {
    addMessage('assistant', '❌ Cambios cancelados. ¿Qué te gustaría hacer diferente?')
    setPendingPlan(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
    if (e.key === 'Escape') {
      closeAllPanels()
    }
  }

  if (!isExpanded) return null

  return (
    <motion.div
      initial={{ opacity: 0, x: 20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 20, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className="fixed bottom-4 right-4 z-50 w-96 h-[450px] glass-panel rounded-lg flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
            Agente
          </span>
        </div>
        <button
          onClick={closeAllPanels}
          className="text-text-tertiary hover:text-text transition-colors text-lg leading-none"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-text-tertiary text-sm space-y-2">
            <p>Hola! Soy tu asistente de diagramas. Puedo ayudarte a:</p>
            <ul className="list-disc list-inside text-xs space-y-1 ml-2">
              <li>Crear diagramas de flujo</li>
              <li>Añadir swimlanes y etapas</li>
              <li>Modificar nodos y conexiones</li>
              <li>Reorganizar el layout</li>
            </ul>
            <p className="text-xs italic mt-2">
              Te mostraré un plan antes de hacer cualquier cambio.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`text-sm ${
              msg.role === 'user'
                ? 'text-text bg-primary/5 rounded-md p-2 ml-8'
                : 'text-text-secondary bg-surface rounded-md p-2 mr-8 whitespace-pre-wrap'
            }`}
          >
            {msg.content}
          </div>
        ))}

        {/* Botones de confirmación del plan */}
        {pendingPlan && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2 mt-2"
          >
            <button
              onClick={handleConfirmPlan}
              className="flex-1 px-3 py-2 bg-green-500 text-white text-sm font-medium rounded-md hover:bg-green-600 transition-colors"
            >
              ✓ Confirmar
            </button>
            <button
              onClick={handleRejectPlan}
              className="flex-1 px-3 py-2 bg-red-100 text-red-600 text-sm font-medium rounded-md hover:bg-red-200 transition-colors"
            >
              ✗ Cancelar
            </button>
          </motion.div>
        )}

        {isLoading && (
          <div className="text-sm text-text-tertiary flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            Analizando tu solicitud...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-border-subtle">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={pendingPlan ? 'Escribe para modificar el plan...' : 'Describe qué quieres hacer...'}
          disabled={isLoading}
          rows={2}
          className="
            w-full px-3 py-2 rounded-md
            bg-white/80 border border-border
            text-sm text-text placeholder-text-tertiary
            resize-none
            focus:outline-none focus:border-accent
            transition-colors duration-100
            disabled:opacity-50
          "
        />
        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-text-tertiary">Enter para enviar</span>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="
              px-3 py-1 rounded-md
              bg-accent text-white text-sm font-medium
              hover:bg-accent/90
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors duration-100
            "
          >
            Enviar
          </button>
        </div>
      </form>
    </motion.div>
  )
}
