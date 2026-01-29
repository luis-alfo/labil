'use client'

import { memo, useState, useCallback } from 'react'
import { Handle, Position, NodeProps, useReactFlow } from 'reactflow'
import { NodeResizer } from '@reactflow/node-resizer'

export interface SwimlaneData {
  label: string
  color?: string
}

function SwimlaneNode({ id, data, selected }: NodeProps<SwimlaneData>) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(data.label)
  const { setNodes } = useReactFlow()

  const handleDoubleClick = useCallback(() => {
    setIsEditing(true)
    setEditValue(data.label)
  }, [data.label])

  const handleBlur = useCallback(() => {
    setIsEditing(false)
    setNodes((nodes) =>
      nodes.map((node) =>
        node.id === id
          ? { ...node, data: { ...node.data, label: editValue } }
          : node
      )
    )
  }, [id, editValue, setNodes])

  const bgColor = data.color || 'rgba(253, 246, 240, 0.3)'

  return (
    <>
      <NodeResizer
        minWidth={200}
        minHeight={100}
        isVisible={selected}
        lineClassName="border-muted"
        handleClassName="h-2 w-2 bg-muted rounded-full"
      />

      <div
        className={`
          w-full h-full min-w-[200px] min-h-[100px]
          border border-dashed border-muted/50
          rounded-lg
          ${selected ? 'border-primary/50' : ''}
        `}
        style={{ backgroundColor: bgColor }}
      >
        {/* Header del swimlane */}
        <div
          className="absolute left-0 top-0 px-3 py-1 bg-surface/80 rounded-tl-lg rounded-br-lg border-r border-b border-muted/30"
          onDoubleClick={handleDoubleClick}
        >
          {isEditing ? (
            <input
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={handleBlur}
              onKeyDown={(e) => e.key === 'Enter' && handleBlur()}
              autoFocus
              className="bg-transparent text-sm font-medium text-text outline-none w-24"
            />
          ) : (
            <span className="text-sm font-medium text-text">{data.label}</span>
          )}
        </div>
      </div>
    </>
  )
}

export default memo(SwimlaneNode)
