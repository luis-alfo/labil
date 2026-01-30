export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          email: string
          full_name: string | null
          avatar_url: string | null
          energy_balance: number
          plan: 'free' | 'pro' | 'team'
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          energy_balance?: number
          plan?: 'free' | 'pro' | 'team'
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          energy_balance?: number
          plan?: 'free' | 'pro' | 'team'
          created_at?: string
          updated_at?: string
        }
      }
      projects: {
        Row: {
          id: string
          user_id: string
          name: string
          description: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name?: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      diagrams: {
        Row: {
          id: string
          project_id: string
          user_id: string
          name: string
          nodes: Json
          edges: Json
          viewport: Json
          mermaid_code: string | null
          ai_prompt: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          project_id: string
          user_id: string
          name?: string
          nodes?: Json
          edges?: Json
          viewport?: Json
          mermaid_code?: string | null
          ai_prompt?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          project_id?: string
          user_id?: string
          name?: string
          nodes?: Json
          edges?: Json
          viewport?: Json
          mermaid_code?: string | null
          ai_prompt?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      energy_log: {
        Row: {
          id: string
          user_id: string
          diagram_id: string | null
          action: string
          julios_spent: number
          tokens_used: number | null
          model: string | null
          prompt_preview: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          diagram_id?: string | null
          action: string
          julios_spent: number
          tokens_used?: number | null
          model?: string | null
          prompt_preview?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          diagram_id?: string | null
          action?: string
          julios_spent?: number
          tokens_used?: number | null
          model?: string | null
          prompt_preview?: string | null
          created_at?: string
        }
      }
    }
  }
}

export type Profile = Database['public']['Tables']['profiles']['Row']
export type Project = Database['public']['Tables']['projects']['Row']
export type Diagram = Database['public']['Tables']['diagrams']['Row']
export type EnergyLog = Database['public']['Tables']['energy_log']['Row']
