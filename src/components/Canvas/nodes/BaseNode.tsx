'use client'

import { memo, useState, useCallback, useEffect, useRef } from 'react'
import { Handle, Position, NodeProps, useReactFlow } from 'reactflow'
import { NodeResizer } from '@reactflow/node-resizer'
import '@reactflow/node-resizer/dist/style.css'

export type NodeShape = 'rectangle' | 'diamond' | 'circle' | 'hexagon' | 'chevron' | 'octagon'

export interface BaseNodeData {
  label: string
  shape: NodeShape
  color?: string
  borderColor?: string
}

// SVG-based shapes for better rendering
function ShapeContainer({
  shape,
  bgColor,
  borderColor,
  selected,
  children,
  onDoubleClick,
}: {
  shape: NodeShape
  bgColor: string
  borderColor: string
  selected: boolean
  children: React.ReactNode
  onDoubleClick: () => void
}) {
  // Solo cambiar el stroke al seleccionar, sin cambios de color fuertes
  const strokeColor = borderColor
  const strokeWidth = selected ? 2.5 : 2

  const renderShape = () => {
    switch (shape) {
      case 'diamond':
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <polygon
              points="60,5 115,40 60,75 5,40"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
      case 'hexagon':
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <polygon
              points="30,5 90,5 115,40 90,75 30,75 5,40"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
      case 'chevron':
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <polygon
              points="5,5 95,5 115,40 95,75 5,75 25,40"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
      case 'octagon':
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <polygon
              points="35,5 85,5 115,25 115,55 85,75 35,75 5,55 5,25"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
      case 'circle':
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <ellipse
              cx="60"
              cy="40"
              rx="55"
              ry="35"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
      case 'rectangle':
      default:
        return (
          <svg viewBox="0 0 120 80" className="w-full h-full absolute inset-0" preserveAspectRatio="none">
            <rect
              x="5"
              y="5"
              width="110"
              height="70"
              rx="8"
              fill={bgColor}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
            />
          </svg>
        )
    }
  }

  return (
    <div
      className="relative w-full h-full flex items-center justify-center"
      onDoubleClick={onDoubleClick}
    >
      {renderShape()}
      <div className="relative z-10 px-3 py-2 w-full h-full flex items-center justify-center">
        {children}
      </div>
    </div>
  )
}

function BaseNode({ id, data, selected }: NodeProps<BaseNodeData>) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(data.label)
  const { setNodes } = useReactFlow()
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const labelRef = useRef(data.label)

  // Update editValue when data.label changes externally (NOT during editing)
  useEffect(() => {
    if (!isEditing) {
      setEditValue(data.label)
      labelRef.current = data.label
    }
  }, [data.label, isEditing])

  const handleDoubleClick = useCallback(() => {
    setIsEditing(true)
    setEditValue(labelRef.current)
  }, [])

  const commitLabel = useCallback((value: string) => {
    setIsEditing(false)
    labelRef.current = value
    setNodes((nodes) =>
      nodes.map((node) =>
        node.id === id
          ? { ...node, data: { ...node.data, label: value } }
          : node
      )
    )
  }, [id, setNodes])

  const handleBlur = useCallback(() => {
    commitLabel(editValue)
  }, [editValue, commitLabel])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Shift+Enter for new line, Enter alone to confirm
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        commitLabel(editValue)
      }
      if (e.key === 'Escape') {
        setIsEditing(false)
        setEditValue(labelRef.current)
      }
      // Stop propagation to prevent shortcuts from firing
      e.stopPropagation()
    },
    [editValue, commitLabel]
  )

  // Focus textarea when editing starts (only on mount)
  useEffect(() => {
    if (textareaRef.current && isEditing) {
      textareaRef.current.focus()
      textareaRef.current.select()
    }
  }, [isEditing])

  const bgColor = data.color || '#FDF6F0'
  const borderColor = data.borderColor || '#E8DDD5'

  return (
    <>
      <NodeResizer
        minWidth={80}
        minHeight={50}
        isVisible={selected}
        lineClassName="!border-transparent"
        handleClassName="!h-2.5 !w-2.5 !bg-muted/60 !rounded-full !border !border-muted"
      />

      {/* Handles with unique IDs for all 4 positions */}
      <Handle
        type="target"
        position={Position.Top}
        id="top"
        className="!w-2 !h-2 !bg-muted !border-0"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        className="!w-2 !h-2 !bg-muted !border-0"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        className="!w-2 !h-2 !bg-muted !border-0"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        className="!w-2 !h-2 !bg-muted !border-0"
      />
      {/* Also allow source from top/left and target from bottom/right for flexibility */}
      <Handle
        type="source"
        position={Position.Top}
        id="top-source"
        className="!w-2 !h-2 !bg-muted !border-0 !opacity-0"
      />
      <Handle
        type="source"
        position={Position.Left}
        id="left-source"
        className="!w-2 !h-2 !bg-muted !border-0 !opacity-0"
      />
      <Handle
        type="target"
        position={Position.Bottom}
        id="bottom-target"
        className="!w-2 !h-2 !bg-muted !border-0 !opacity-0"
      />
      <Handle
        type="target"
        position={Position.Right}
        id="right-target"
        className="!w-2 !h-2 !bg-muted !border-0 !opacity-0"
      />

      <ShapeContainer
        shape={data.shape}
        bgColor={bgColor}
        borderColor={borderColor}
        selected={!!selected}
        onDoubleClick={handleDoubleClick}
      >
        {isEditing ? (
          <textarea
            ref={textareaRef}
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            className="bg-transparent text-center text-sm text-text resize-none outline-none w-full min-h-[1.5em] overflow-hidden"
            style={{ lineHeight: '1.4' }}
            placeholder="Texto..."
          />
        ) : (
          <span
            className="text-sm text-text text-center block whitespace-pre-wrap break-words"
            style={{ lineHeight: '1.4' }}
          >
            {data.label || 'Doble clic para editar'}
          </span>
        )}
      </ShapeContainer>
    </>
  )
}

export default memo(BaseNode)
