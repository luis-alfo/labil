'use client'

import { useEffect, useRef, useState } from 'react'

interface MermaidRendererProps {
  chart: string
  className?: string
}

export function MermaidRenderer({ chart, className = '' }: MermaidRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [isReady, setIsReady] = useState(false)

  // Initialize mermaid only on client side
  useEffect(() => {
    const initMermaid = async () => {
      console.log('Initializing mermaid...')
      const mermaid = (await import('mermaid')).default

      mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        themeVariables: {
          primaryColor: '#F3F2EE',
          primaryTextColor: '#1A1919',
          primaryBorderColor: '#E8E6E1',
          lineColor: '#9C9890',
          secondaryColor: 'rgba(139, 92, 246, 0.08)',
          tertiaryColor: '#FAFAFA',
          fontFamily: 'Plus Jakarta Sans, -apple-system, sans-serif',
          fontSize: '13px',
          nodeBorder: '#E8E6E1',
          clusterBkg: 'rgba(243, 242, 238, 0.4)',
          clusterBorder: 'rgba(232, 230, 225, 0.6)',
          noteBkgColor: '#F3F2EE',
          noteTextColor: '#6B6966',
        },
        flowchart: {
          htmlLabels: true,
          curve: 'basis',
          nodeSpacing: 50,
          rankSpacing: 50,
          padding: 15,
        },
      })

      console.log('Mermaid ready!')
      setIsReady(true)
    }

    initMermaid().catch(err => console.error('Mermaid init error:', err))
  }, [])

  // Render chart when mermaid is ready and chart changes
  useEffect(() => {
    const renderChart = async () => {
      console.log('Render attempt - isReady:', isReady, 'chart:', chart?.substring(0, 50))
      if (!chart || !isReady) return

      try {
        setError(null)
        const mermaid = (await import('mermaid')).default
        const id = `mermaid-${Date.now()}`
        console.log('Rendering with id:', id)
        const { svg } = await mermaid.render(id, chart)
        console.log('SVG generated, length:', svg?.length)
        setSvg(svg)
      } catch (err) {
        console.error('Mermaid render error:', err)
        setError(err instanceof Error ? err.message : 'Error rendering diagram')
      }
    }

    renderChart()
  }, [chart, isReady])

  if (error) {
    return (
      <div className={`p-4 rounded-md bg-[#FECACA]/50 border border-[#DC2626] text-[#991B1B] text-sm ${className}`}>
        <p className="font-medium mb-1">Error en el diagrama</p>
        <p className="text-xs opacity-80">{error}</p>
      </div>
    )
  }

  if (!svg) {
    return (
      <div className={`flex items-center justify-center p-8 text-[#9C9890] text-sm ${className}`}>
        Generando diagrama...
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={`mermaid-container ${className}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}
