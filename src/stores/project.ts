import { create } from 'zustand'
import { Node, Edge } from 'reactflow'

export interface HistoryEntry {
  timestamp: string
  prompt: string | null // null si fue edición manual
  title: string // título auto-generado o del prompt
  mermaidCode: string
  nodes: Node[]
  edges: Edge[]
  named: string | false // false o nombre del snapshot
}

export interface ProjectState {
  name: string
  currentNodes: Node[]
  currentEdges: Edge[]
  currentMermaidCode: string
  history: HistoryEntry[]
  historyIndex: number // para undo/redo
  legend: Record<string, { shape: string; color: string; description: string }>

  // Actions
  setName: (name: string) => void
  setDiagram: (nodes: Node[], edges: Edge[], mermaidCode: string, prompt?: string | null, title?: string) => void
  updateNodes: (nodes: Node[]) => void
  updateEdges: (edges: Edge[]) => void
  createSnapshot: (name: string) => void
  restoreSnapshot: (index: number) => void
  undo: () => void
  redo: () => void
  canUndo: () => boolean
  canRedo: () => boolean
  duplicateNode: (nodeId: string) => void
  exportProject: () => string
  importProject: (json: string) => void
  clearHistory: () => void
}

const defaultLegend = {
  etapa: { shape: 'chevron', color: '#FDF6F0', description: 'Etapa del proceso' },
  manual: { shape: 'rectangle', color: '#FDF6F0', description: 'Acción manual' },
  agente: { shape: 'hexagon', color: '#B5EAD7', description: 'Acción automatizada' },
  dolor: { shape: 'octagon', color: '#FFB5A7', description: 'Punto de dolor' },
  decision: { shape: 'diamond', color: '#FFF3B0', description: 'Decisión' },
}

// Genera un título corto a partir del prompt
function generateTitle(prompt: string | null): string {
  if (!prompt) return 'Edición manual'
  // Tomar las primeras palabras relevantes
  const words = prompt.split(' ').slice(0, 5).join(' ')
  return words.length > 30 ? words.substring(0, 30) + '...' : words
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  name: 'Nuevo Proyecto',
  currentNodes: [],
  currentEdges: [],
  currentMermaidCode: '',
  history: [],
  historyIndex: -1,
  legend: defaultLegend,

  setName: (name) => set({ name }),

  setDiagram: (nodes, edges, mermaidCode, prompt, title) => {
    const autoTitle = title || generateTitle(prompt ?? null)
    const entry: HistoryEntry = {
      timestamp: new Date().toISOString(),
      prompt: prompt ?? null,
      title: autoTitle,
      mermaidCode,
      nodes: JSON.parse(JSON.stringify(nodes)),
      edges: JSON.parse(JSON.stringify(edges)),
      named: false,
    }

    set((state) => {
      // Si estamos en medio del historial (después de undo), truncamos
      const newHistory = state.historyIndex < state.history.length - 1
        ? [...state.history.slice(0, state.historyIndex + 1), entry]
        : [...state.history, entry]

      return {
        currentNodes: nodes,
        currentEdges: edges,
        currentMermaidCode: mermaidCode,
        history: newHistory,
        historyIndex: newHistory.length - 1,
      }
    })
  },

  updateNodes: (nodes) => {
    set({ currentNodes: nodes })
  },

  updateEdges: (edges) => {
    set({ currentEdges: edges })
  },

  createSnapshot: (name) => {
    const state = get()
    const entry: HistoryEntry = {
      timestamp: new Date().toISOString(),
      prompt: null,
      title: name,
      mermaidCode: state.currentMermaidCode,
      nodes: JSON.parse(JSON.stringify(state.currentNodes)),
      edges: JSON.parse(JSON.stringify(state.currentEdges)),
      named: name,
    }

    set((state) => ({
      history: [...state.history, entry],
      historyIndex: state.history.length,
    }))
  },

  restoreSnapshot: (index) => {
    const state = get()
    const entry = state.history[index]
    if (entry) {
      set({
        currentNodes: JSON.parse(JSON.stringify(entry.nodes)),
        currentEdges: JSON.parse(JSON.stringify(entry.edges)),
        currentMermaidCode: entry.mermaidCode,
        historyIndex: index,
      })
    }
  },

  undo: () => {
    const state = get()
    if (state.historyIndex > 0) {
      const newIndex = state.historyIndex - 1
      const entry = state.history[newIndex]
      set({
        currentNodes: JSON.parse(JSON.stringify(entry.nodes)),
        currentEdges: JSON.parse(JSON.stringify(entry.edges)),
        currentMermaidCode: entry.mermaidCode,
        historyIndex: newIndex,
      })
    }
  },

  redo: () => {
    const state = get()
    if (state.historyIndex < state.history.length - 1) {
      const newIndex = state.historyIndex + 1
      const entry = state.history[newIndex]
      set({
        currentNodes: JSON.parse(JSON.stringify(entry.nodes)),
        currentEdges: JSON.parse(JSON.stringify(entry.edges)),
        currentMermaidCode: entry.mermaidCode,
        historyIndex: newIndex,
      })
    }
  },

  canUndo: () => {
    const state = get()
    return state.historyIndex > 0
  },

  canRedo: () => {
    const state = get()
    return state.historyIndex < state.history.length - 1
  },

  duplicateNode: (nodeId) => {
    const state = get()
    const nodeToDuplicate = state.currentNodes.find(n => n.id === nodeId)
    if (!nodeToDuplicate) return

    const newId = `node-${Date.now()}`
    const newNode: Node = {
      ...JSON.parse(JSON.stringify(nodeToDuplicate)),
      id: newId,
      position: {
        x: nodeToDuplicate.position.x + 50,
        y: nodeToDuplicate.position.y + 50,
      },
      selected: false,
    }

    set({
      currentNodes: [...state.currentNodes, newNode],
    })
  },

  exportProject: () => {
    const state = get()
    return JSON.stringify(
      {
        name: state.name,
        currentNodes: state.currentNodes,
        currentEdges: state.currentEdges,
        currentMermaidCode: state.currentMermaidCode,
        history: state.history,
        legend: state.legend,
        exportedAt: new Date().toISOString(),
        version: '1.1',
      },
      null,
      2
    )
  },

  importProject: (json) => {
    try {
      const data = JSON.parse(json)
      set({
        name: data.name || 'Proyecto Importado',
        currentNodes: data.currentNodes || [],
        currentEdges: data.currentEdges || [],
        currentMermaidCode: data.currentMermaidCode || '',
        history: data.history || [],
        historyIndex: (data.history?.length || 0) - 1,
        legend: data.legend || defaultLegend,
      })
    } catch (e) {
      console.error('Error importing project:', e)
    }
  },

  clearHistory: () => {
    set({ history: [], historyIndex: -1 })
  },
}))
