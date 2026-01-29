import { Node, Edge } from 'reactflow'
import type { NodeShape, BaseNodeData } from '@/components/Canvas/nodes'

interface ParsedNode {
  id: string
  label: string
  shape: NodeShape
}

interface ParsedEdge {
  source: string
  target: string
  label?: string
}

interface ParsedSubgraph {
  id: string
  label: string
  nodes: string[]
}

// Detectar forma basándose en la sintaxis de Mermaid
function detectShape(nodeDefinition: string): { id: string; label: string; shape: NodeShape } {
  // Patrones de Mermaid - ORDEN IMPORTA (más específico primero)
  const patterns: { regex: RegExp; shape: NodeShape }[] = [
    // ((texto)) - círculo
    { regex: /^(\w+)\(\((.+)\)\)$/, shape: 'circle' },
    // {{texto}} - hexágono (ANTES de diamond para no confundir)
    { regex: /^(\w+)\{\{(.+)\}\}$/, shape: 'hexagon' },
    // {texto} - rombo
    { regex: /^(\w+)\{(.+)\}$/, shape: 'diamond' },
    // [/texto/] - paralelogramo (usamos chevron)
    { regex: /^(\w+)\[\/(.+)\/\]$/, shape: 'chevron' },
    // [[texto]] - rectángulo con bordes dobles (usamos octágono)
    { regex: /^(\w+)\[\[(.+)\]\]$/, shape: 'octagon' },
    // [texto] - rectángulo (default)
    { regex: /^(\w+)\[(.+)\]$/, shape: 'rectangle' },
    // (texto) - rectángulo redondeado
    { regex: /^(\w+)\((.+)\)$/, shape: 'rectangle' },
    // Solo ID sin forma
    { regex: /^(\w+)$/, shape: 'rectangle' },
  ]

  for (const { regex, shape } of patterns) {
    const match = nodeDefinition.match(regex)
    if (match) {
      return {
        id: match[1],
        label: match[2] || match[1],
        shape,
      }
    }
  }

  // Fallback
  return { id: nodeDefinition, label: nodeDefinition, shape: 'rectangle' }
}

// Parsear código Mermaid a estructura intermedia
function parseMermaid(code: string): {
  nodes: ParsedNode[]
  edges: ParsedEdge[]
  subgraphs: ParsedSubgraph[]
  direction: 'TB' | 'LR' | 'BT' | 'RL'
} {
  const lines = code.split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('%%'))
  const nodes: Map<string, ParsedNode> = new Map()
  const edges: ParsedEdge[] = []
  const subgraphs: ParsedSubgraph[] = []
  let direction: 'TB' | 'LR' | 'BT' | 'RL' = 'TB'
  let currentSubgraph: ParsedSubgraph | null = null

  for (const line of lines) {
    // Detectar dirección
    if (line.match(/^flowchart\s+(TB|LR|BT|RL)/i) || line.match(/^graph\s+(TB|LR|BT|RL)/i)) {
      const match = line.match(/(TB|LR|BT|RL)/i)
      if (match) direction = match[1].toUpperCase() as 'TB' | 'LR' | 'BT' | 'RL'
      continue
    }

    // Detectar subgraph
    if (line.match(/^subgraph\s+/i)) {
      const match = line.match(/^subgraph\s+(\w+)(?:\s*\[(.+)\])?/i)
      if (match) {
        currentSubgraph = {
          id: match[1],
          label: match[2] || match[1],
          nodes: [],
        }
      }
      continue
    }

    if (line === 'end' && currentSubgraph) {
      subgraphs.push(currentSubgraph)
      currentSubgraph = null
      continue
    }

    // Detectar conexiones - puede haber múltiples en una línea (A --> B --> C)
    // Primero, dividir por --> para manejar cadenas
    if (line.includes('-->')) {
      // Regex para extraer nodos - incluye formas especiales
      // Nota: El orden importa, más específico primero
      const nodePattern = /(\w+(?:\[\[.+?\]\]|\[.+?\]|\(\(.+?\)\)|\(.+?\)|\{\{.+?\}\}|\{.+?\})?)/g
      const parts = line.split(/\s*-->\s*/)

      for (let i = 0; i < parts.length - 1; i++) {
        // Limpiar parte para extraer nodo y posible label
        let sourcePart = parts[i].trim()
        let targetPart = parts[i + 1].trim()
        let edgeLabel: string | undefined

        // Extraer label si existe (formato |label|)
        const labelMatch = targetPart.match(/^\|(.+?)\|\s*(.+)$/)
        if (labelMatch) {
          edgeLabel = labelMatch[1]
          targetPart = labelMatch[2]
        }

        // Quedarnos solo con el último nodo de sourcePart (por si hay labels previos)
        const sourceMatches = sourcePart.match(nodePattern)
        if (sourceMatches) {
          sourcePart = sourceMatches[sourceMatches.length - 1]
        }

        // Quedarnos solo con el primer nodo de targetPart
        const targetMatches = targetPart.match(nodePattern)
        if (targetMatches) {
          targetPart = targetMatches[0]
        }

        const sourceNode = detectShape(sourcePart)
        const targetNode = detectShape(targetPart)

        if (!nodes.has(sourceNode.id)) nodes.set(sourceNode.id, sourceNode)
        if (!nodes.has(targetNode.id)) nodes.set(targetNode.id, targetNode)

        edges.push({
          source: sourceNode.id,
          target: targetNode.id,
          label: edgeLabel,
        })

        if (currentSubgraph) {
          if (!currentSubgraph.nodes.includes(sourceNode.id)) currentSubgraph.nodes.push(sourceNode.id)
          if (!currentSubgraph.nodes.includes(targetNode.id)) currentSubgraph.nodes.push(targetNode.id)
        }
      }
      continue
    }

    // Detectar definición de nodo solo
    const nodeMatch = line.match(/^(\w+)(\[.+\]|\(.+\)|\{.+\})?$/)
    if (nodeMatch && !line.includes('-->')) {
      const parsed = detectShape(line)
      if (!nodes.has(parsed.id)) {
        nodes.set(parsed.id, parsed)
        if (currentSubgraph) {
          currentSubgraph.nodes.push(parsed.id)
        }
      }
    }
  }

  return {
    nodes: Array.from(nodes.values()),
    edges,
    subgraphs,
    direction,
  }
}

// Calcular posiciones estilo FigJam (3 capas)
function calculatePositions(
  nodes: ParsedNode[],
  edges: ParsedEdge[],
  subgraphs: ParsedSubgraph[],
  direction: 'TB' | 'LR' | 'BT' | 'RL'
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>()
  const nodeSpacingX = 200
  const nodeSpacingY = 120
  const swimlaneHeight = 120
  const topPadding = 80

  // Identificar nodos de etapa (chevrons fuera de subgraphs)
  const subgraphNodeIds = new Set<string>()
  for (const sg of subgraphs) {
    for (const nodeId of sg.nodes) {
      subgraphNodeIds.add(nodeId)
    }
  }

  // Etapas son chevrons que NO están en ningún subgraph
  const stageNodes = nodes.filter(n => n.shape === 'chevron' && !subgraphNodeIds.has(n.id))
  const regularNodes = nodes.filter(n => !stageNodes.includes(n))

  // CAPA 1: Etapas cronológicas (arriba)
  const stageOrder: string[] = []
  if (stageNodes.length > 0) {
    const stageIds = new Set(stageNodes.map(n => n.id))
    const stageEdges = edges.filter(e => stageIds.has(e.source) && stageIds.has(e.target))

    const incomingCount = new Map<string, number>()
    for (const node of stageNodes) incomingCount.set(node.id, 0)
    for (const edge of stageEdges) {
      incomingCount.set(edge.target, (incomingCount.get(edge.target) || 0) + 1)
    }

    let current = stageNodes.find(n => incomingCount.get(n.id) === 0)?.id
    const visited = new Set<string>()
    while (current && !visited.has(current)) {
      stageOrder.push(current)
      visited.add(current)
      const nextEdge = stageEdges.find(e => e.source === current)
      current = nextEdge?.target
    }
    for (const node of stageNodes) {
      if (!visited.has(node.id)) stageOrder.push(node.id)
    }
  }

  for (let i = 0; i < stageOrder.length; i++) {
    positions.set(stageOrder[i], {
      x: 100 + i * nodeSpacingX,
      y: topPadding,
    })
  }

  // CAPA 2: Swimlanes (filas de actores)
  for (let swimlaneIdx = 0; swimlaneIdx < subgraphs.length; swimlaneIdx++) {
    const subgraph = subgraphs[swimlaneIdx]
    const swimlaneY = topPadding + 100 + swimlaneIdx * (swimlaneHeight + 60)

    const swimlaneNodeIds = new Set(subgraph.nodes)
    const swimlaneNodesList = regularNodes.filter(n => swimlaneNodeIds.has(n.id))
    const internalEdges = edges.filter(e => swimlaneNodeIds.has(e.source) && swimlaneNodeIds.has(e.target))

    const nodeOrder: string[] = []
    const inDegree = new Map<string, number>()
    for (const node of swimlaneNodesList) inDegree.set(node.id, 0)
    for (const edge of internalEdges) {
      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1)
    }

    let queue = swimlaneNodesList.filter(n => inDegree.get(n.id) === 0).map(n => n.id)
    const visitedNodes = new Set<string>()
    while (queue.length > 0) {
      const current = queue.shift()!
      if (!visitedNodes.has(current)) {
        nodeOrder.push(current)
        visitedNodes.add(current)
        for (const edge of internalEdges) {
          if (edge.source === current) {
            const newDegree = (inDegree.get(edge.target) || 1) - 1
            inDegree.set(edge.target, newDegree)
            if (newDegree === 0 && !visitedNodes.has(edge.target)) {
              queue.push(edge.target)
            }
          }
        }
      }
    }

    for (const node of swimlaneNodesList) {
      if (!visitedNodes.has(node.id)) nodeOrder.push(node.id)
    }

    for (let i = 0; i < nodeOrder.length; i++) {
      positions.set(nodeOrder[i], {
        x: 100 + i * nodeSpacingX,
        y: swimlaneY + 60,
      })
    }
  }

  // Nodos sueltos (no en swimlanes, no etapas)
  // Estos SÍ respetan la dirección del diagrama
  const looseNodes = regularNodes.filter(n => !subgraphNodeIds.has(n.id))

  if (looseNodes.length > 0) {
    // Ordenar topológicamente los nodos sueltos
    const looseNodeIds = new Set(looseNodes.map(n => n.id))
    const looseEdges = edges.filter(e => looseNodeIds.has(e.source) && looseNodeIds.has(e.target))

    const inDegree = new Map<string, number>()
    for (const node of looseNodes) inDegree.set(node.id, 0)
    for (const edge of looseEdges) {
      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1)
    }

    const nodeOrder: string[] = []
    let queue = looseNodes.filter(n => inDegree.get(n.id) === 0).map(n => n.id)
    const visitedNodes = new Set<string>()

    while (queue.length > 0) {
      const current = queue.shift()!
      if (!visitedNodes.has(current)) {
        nodeOrder.push(current)
        visitedNodes.add(current)
        for (const edge of looseEdges) {
          if (edge.source === current) {
            const newDegree = (inDegree.get(edge.target) || 1) - 1
            inDegree.set(edge.target, newDegree)
            if (newDegree === 0 && !visitedNodes.has(edge.target)) {
              queue.push(edge.target)
            }
          }
        }
      }
    }

    for (const node of looseNodes) {
      if (!visitedNodes.has(node.id)) nodeOrder.push(node.id)
    }

    // Posicionar según dirección
    const baseX = 100
    const baseY = topPadding + 100 + subgraphs.length * (swimlaneHeight + 60)

    for (let i = 0; i < nodeOrder.length; i++) {
      if (!positions.has(nodeOrder[i])) {
        if (direction === 'LR' || direction === 'RL') {
          // Horizontal: incrementar X
          positions.set(nodeOrder[i], {
            x: baseX + i * nodeSpacingX,
            y: baseY,
          })
        } else {
          // TB/BT: incrementar Y
          positions.set(nodeOrder[i], {
            x: baseX,
            y: baseY + i * nodeSpacingY,
          })
        }
      }
    }
  }

  return positions
}

// Convertir a formato ReactFlow
export function mermaidToReactFlow(code: string): { nodes: Node<BaseNodeData>[]; edges: Edge[] } {
  const { nodes: parsedNodes, edges: parsedEdges, subgraphs, direction } = parseMermaid(code)
  const positions = calculatePositions(parsedNodes, parsedEdges, subgraphs, direction)

  const nodes: Node<BaseNodeData>[] = parsedNodes.map((node) => ({
    id: node.id,
    type: 'base',
    position: positions.get(node.id) || { x: 0, y: 0 },
    data: {
      label: node.label,
      shape: node.shape,
    },
  }))

  // Añadir swimlanes como nodos de fondo
  for (const subgraph of subgraphs) {
    const subgraphNodes = subgraph.nodes
      .map((id) => positions.get(id))
      .filter(Boolean) as { x: number; y: number }[]

    if (subgraphNodes.length > 0) {
      const minX = Math.min(...subgraphNodes.map((p) => p.x)) - 40
      const maxX = Math.max(...subgraphNodes.map((p) => p.x)) + 160
      const minY = Math.min(...subgraphNodes.map((p) => p.y)) - 40
      const maxY = Math.max(...subgraphNodes.map((p) => p.y)) + 80

      nodes.unshift({
        id: `swimlane-${subgraph.id}`,
        type: 'swimlane',
        position: { x: minX, y: minY },
        data: { label: subgraph.label },
        style: { width: maxX - minX, height: maxY - minY },
        zIndex: -1,
      } as Node)
    }
  }

  const edges: Edge[] = parsedEdges.map((edge, idx) => ({
    id: `e-${edge.source}-${edge.target}-${idx}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    style: { stroke: '#6B5B4F', strokeWidth: 2 },
  }))

  return { nodes, edges }
}
