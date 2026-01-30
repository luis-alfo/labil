import { create } from 'zustand'
import { User, Session } from '@supabase/supabase-js'
import { getSupabase } from '@/lib/supabase'
import type { Profile } from '@/lib/supabase'

interface AuthState {
  user: User | null
  profile: Profile | null
  session: Session | null
  isLoading: boolean
  isLoginModalOpen: boolean

  // Actions
  setUser: (user: User | null) => void
  setProfile: (profile: Profile | null) => void
  setSession: (session: Session | null) => void
  setLoading: (loading: boolean) => void
  openLoginModal: () => void
  closeLoginModal: () => void

  // Auth actions
  signInWithEmail: (email: string, password: string) => Promise<{ error: string | null }>
  signUpWithEmail: (email: string, password: string, fullName?: string) => Promise<{ error: string | null }>
  signInWithMagicLink: (email: string) => Promise<{ error: string | null }>
  signInWithGoogle: () => Promise<{ error: string | null }>
  signOut: () => Promise<void>
  fetchProfile: () => Promise<void>
  initializeAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  profile: null,
  session: null,
  isLoading: true,
  isLoginModalOpen: false,

  setUser: (user) => set({ user }),
  setProfile: (profile) => set({ profile }),
  setSession: (session) => set({ session }),
  setLoading: (isLoading) => set({ isLoading }),
  openLoginModal: () => set({ isLoginModalOpen: true }),
  closeLoginModal: () => set({ isLoginModalOpen: false }),

  signInWithEmail: async (email, password) => {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) return { error: error.message }
    get().closeLoginModal()
    return { error: null }
  },

  signUpWithEmail: async (email, password, fullName) => {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName }
      }
    })
    if (error) return { error: error.message }
    return { error: null }
  },

  signInWithMagicLink: async (email) => {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) return { error: error.message }
    return { error: null }
  },

  signInWithGoogle: async () => {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) return { error: error.message }
    return { error: null }
  },

  signOut: async () => {
    const supabase = getSupabase()
    await supabase.auth.signOut()
    set({ user: null, profile: null, session: null })
  },

  fetchProfile: async () => {
    const { user } = get()
    if (!user) return

    const supabase = getSupabase()
    const { data } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (data) {
      set({ profile: data as Profile })
    }
  },

  initializeAuth: async () => {
    const supabase = getSupabase()

    // Get initial session
    const { data: { session } } = await supabase.auth.getSession()

    if (session) {
      set({ user: session.user, session })
      await get().fetchProfile()
    }

    set({ isLoading: false })

    // Listen for auth changes
    supabase.auth.onAuthStateChange(async (event, session) => {
      set({ user: session?.user ?? null, session })

      if (session?.user) {
        await get().fetchProfile()
      } else {
        set({ profile: null })
      }
    })
  }
}))
