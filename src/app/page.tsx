'use client'

import dynamic from 'next/dynamic'
import { Panels } from '@/components/Panels'
import { useProjectStore } from '@/stores/project'

// Dynamic import to avoid SSR issues with ReactFlow
const FlowCanvas = dynamic(
  () => import('@/components/Canvas/FlowCanvas').then((mod) => mod.FlowCanvas),
  { ssr: false, loading: () => <div className="h-full w-full bg-bg" /> }
)

export default function Home() {
  const { name } = useProjectStore()

  return (
    <main className="h-screen w-screen overflow-hidden bg-bg">
      {/* Canvas area */}
      <div className="h-full w-full">
        <FlowCanvas />
      </div>

      {/* Floating panels */}
      <Panels />

      {/* Logo/title */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-30 pointer-events-none">
        <h1 className="text-lg font-semibold text-text tracking-tight opacity-50">{name}</h1>
      </div>
    </main>
  )
}
