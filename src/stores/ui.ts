import { create } from 'zustand'

export type PanelId = 'list' | 'new' | 'agent' | 'history'

interface UIState {
  // Panel states
  expandedPanel: PanelId | null
  pinnedPanels: Set<PanelId> // Panels que se mantienen abiertos (click o interacción prolongada)

  // Actions
  togglePanel: (panel: PanelId) => void
  closeAllPanels: () => void
  openPanel: (panel: PanelId) => void
  pinPanel: (panel: PanelId) => void
  unpinPanel: (panel: PanelId) => void
  isPinned: (panel: PanelId) => boolean
}

export const useUIStore = create<UIState>((set, get) => ({
  expandedPanel: null,
  pinnedPanels: new Set(),

  togglePanel: (panel) =>
    set((state) => {
      if (state.expandedPanel === panel) {
        // Si está abierto, cerrarlo y despinnearlo
        const newPinned = new Set(state.pinnedPanels)
        newPinned.delete(panel)
        return { expandedPanel: null, pinnedPanels: newPinned }
      }
      return { expandedPanel: panel }
    }),

  closeAllPanels: () => set({ expandedPanel: null }),

  openPanel: (panel) => set({ expandedPanel: panel }),

  pinPanel: (panel) =>
    set((state) => {
      const newPinned = new Set(state.pinnedPanels)
      newPinned.add(panel)
      return { pinnedPanels: newPinned }
    }),

  unpinPanel: (panel) =>
    set((state) => {
      const newPinned = new Set(state.pinnedPanels)
      newPinned.delete(panel)
      return { pinnedPanels: newPinned }
    }),

  isPinned: (panel) => get().pinnedPanels.has(panel),
}))
