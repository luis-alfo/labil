import { getSupabase } from './client'
import type { Diagram, Project } from './types'
import type { Node, Edge } from 'reactflow'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SupabaseResponse<T> = { data: T; error: any }

// ============== PROJECTS ==============

export async function getUserProjects(userId: string): Promise<Project[]> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function createProject(userId: string, name: string = 'Nuevo Proyecto'): Promise<Project> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('projects')
    .insert({ user_id: userId, name })
    .select()
    .single()

  if (error) throw error
  return data
}

export async function updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('projects')
    .update(updates)
    .eq('id', projectId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteProject(projectId: string): Promise<void> {
  const supabase = getSupabase()
  const { error } = await supabase
    .from('projects')
    .delete()
    .eq('id', projectId)

  if (error) throw error
}

// ============== DIAGRAMS ==============

export async function getProjectDiagrams(projectId: string): Promise<Diagram[]> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .select('*')
    .eq('project_id', projectId)
    .order('updated_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getUserDiagrams(userId: string): Promise<Diagram[]> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getDiagram(diagramId: string): Promise<Diagram | null> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .select('*')
    .eq('id', diagramId)
    .single()

  if (error) {
    if (error.code === 'PGRST116') return null // Not found
    throw error
  }
  return data
}

export async function createDiagram(
  projectId: string,
  userId: string,
  name: string = 'Nuevo Diagrama',
  nodes: Node[] = [],
  edges: Edge[] = []
): Promise<Diagram> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .insert({
      project_id: projectId,
      user_id: userId,
      name,
      nodes: nodes as unknown as object,
      edges: edges as unknown as object
    })
    .select()
    .single()

  if (error) throw error
  return data
}

export async function saveDiagram(
  diagramId: string,
  nodes: Node[],
  edges: Edge[],
  mermaidCode?: string,
  aiPrompt?: string
): Promise<Diagram> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .update({
      nodes: nodes as unknown as object,
      edges: edges as unknown as object,
      mermaid_code: mermaidCode,
      ai_prompt: aiPrompt
    })
    .eq('id', diagramId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function updateDiagramName(diagramId: string, name: string): Promise<Diagram> {
  const supabase = getSupabase()
  const { data, error } = await supabase
    .from('diagrams')
    .update({ name })
    .eq('id', diagramId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteDiagram(diagramId: string): Promise<void> {
  const supabase = getSupabase()
  const { error } = await supabase
    .from('diagrams')
    .delete()
    .eq('id', diagramId)

  if (error) throw error
}

// ============== VIEWPORT ==============

export async function saveViewport(
  diagramId: string,
  viewport: { x: number; y: number; zoom: number }
): Promise<void> {
  const supabase = getSupabase()
  const { error } = await supabase
    .from('diagrams')
    .update({ viewport: viewport as unknown as object })
    .eq('id', diagramId)

  if (error) throw error
}
