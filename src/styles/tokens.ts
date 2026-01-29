// Labil Design Tokens — "Warm Clarity"

export const colors = {
  // Backgrounds
  bg: '#FAFAFA',
  bgElevated: 'rgba(255, 255, 254, 0.72)',
  bgCanvas: '#FFFFFF',

  // Surfaces (Soft Paper warmth)
  surface: 'rgba(243, 242, 238, 0.6)',
  surfaceHover: 'rgba(243, 242, 238, 0.8)',
  surfaceSolid: '#F3F2EE',

  // Borders
  border: 'rgba(232, 230, 225, 0.6)',
  borderSubtle: 'rgba(232, 230, 225, 0.3)',

  // Text
  text: '#1A1919',
  textSecondary: '#6B6966',
  textTertiary: '#9C9890',

  // Accent
  accent: '#8B5CF6',
  accentSubtle: 'rgba(139, 92, 246, 0.08)',
  accentHover: 'rgba(139, 92, 246, 0.12)',

  // Semantic
  pain: '#FECACA',
  painBorder: '#DC2626',
  painText: '#991B1B',
  success: '#BBF7D0',
  successBorder: '#16A34A',
} as const

export const glass = {
  background: 'rgba(255, 255, 254, 0.72)',
  blur: 'blur(20px) saturate(180%)',
  border: '1px solid rgba(255, 255, 255, 0.18)',
  shadow: '0 4px 24px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)',
} as const

export const motion = {
  fast: '100ms ease-out',
  default: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  smooth: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
  spring: '300ms cubic-bezier(0.175, 0.885, 0.32, 1.275)',
} as const

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
} as const

export const radius = {
  sm: '6px',
  md: '10px',
  lg: '16px',
  xl: '24px',
} as const
