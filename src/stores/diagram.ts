import { create } from 'zustand'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface DiagramState {
  // Current diagram
  mermaidCode: string
  diagramType: 'flowchart' | 'erDiagram' | 'sequenceDiagram' | 'stateDiagram'

  // Chat history
  messages: Message[]

  // UI state
  isLoading: boolean
  error: string | null

  // Actions
  setMermaidCode: (code: string) => void
  setDiagramType: (type: DiagramState['diagramType']) => void
  addMessage: (role: 'user' | 'assistant', content: string) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const DEFAULT_MERMAID = `flowchart LR
  subgraph Cliente
    A[Solicita acceso] --> B[Confirma email]
  end

  subgraph Sistema
    C{{Valida datos}} --> D[Envía notificación]
  end

  A --> C
  D --> B`

export const useDiagramStore = create<DiagramState>((set) => ({
  mermaidCode: DEFAULT_MERMAID,
  diagramType: 'flowchart',
  messages: [],
  isLoading: false,
  error: null,

  setMermaidCode: (code) => set({ mermaidCode: code, error: null }),

  setDiagramType: (type) => set({ diagramType: type }),

  addMessage: (role, content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: `msg-${Date.now()}`,
          role,
          content,
          timestamp: Date.now(),
        },
      ],
    })),

  clearMessages: () => set({ messages: [] }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      mermaidCode: DEFAULT_MERMAID,
      diagramType: 'flowchart',
      messages: [],
      isLoading: false,
      error: null,
    }),
}))
