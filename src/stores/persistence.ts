import { create } from 'zustand'
import type { Node, Edge } from 'reactflow'
import type { Project, Diagram } from '@/lib/supabase'
import {
  getUserProjects,
  createProject,
  updateProject,
  deleteProject as deleteProjectApi,
  getUserDiagrams,
  getDiagram,
  createDiagram,
  saveDiagram as saveDiagramApi,
  updateDiagramName,
  deleteDiagram as deleteDiagramApi,
  saveViewport
} from '@/lib/supabase/diagrams'

interface PersistenceState {
  // Data
  projects: Project[]
  diagrams: Diagram[]
  currentProjectId: string | null
  currentDiagramId: string | null

  // UI state
  isLoadingProjects: boolean
  isLoadingDiagrams: boolean
  isSaving: boolean
  lastSaved: Date | null
  hasUnsavedChanges: boolean

  // Actions - Projects
  loadProjects: (userId: string) => Promise<void>
  createNewProject: (userId: string, name?: string) => Promise<Project>
  renameProject: (projectId: string, name: string) => Promise<void>
  deleteProject: (projectId: string) => Promise<void>

  // Actions - Diagrams
  loadDiagrams: (userId: string) => Promise<void>
  loadDiagram: (diagramId: string) => Promise<Diagram | null>
  createNewDiagram: (projectId: string, userId: string, name?: string) => Promise<Diagram>
  saveDiagram: (diagramId: string, nodes: Node[], edges: Edge[], mermaidCode?: string, aiPrompt?: string) => Promise<void>
  renameDiagram: (diagramId: string, name: string) => Promise<void>
  deleteDiagram: (diagramId: string) => Promise<void>
  saveCurrentViewport: (diagramId: string, viewport: { x: number; y: number; zoom: number }) => Promise<void>

  // State management
  setCurrentProject: (projectId: string | null) => void
  setCurrentDiagram: (diagramId: string | null) => void
  setHasUnsavedChanges: (value: boolean) => void
}

export const usePersistenceStore = create<PersistenceState>((set, get) => ({
  projects: [],
  diagrams: [],
  currentProjectId: null,
  currentDiagramId: null,
  isLoadingProjects: false,
  isLoadingDiagrams: false,
  isSaving: false,
  lastSaved: null,
  hasUnsavedChanges: false,

  // Projects
  loadProjects: async (userId) => {
    set({ isLoadingProjects: true })
    try {
      const projects = await getUserProjects(userId)
      set({ projects })
    } catch (error) {
      console.error('Error loading projects:', error)
    } finally {
      set({ isLoadingProjects: false })
    }
  },

  createNewProject: async (userId, name = 'Nuevo Proyecto') => {
    const project = await createProject(userId, name)
    set((state) => ({ projects: [project, ...state.projects] }))
    return project
  },

  renameProject: async (projectId, name) => {
    await updateProject(projectId, { name })
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId ? { ...p, name } : p
      )
    }))
  },

  deleteProject: async (projectId) => {
    await deleteProjectApi(projectId)
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== projectId),
      diagrams: state.diagrams.filter((d) => d.project_id !== projectId),
      currentProjectId: state.currentProjectId === projectId ? null : state.currentProjectId
    }))
  },

  // Diagrams
  loadDiagrams: async (userId) => {
    set({ isLoadingDiagrams: true })
    try {
      const diagrams = await getUserDiagrams(userId)
      set({ diagrams })
    } catch (error) {
      console.error('Error loading diagrams:', error)
    } finally {
      set({ isLoadingDiagrams: false })
    }
  },

  loadDiagram: async (diagramId) => {
    try {
      return await getDiagram(diagramId)
    } catch (error) {
      console.error('Error loading diagram:', error)
      return null
    }
  },

  createNewDiagram: async (projectId, userId, name = 'Nuevo Diagrama') => {
    const diagram = await createDiagram(projectId, userId, name)
    set((state) => ({ diagrams: [diagram, ...state.diagrams] }))
    return diagram
  },

  saveDiagram: async (diagramId, nodes, edges, mermaidCode, aiPrompt) => {
    set({ isSaving: true })
    try {
      const updated = await saveDiagramApi(diagramId, nodes, edges, mermaidCode, aiPrompt)
      set((state) => ({
        diagrams: state.diagrams.map((d) =>
          d.id === diagramId ? updated : d
        ),
        lastSaved: new Date(),
        hasUnsavedChanges: false
      }))
    } catch (error) {
      console.error('Error saving diagram:', error)
      throw error
    } finally {
      set({ isSaving: false })
    }
  },

  renameDiagram: async (diagramId, name) => {
    const updated = await updateDiagramName(diagramId, name)
    set((state) => ({
      diagrams: state.diagrams.map((d) =>
        d.id === diagramId ? updated : d
      )
    }))
  },

  deleteDiagram: async (diagramId) => {
    await deleteDiagramApi(diagramId)
    set((state) => ({
      diagrams: state.diagrams.filter((d) => d.id !== diagramId),
      currentDiagramId: state.currentDiagramId === diagramId ? null : state.currentDiagramId
    }))
  },

  saveCurrentViewport: async (diagramId, viewport) => {
    try {
      await saveViewport(diagramId, viewport)
    } catch (error) {
      console.error('Error saving viewport:', error)
    }
  },

  // State
  setCurrentProject: (projectId) => set({ currentProjectId: projectId }),
  setCurrentDiagram: (diagramId) => set({ currentDiagramId: diagramId }),
  setHasUnsavedChanges: (hasUnsavedChanges) => set({ hasUnsavedChanges })
}))
