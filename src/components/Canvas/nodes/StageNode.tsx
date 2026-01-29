'use client'

import { memo, useState, useCallback } from 'react'
import { NodeProps, useReactFlow } from 'reactflow'
import { NodeResizer } from '@reactflow/node-resizer'

export interface StageData {
  label: string
}

// Nodo para las etapas (chevrons en la parte superior del diagrama)
function StageNode({ id, data, selected }: NodeProps<StageData>) {
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

  return (
    <>
      <NodeResizer
        minWidth={120}
        minHeight={36}
        isVisible={selected}
        lineClassName="border-primary"
        handleClassName="h-2 w-2 bg-primary rounded-full"
      />

      <div
        className={`
          w-full h-full min-w-[120px] min-h-[36px]
          flex items-center justify-center
          bg-surface border border-muted
          transition-all
          ${selected ? 'shadow-md ring-2 ring-primary/30' : 'shadow-sm'}
        `}
        style={{
          clipPath: 'polygon(0% 0%, 90% 0%, 100% 50%, 90% 100%, 0% 100%, 10% 50%)',
        }}
        onDoubleClick={handleDoubleClick}
      >
        {isEditing ? (
          <input
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={handleBlur}
            onKeyDown={(e) => e.key === 'Enter' && handleBlur()}
            autoFocus
            className="bg-transparent text-center text-sm font-medium text-text outline-none w-full px-4"
          />
        ) : (
          <span className="text-sm font-medium text-text px-4">{data.label}</span>
        )}
      </div>
    </>
  )
}

export default memo(StageNode)
