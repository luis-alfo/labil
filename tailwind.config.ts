import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Warm Clarity palette
        bg: '#FAFAFA',
        surface: '#F3F2EE',
        'surface-hover': 'rgba(243, 242, 238, 0.8)',
        border: 'rgba(232, 230, 225, 0.6)',
        'border-subtle': 'rgba(232, 230, 225, 0.3)',
        text: '#1A1919',
        'text-secondary': '#6B6966',
        'text-tertiary': '#9C9890',
        accent: '#8B5CF6',
        'accent-subtle': 'rgba(139, 92, 246, 0.08)',
        'accent-hover': 'rgba(139, 92, 246, 0.12)',
        pain: '#FECACA',
        'pain-border': '#DC2626',
        'pain-text': '#991B1B',
        success: '#BBF7D0',
        'success-border': '#16A34A',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      fontSize: {
        'xs': '11px',
        'sm': '13px',
        'base': '14px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
      },
      borderRadius: {
        'sm': '6px',
        'md': '10px',
        'lg': '16px',
        'xl': '24px',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
      backdropBlur: {
        'glass': '20px',
      },
    },
  },
  plugins: [],
}
export default config
