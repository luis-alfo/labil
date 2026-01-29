'use client'

import { useCallback } from 'react'
import { useReactFlow } from 'reactflow'
import type { NodeShape } from './nodes'

interface ToolbarProps {
  selectedNodeId: string | null
  onAddNode: (shape: NodeShape) => void
}

const shapes: { shape: NodeShape; label: string; icon: string }[] = [
  { shape: 'rectangle', label: 'Rectángulo', icon: '▭' },
  { shape: 'diamond', label: 'Rombo', icon: '◇' },
  { shape: 'circle', label: 'Círculo', icon: '○' },
  { shape: 'hexagon', label: 'Hexágono', icon: '⬡' },
  { shape: 'chevron', label: 'Etapa', icon: '▷' },
  { shape: 'octagon', label: 'Octágono', icon: '⯃' },
]

const colors = [
  { name: 'Default', value: '#FDF6F0', border: '#E8DDD5' },
  { name: 'Coral', value: '#FFB5A7', border: '#F08080' },
  { name: 'Green', value: '#B5EAD7', border: '#7DC89E' },
  { name: 'Blue', value: '#A2D2FF', border: '#6BA3D6' },
  { name: 'Yellow', value: '#FFF3B0', border: '#E6D47A' },
  { name: 'Purple', value: '#E2BBE9', border: '#C490D1' },
]

export function Toolbar({ selectedNodeId, onAddNode }: ToolbarProps) {
  const { setNodes, deleteElements, getNode } = useReactFlow()

  const handleChangeShape = useCallback(
    (newShape: NodeShape) => {
      if (!selectedNodeId) return
      setNodes((nodes) =>
        nodes.map((node) =>
          node.id === selectedNodeId
            ? { ...node, data: { ...node.data, shape: newShape } }
            : node
        )
      )
    },
    [selectedNodeId, setNodes]
  )

  const handleChangeColor = useCallback(
    (color: string, borderColor: string) => {
      if (!selectedNodeId) return
      setNodes((nodes) =>
        nodes.map((node) =>
          node.id === selectedNodeId
            ? { ...node, data: { ...node.data, color, borderColor } }
            : node
        )
      )
    },
    [selectedNodeId, setNodes]
  )

  const handleDelete = useCallback(() => {
    if (!selectedNodeId) return
    const node = getNode(selectedNodeId)
    if (node) {
      deleteElements({ nodes: [node] })
    }
  }, [selectedNodeId, getNode, deleteElements])

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50" data-testid="toolbar">
      <div className="glass-panel px-3 py-2 flex items-center gap-4">
        {/* Añadir nodos */}
        <div className="flex items-center gap-1">
          <span className="text-xs text-muted mr-1">Añadir:</span>
          {shapes.slice(0, 4).map(({ shape, label, icon }) => (
            <button
              key={shape}
              onClick={() => onAddNode(shape)}
              title={label}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-surface/50 transition-colors text-lg"
            >
              {icon}
            </button>
          ))}
        </div>

        {/* Separador */}
        <div className="w-px h-6 bg-muted/30" />

        {/* Cambiar forma (solo si hay selección) */}
        {selectedNodeId && (
          <>
            <div className="flex items-center gap-1">
              <span className="text-xs text-muted mr-1">Forma:</span>
              {shapes.map(({ shape, label, icon }) => (
                <button
                  key={shape}
                  onClick={() => handleChangeShape(shape)}
                  title={label}
                  className="w-7 h-7 flex items-center justify-center rounded hover:bg-surface/50 transition-colors text-sm"
                >
                  {icon}
                </button>
              ))}
            </div>

            <div className="w-px h-6 bg-muted/30" />

            {/* Colores */}
            <div className="flex items-center gap-1">
              <span className="text-xs text-muted mr-1">Color:</span>
              {colors.map(({ name, value, border }) => (
                <button
                  key={name}
                  onClick={() => handleChangeColor(value, border)}
                  title={name}
                  className="w-5 h-5 rounded-full border-2 hover:scale-110 transition-transform"
                  style={{ backgroundColor: value, borderColor: border }}
                />
              ))}
            </div>

            <div className="w-px h-6 bg-muted/30" />

            {/* Eliminar */}
            <button
              onClick={handleDelete}
              className="px-2 py-1 text-xs text-error hover:bg-error/10 rounded transition-colors"
            >
              Eliminar
            </button>
          </>
        )}
      </div>
    </div>
  )
}
