'use client'

import dynamic from 'next/dynamic'
import { Panels } from '@/components/Panels'
import { UserMenu } from '@/components/Auth'
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

      {/* Top bar: Logo centered + UserMenu right */}
      <div className="fixed top-4 left-0 right-0 z-30 flex items-center justify-between px-20 pointer-events-none">
        {/* Spacer for balance */}
        <div className="w-20" />

        {/* Logo centered */}
        <span className="text-xl font-semibold" style={{ color: '#6BCB77' }}>
          labil
        </span>

        {/* User menu - right aligned */}
        <div className="pointer-events-auto">
          <UserMenu />
        </div>
      </div>
    </main>
  )
}
