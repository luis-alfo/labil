'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/stores/auth'

export function UserMenu() {
  const { user, profile, signOut, openLoginModal, isLoading } = useAuthStore()
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (isLoading) {
    return (
      <div className="w-9 h-9 rounded-full bg-surface animate-pulse" />
    )
  }

  if (!user) {
    return (
      <button
        onClick={openLoginModal}
        className="px-4 py-2 rounded-lg text-sm font-medium bg-text text-bg hover:bg-text/90 transition-colors"
      >
        Entrar
      </button>
    )
  }

  const initials = profile?.full_name
    ? profile.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user.email?.[0]?.toUpperCase() || '?'

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-9 h-9 rounded-full bg-accent text-white flex items-center justify-center text-sm font-medium hover:scale-105 transition-transform"
      >
        {profile?.avatar_url ? (
          <img src={profile.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
        ) : (
          initials
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full right-0 mt-2 w-56 glass-panel rounded-xl overflow-hidden"
          >
            {/* User info */}
            <div className="px-4 py-3 border-b border-border-subtle">
              <p className="text-sm font-medium truncate">{profile?.full_name || 'Usuario'}</p>
              <p className="text-xs text-text-secondary truncate">{user.email}</p>
            </div>

            {/* Energy balance */}
            <div className="px-4 py-3 border-b border-border-subtle">
              <div className="flex items-center justify-between">
                <span className="text-xs text-text-secondary">Julios disponibles</span>
                <span className="text-sm font-semibold" style={{ color: '#6BCB77' }}>
                  {profile?.energy_balance ?? 100}J
                </span>
              </div>
              <div className="mt-2 h-1.5 bg-surface-solid rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, ((profile?.energy_balance ?? 100) / 100) * 100)}%`,
                    backgroundColor: '#6BCB77'
                  }}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="p-2">
              <button
                onClick={() => { signOut(); setIsOpen(false) }}
                className="w-full px-3 py-2 rounded-md text-left text-sm text-text-secondary hover:text-text hover:bg-white/50 transition-colors"
              >
                Cerrar sesión
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
