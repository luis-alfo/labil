'use client'

import { motion } from 'framer-motion'

interface PanelBubbleProps {
  icon: React.ReactNode
  label: string
  shortcut: string
  isExpanded: boolean
  onClick: () => void
  onMouseEnter?: () => void
  onMouseLeave?: () => void
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'bottom-left-offset'
}

const positionClasses = {
  'top-left': 'top-4 left-4',
  'top-right': 'top-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left-offset': 'bottom-4 left-16', // Offset para no solaparse con controles del canvas
}

export function PanelBubble({
  icon,
  label,
  shortcut,
  isExpanded,
  onClick,
  onMouseEnter,
  onMouseLeave,
  position,
}: PanelBubbleProps) {
  if (isExpanded) return null

  return (
    <motion.button
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ duration: 0.15, ease: [0.175, 0.885, 0.32, 1.275] }}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={`
        fixed ${positionClasses[position]} z-40
        w-12 h-12 rounded-full
        glass-panel
        flex items-center justify-center
        text-text-secondary hover:text-text
        hover:scale-110
        transition-transform duration-100 ease-out
        group
      `}
      title={`${label} (${shortcut})`}
    >
      {icon}

      {/* Tooltip */}
      <div
        className={`
          absolute ${position.includes('right') ? 'right-14' : 'left-14'}
          px-2 py-1 rounded-md
          bg-text text-bg text-xs font-medium
          opacity-0 group-hover:opacity-100
          transition-opacity duration-100
          whitespace-nowrap
          pointer-events-none
        `}
      >
        {label}
        <span className="ml-2 opacity-60">{shortcut}</span>
      </div>
    </motion.button>
  )
}
