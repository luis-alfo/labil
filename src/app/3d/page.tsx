'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import Link from 'next/link'
import { palette, versions, type ColorPair } from '@/components/Three'

const STLViewer = dynamic(
  () => import('@/components/Three/STLViewer').then((m) => m.STLViewer),
  {
    ssr: false,
    loading: () => (
      <div className="h-full w-full flex items-center justify-center text-text-tertiary text-sm">
        Cargando modelo 3D…
      </div>
    ),
  }
)

const VersionThumbnail = dynamic(
  () => import('@/components/Three/VersionThumbnail').then((m) => m.VersionThumbnail),
  { ssr: false, loading: () => <div className="h-full w-full bg-surface-solid/40" /> }
)

const MODEL_URL = '/models/key.stl'

export default function ThreeDPage() {
  const [primary, setPrimary] = useState(versions[0].primary)
  const [secondary, setSecondary] = useState(versions[0].secondary)
  const [activeVersion, setActiveVersion] = useState<string | null>(versions[0].name)
  const [blendMode, setBlendMode] = useState<'gradient' | 'split'>('gradient')
  const [rotate, setRotate] = useState(false)

  const applyVersion = (v: ColorPair) => {
    setPrimary(v.primary)
    setSecondary(v.secondary)
    setActiveVersion(v.name)
  }

  return (
    <main className="min-h-screen w-full bg-bg text-text">
      {/* Top bar */}
      <header className="sticky top-0 z-30 flex items-center justify-between px-6 md:px-10 py-4 backdrop-blur-glass bg-bg/70 border-b border-border-subtle">
        <Link href="/" className="text-xl font-semibold" style={{ color: '#6BCB77' }}>
          labil
        </Link>
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span className="px-2 py-1 rounded-md bg-surface-solid/60">3D · key.stl</span>
        </div>
      </header>

      <div className="px-4 md:px-10 py-6 md:py-10 grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
        {/* Viewer */}
        <section className="relative">
          <div className="rounded-xl overflow-hidden bg-gradient-to-b from-surface-solid to-bg border border-border h-[60vh] lg:h-[78vh]">
            <STLViewer
              url={MODEL_URL}
              primary={primary}
              secondary={secondary}
              blendMode={blendMode}
              rotate={rotate}
            />
          </div>

          {/* Floating controls over the canvas */}
          <div className="absolute top-3 left-3 flex flex-wrap items-center gap-2 glass-panel rounded-md px-3 py-2">
            <span className="text-xs text-text-secondary mr-1">Modo</span>
            <button
              onClick={() => setBlendMode('gradient')}
              className={`text-xs px-2 py-1 rounded-sm transition ${
                blendMode === 'gradient'
                  ? 'bg-text text-bg'
                  : 'bg-surface-solid/60 hover:bg-surface-hover'
              }`}
            >
              Degradado
            </button>
            <button
              onClick={() => setBlendMode('split')}
              className={`text-xs px-2 py-1 rounded-sm transition ${
                blendMode === 'split'
                  ? 'bg-text text-bg'
                  : 'bg-surface-solid/60 hover:bg-surface-hover'
              }`}
            >
              Bicolor
            </button>
            <div className="w-px h-4 bg-border mx-1" />
            <button
              onClick={() => setRotate((r) => !r)}
              className={`text-xs px-2 py-1 rounded-sm transition ${
                rotate
                  ? 'bg-text text-bg'
                  : 'bg-surface-solid/60 hover:bg-surface-hover'
              }`}
              title="Auto-rotación"
            >
              {rotate ? 'Rotando' : 'Rotar'}
            </button>
          </div>

          {/* Active swatch indicator */}
          <div className="absolute bottom-3 left-3 glass-panel rounded-md px-3 py-2 flex items-center gap-2">
            <span className="text-xs text-text-secondary">
              {activeVersion ?? 'Personalizado'}
            </span>
            <div
              className="w-4 h-4 rounded-full border border-border"
              style={{ background: primary }}
              title="Primario"
            />
            <div
              className="w-4 h-4 rounded-full border border-border"
              style={{ background: secondary }}
              title="Secundario"
            />
          </div>
        </section>

        {/* Right panel: versions + custom pickers */}
        <aside className="space-y-6">
          <div>
            <h2 className="text-sm font-semibold mb-3">Versiones</h2>
            <div className="grid grid-cols-2 gap-3">
              {versions.map((v) => {
                const isActive = activeVersion === v.name
                return (
                  <button
                    key={v.name}
                    onClick={() => applyVersion(v)}
                    className={`group rounded-md border transition overflow-hidden text-left ${
                      isActive
                        ? 'border-accent ring-2 ring-accent/30'
                        : 'border-border hover:border-text-tertiary'
                    }`}
                  >
                    <div
                      className="h-24 w-full"
                      style={{
                        background: `linear-gradient(180deg, ${v.primary} 0%, ${v.secondary} 100%)`,
                      }}
                    >
                      <div className="h-full w-full opacity-90">
                        <VersionThumbnail
                          url={MODEL_URL}
                          primary={v.primary}
                          secondary={v.secondary}
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between px-2 py-1.5 bg-bg">
                      <span className="text-xs">{v.name}</span>
                      <div className="flex gap-1">
                        <span
                          className="w-3 h-3 rounded-full border border-border"
                          style={{ background: v.primary }}
                        />
                        <span
                          className="w-3 h-3 rounded-full border border-border"
                          style={{ background: v.secondary }}
                        />
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold mb-3">Personalizar</h2>
            <div className="space-y-3">
              <ColorRow
                label="Primario"
                value={primary}
                onChange={(c) => {
                  setPrimary(c)
                  setActiveVersion(null)
                }}
              />
              <ColorRow
                label="Secundario"
                value={secondary}
                onChange={(c) => {
                  setSecondary(c)
                  setActiveVersion(null)
                }}
              />
            </div>
          </div>
        </aside>
      </div>
    </main>
  )
}

function ColorRow({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (c: string) => void
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-text-secondary">{label}</span>
        <span className="text-xs font-mono text-text-tertiary">{value}</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {palette.map((p) => {
          const isActive = p.hex.toLowerCase() === value.toLowerCase()
          return (
            <button
              key={p.hex}
              onClick={() => onChange(p.hex)}
              title={p.name}
              className={`w-7 h-7 rounded-full border transition ${
                isActive
                  ? 'border-text scale-110'
                  : 'border-border hover:scale-105'
              }`}
              style={{ background: p.hex }}
            />
          )
        })}
        <label
          className="w-7 h-7 rounded-full border border-border bg-bg cursor-pointer flex items-center justify-center text-text-tertiary text-xs hover:border-text-secondary"
          title="Color personalizado"
        >
          +
          <input
            type="color"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="sr-only"
          />
        </label>
      </div>
    </div>
  )
}
