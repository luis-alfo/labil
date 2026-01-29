'use client'

import { useCallback, useState, useRef, useEffect } from 'react'
import ReactFlow, {
  Background,
  MiniMap,
  Controls,
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  useReactFlow,
  NodeChange,
  NodePositionChange,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'

import BaseNode from './nodes/BaseNode'
import SwimlaneNode from './nodes/SwimlaneNode'
import StageNode from './nodes/StageNode'
import { useProjectStore } from '@/stores/project'
import type { NodeShape, BaseNodeData } from './nodes'

const nodeTypes = {
  base: BaseNode,
  swimlane: SwimlaneNode,
  stage: StageNode,
}

const defaultEdgeOptions = {
  type: 'smoothstep',
  animated: false,
  style: { stroke: '#6B5B4F', strokeWidth: 2 },
  deletable: true,
}

// Nodos iniciales de ejemplo
const defaultNodes: Node[] = [
  {
    id: '1',
    type: 'base',
    position: { x: 100, y: 100 },
    data: { label: 'Inicio', shape: 'circle' as NodeShape, color: '#B5EAD7', borderColor: '#7DC89E' },
  },
  {
    id: '2',
    type: 'base',
    position: { x: 300, y: 100 },
    data: { label: 'Proceso', shape: 'rectangle' as NodeShape },
  },
  {
    id: '3',
    type: 'base',
    position: { x: 500, y: 100 },
    data: { label: '¿Decisión?', shape: 'diamond' as NodeShape, color: '#FFF3B0', borderColor: '#E6D47A' },
  },
]

const defaultEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', sourceHandle: 'right', targetHandle: 'left' },
  { id: 'e2-3', source: '2', target: '3', sourceHandle: 'right', targetHandle: 'left' },
]

// Icons
const UndoIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 7v6h6M3 13c1.5-3.5 4.5-6 9-6 5.5 0 9 4 9 9s-4 9-9 9c-3 0-5.5-1.5-7-4" />
  </svg>
)

const RedoIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 7v6h-6M21 13c-1.5-3.5-4.5-6-9-6-5.5 0-9 4-9 9s4 9 9 9c3 0 5.5-1.5 7-4" />
  </svg>
)

const DuplicateIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="9" y="9" width="13" height="13" rx="2" />
    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
  </svg>
)

const PlusIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12h14" />
  </svg>
)

const MinusIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M5 12h14" />
  </svg>
)

const FitIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
  </svg>
)

// Shape icons as proper SVGs
const ShapeIcon = ({ shape }: { shape: NodeShape }) => {
  const className = "text-muted"
  switch (shape) {
    case 'rectangle':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <rect x="3" y="5" width="18" height="14" rx="2" />
        </svg>
      )
    case 'diamond':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <path d="M12 2l10 10-10 10L2 12z" />
        </svg>
      )
    case 'circle':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <circle cx="12" cy="12" r="9" />
        </svg>
      )
    case 'hexagon':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <path d="M12 2l8 4.5v9L12 22l-8-6.5v-9z" />
        </svg>
      )
    case 'chevron':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <path d="M4 4h12l4 8-4 8H4l4-8z" />
        </svg>
      )
    case 'octagon':
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
          <path d="M7.86 2h8.28L22 7.86v8.28L16.14 22H7.86L2 16.14V7.86z" />
        </svg>
      )
    default:
      return null
  }
}

const shapes: { shape: NodeShape; label: string }[] = [
  { shape: 'rectangle', label: 'Rectángulo' },
  { shape: 'diamond', label: 'Rombo' },
  { shape: 'circle', label: 'Círculo' },
  { shape: 'hexagon', label: 'Hexágono' },
  { shape: 'chevron', label: 'Etapa' },
  { shape: 'octagon', label: 'Punto dolor' },
]

function FlowCanvasInner() {
  const {
    currentNodes: storeNodes,
    currentEdges: storeEdges,
    updateNodes,
    updateEdges,
    setDiagram,
    history,
    historyIndex,
  } = useProjectStore()

  // Use store nodes if available, otherwise defaults
  const initialNodes = storeNodes.length > 0 ? storeNodes : defaultNodes
  const initialEdges = storeEdges.length > 0 ? storeEdges : defaultEdges

  const [nodes, setNodes, onNodesChangeInternal] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(initialEdges)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const nodeIdCounter = useRef(10)
  const { screenToFlowPosition, fitView, zoomIn, zoomOut } = useReactFlow()

  // Track if we're in the middle of a drag to avoid saving too often
  const isDraggingRef = useRef(false)
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Sync nodes/edges when store changes (from agent)
  useEffect(() => {
    if (storeNodes.length > 0) {
      setNodes(storeNodes)
      setEdges(storeEdges)
      setTimeout(() => fitView({ padding: 0.2 }), 100)
    }
  }, [storeNodes, storeEdges, setNodes, setEdges, fitView])

  // Save current state to history (debounced)
  const saveToHistory = useCallback(() => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    saveTimeoutRef.current = setTimeout(() => {
      // Get current nodes/edges from the refs
      setNodes((currentNodes) => {
        setEdges((currentEdges) => {
          // Only save if there are changes
          if (currentNodes.length > 0) {
            setDiagram(currentNodes, currentEdges, '', null, 'Edición manual')
          }
          return currentEdges
        })
        return currentNodes
      })
    }, 500)
  }, [setDiagram, setNodes, setEdges])

  // Undo/Redo functions that work with local state
  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      const entry = history[historyIndex - 1]
      if (entry) {
        setNodes(JSON.parse(JSON.stringify(entry.nodes)))
        setEdges(JSON.parse(JSON.stringify(entry.edges)))
        useProjectStore.setState({ historyIndex: historyIndex - 1 })
      }
    }
  }, [historyIndex, history, setNodes, setEdges])

  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const entry = history[historyIndex + 1]
      if (entry) {
        setNodes(JSON.parse(JSON.stringify(entry.nodes)))
        setEdges(JSON.parse(JSON.stringify(entry.edges)))
        useProjectStore.setState({ historyIndex: historyIndex + 1 })
      }
    }
  }, [historyIndex, history, setNodes, setEdges])

  const canUndo = historyIndex > 0
  const canRedo = historyIndex < history.length - 1

  // Duplicate node using local state
  const handleDuplicateNode = useCallback(() => {
    if (!selectedNodeId) return

    setNodes((currentNodes) => {
      const nodeToDuplicate = currentNodes.find(n => n.id === selectedNodeId)
      if (!nodeToDuplicate) return currentNodes

      const newId = `node-${Date.now()}`
      const newNode: Node = {
        ...JSON.parse(JSON.stringify(nodeToDuplicate)),
        id: newId,
        position: {
          x: nodeToDuplicate.position.x + 50,
          y: nodeToDuplicate.position.y + 50,
        },
        selected: false,
      }

      return [...currentNodes, newNode]
    })

    // Save after duplicate
    setTimeout(saveToHistory, 100)
  }, [selectedNodeId, setNodes, saveToHistory])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input/textarea
      if (document.activeElement?.tagName === 'INPUT' ||
          document.activeElement?.tagName === 'TEXTAREA') {
        return
      }

      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modKey = isMac ? e.metaKey : e.ctrlKey

      // Undo: Cmd/Ctrl + Z
      if (modKey && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        handleUndo()
      }

      // Redo: Cmd/Ctrl + Shift + Z o Cmd/Ctrl + Y
      if ((modKey && e.shiftKey && e.key === 'z') || (modKey && e.key === 'y')) {
        e.preventDefault()
        handleRedo()
      }

      // Duplicate: Cmd/Ctrl + D
      if (modKey && e.key === 'd' && selectedNodeId) {
        e.preventDefault()
        handleDuplicateNode()
      }

      // Delete: Backspace o Delete
      if ((e.key === 'Backspace' || e.key === 'Delete') && selectedNodeId) {
        e.preventDefault()
        setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId))
        setSelectedNodeId(null)
        saveToHistory()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedNodeId, handleUndo, handleRedo, handleDuplicateNode, setNodes, saveToHistory])

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge({ ...params, ...defaultEdgeOptions }, eds))
      saveToHistory()
    },
    [setEdges, saveToHistory]
  )

  const onSelectionChange = useCallback(
    ({ nodes: selectedNodes }: { nodes: Node[] }) => {
      setSelectedNodeId(selectedNodes.length === 1 ? selectedNodes[0].id : null)
    },
    []
  )

  const handleAddNode = useCallback(
    (shape: NodeShape) => {
      const id = `node-${nodeIdCounter.current++}`
      const position = screenToFlowPosition({ x: window.innerWidth / 2, y: window.innerHeight / 2 })

      const newNode: Node<BaseNodeData> = {
        id,
        type: 'base',
        position,
        data: {
          label: 'Nuevo',
          shape,
        },
      }

      setNodes((nds) => [...nds, newNode])
      saveToHistory()
    },
    [setNodes, screenToFlowPosition, saveToHistory]
  )

  const handleAddSwimlane = useCallback(() => {
    const id = `swimlane-${nodeIdCounter.current++}`
    const position = screenToFlowPosition({ x: window.innerWidth / 2 - 200, y: window.innerHeight / 2 - 100 })

    const newNode: Node = {
      id,
      type: 'swimlane',
      position,
      data: { label: 'Nuevo Swimlane' },
      style: { width: 400, height: 200 },
    }

    setNodes((nds) => [...nds, newNode])
    saveToHistory()
  }, [setNodes, screenToFlowPosition, saveToHistory])

  // Helper: check if a node is inside a swimlane
  const isNodeInsideSwimlane = useCallback((node: Node, swimlane: Node) => {
    const swimlaneBounds = {
      x: swimlane.position.x,
      y: swimlane.position.y,
      width: (swimlane.style?.width as number) || 400,
      height: (swimlane.style?.height as number) || 200,
    }
    return (
      node.position.x >= swimlaneBounds.x &&
      node.position.x <= swimlaneBounds.x + swimlaneBounds.width &&
      node.position.y >= swimlaneBounds.y &&
      node.position.y <= swimlaneBounds.y + swimlaneBounds.height
    )
  }, [])

  // Track previous swimlane positions for delta calculation
  const swimlanePositions = useRef<Map<string, { x: number; y: number }>>(new Map())

  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      // Check for drag start/end
      const positionChanges = changes.filter(c => c.type === 'position') as NodePositionChange[]
      const hasDragging = positionChanges.some(c => c.dragging)
      const hadDragging = isDraggingRef.current

      if (hasDragging) {
        isDraggingRef.current = true
      } else if (hadDragging && !hasDragging) {
        // Drag ended, save to history
        isDraggingRef.current = false
        saveToHistory()
      }

      // Find swimlane position changes
      const swimlaneChanges = changes.filter(
        (change): change is NodePositionChange =>
          change.type === 'position' &&
          'position' in change &&
          change.position !== undefined &&
          nodes.find((n) => n.id === change.id)?.type === 'swimlane'
      )

      if (swimlaneChanges.length > 0) {
        const additionalChanges: NodePositionChange[] = []

        for (const swimlaneChange of swimlaneChanges) {
          const swimlane = nodes.find((n) => n.id === swimlaneChange.id)
          if (!swimlane || !swimlaneChange.position) continue

          const prevPos = swimlanePositions.current.get(swimlaneChange.id) || swimlane.position
          const deltaX = swimlaneChange.position.x - prevPos.x
          const deltaY = swimlaneChange.position.y - prevPos.y

          swimlanePositions.current.set(swimlaneChange.id, { ...swimlaneChange.position })

          if (deltaX !== 0 || deltaY !== 0) {
            for (const node of nodes) {
              if (node.type !== 'swimlane' && isNodeInsideSwimlane(node, swimlane)) {
                const alreadyMoving = changes.some(
                  (c) => c.type === 'position' && c.id === node.id
                )
                if (!alreadyMoving) {
                  additionalChanges.push({
                    id: node.id,
                    type: 'position',
                    position: {
                      x: node.position.x + deltaX,
                      y: node.position.y + deltaY,
                    },
                    dragging: false,
                  })
                }
              }
            }
          }
        }

        onNodesChangeInternal([...changes, ...additionalChanges])
      } else {
        onNodesChangeInternal(changes)
      }
    },
    [onNodesChangeInternal, nodes, isNodeInsideSwimlane, saveToHistory]
  )

  const handleEdgesChange = useCallback(
    (changes: any) => {
      onEdgesChangeInternal(changes)
    },
    [onEdgesChangeInternal]
  )

  // Color palette for selected node
  const colors = [
    { name: 'Default', value: '#FDF6F0', border: '#E8DDD5' },
    { name: 'Coral', value: '#FFB5A7', border: '#F08080' },
    { name: 'Green', value: '#B5EAD7', border: '#7DC89E' },
    { name: 'Blue', value: '#A2D2FF', border: '#6BA3D6' },
    { name: 'Yellow', value: '#FFF3B0', border: '#E6D47A' },
    { name: 'Purple', value: '#E2BBE9', border: '#C490D1' },
  ]

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
      saveToHistory()
    },
    [selectedNodeId, setNodes, saveToHistory]
  )

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
      saveToHistory()
    },
    [selectedNodeId, setNodes, saveToHistory]
  )

  const handleDeleteNode = useCallback(() => {
    if (!selectedNodeId) return
    setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId))
    setSelectedNodeId(null)
    saveToHistory()
  }, [selectedNodeId, setNodes, saveToHistory])

  // Get selected node for floating toolbar position
  const selectedNode = nodes.find(n => n.id === selectedNodeId)

  return (
    <div className="w-full h-full relative" data-testid="canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        onSelectionChange={onSelectionChange}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        snapToGrid
        snapGrid={[16, 16]}
        className="bg-bg"
        proOptions={{ hideAttribution: true }}
        connectionMode="loose"
        deleteKeyCode={['Backspace', 'Delete']}
        selectionKeyCode={null}
        edgesFocusable={true}
        edgesUpdatable={true}
      >
        <Background color="#E8DDD5" gap={16} size={1} />

        {/* MiniMap oculto temporalmente */}

        {/* Bottom toolbar - Add nodes - centrado con margen para no solaparse */}
        <Panel position="bottom-center" className="mb-4 z-50">
          <div className="glass-panel px-3 py-1.5 flex items-center gap-1 rounded-xl">
            {shapes.map(({ shape, label }) => (
              <button
                key={shape}
                onClick={() => handleAddNode(shape)}
                title={label}
                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-surface/60 transition-colors"
              >
                <ShapeIcon shape={shape} />
              </button>
            ))}
            <div className="w-px h-5 bg-border/30 mx-0.5" />
            <button
              onClick={handleAddSwimlane}
              title="Swimlane"
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-surface/60 transition-colors"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-muted">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <line x1="3" y1="9" x2="21" y2="9" />
                <line x1="3" y1="15" x2="21" y2="15" />
              </svg>
            </button>
          </div>
        </Panel>

        {/* Bottom-left controls - vertical stack */}
        <Panel position="bottom-left" className="ml-4 mb-4">
          <div className="glass-panel rounded-xl p-1 flex flex-col gap-0.5">
            {/* Zoom Controls */}
            <button
              onClick={() => zoomIn()}
              className="p-1.5 rounded-lg hover:bg-surface/60 transition-colors text-muted hover:text-text"
              title="Acercar"
            >
              <PlusIcon />
            </button>
            <button
              onClick={() => zoomOut()}
              className="p-1.5 rounded-lg hover:bg-surface/60 transition-colors text-muted hover:text-text"
              title="Alejar"
            >
              <MinusIcon />
            </button>
            <button
              onClick={() => fitView({ padding: 0.2 })}
              className="p-1.5 rounded-lg hover:bg-surface/60 transition-colors text-muted hover:text-text"
              title="Centrar"
            >
              <FitIcon />
            </button>

            <div className="h-px w-full bg-border/30 my-0.5" />

            {/* Undo/Redo */}
            <button
              onClick={handleUndo}
              disabled={!canUndo}
              className="p-1.5 rounded-lg hover:bg-surface/60 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-muted hover:text-text"
              title="Deshacer (Cmd/Ctrl+Z)"
            >
              <UndoIcon />
            </button>
            <button
              onClick={handleRedo}
              disabled={!canRedo}
              className="p-1.5 rounded-lg hover:bg-surface/60 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-muted hover:text-text"
              title="Rehacer (Cmd/Ctrl+Shift+Z)"
            >
              <RedoIcon />
            </button>
            {selectedNodeId && (
              <button
                onClick={handleDuplicateNode}
                className="p-1.5 rounded-lg hover:bg-surface/60 transition-colors text-muted hover:text-text"
                title="Duplicar (Cmd/Ctrl+D)"
              >
                <DuplicateIcon />
              </button>
            )}
          </div>
        </Panel>
      </ReactFlow>

      {/* Floating toolbar when node is selected */}
      {selectedNode && selectedNode.type === 'base' && (
        <div
          className="absolute z-[100] glass-panel px-2.5 py-1.5 flex items-center gap-1.5 rounded-xl"
          style={{
            left: `calc(50% + ${selectedNode.position.x}px)`,
            top: `calc(50% + ${selectedNode.position.y - 50}px)`,
            transform: 'translateX(-50%)',
          }}
        >
          {/* Shape buttons */}
          {shapes.slice(0, 4).map(({ shape, label }) => (
            <button
              key={shape}
              onClick={() => handleChangeShape(shape)}
              title={label}
              className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface/60 transition-colors"
            >
              <ShapeIcon shape={shape} />
            </button>
          ))}

          <div className="w-px h-4 bg-border/30" />

          {/* Color buttons */}
          {colors.map(({ name, value, border }) => (
            <button
              key={name}
              onClick={() => handleChangeColor(value, border)}
              title={name}
              className="w-4 h-4 rounded-full border hover:scale-110 transition-transform"
              style={{ backgroundColor: value, borderColor: border }}
            />
          ))}

          <div className="w-px h-4 bg-border/30" />

          {/* Delete */}
          <button
            onClick={handleDeleteNode}
            className="w-6 h-6 flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
            title="Eliminar"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
          </button>
        </div>
      )}
    </div>
  )
}

export function FlowCanvas() {
  return (
    <ReactFlowProvider>
      <FlowCanvasInner />
    </ReactFlowProvider>
  )
}
