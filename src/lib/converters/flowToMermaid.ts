import { Node, Edge } from 'reactflow'
import type { NodeShape, BaseNodeData } from '@/components/Canvas/nodes'

// Mapeo de formas a sintaxis Mermaid
const shapeToMermaid: Record<NodeShape, (id: string, label: string) => string> = {
  rectangle: (id, label) => `${id}[${label}]`,
  diamond: (id, label) => `${id}{${label}}`,
  circle: (id, label) => `${id}((${label}))`,
  hexagon: (id, label) => `${id}{{${label}}}`,
  chevron: (id, label) => `${id}[/${label}/]`,
  octagon: (id, label) => `${id}[[${label}]]`,
}

interface SwimlaneData {
  label: string
}

// Detectar swimlanes basándose en posiciones
function detectSwimlanes(nodes: Node[]): Map<string, string[]> {
  const swimlanes = new Map<string, string[]>()
  const regularNodes = nodes.filter((n) => n.type !== 'swimlane')
  const swimlaneNodes = nodes.filter((n) => n.type === 'swimlane')

  for (const swimlane of swimlaneNodes) {
    const bounds = {
      x: swimlane.position.x,
      y: swimlane.position.y,
      width: (swimlane.style?.width as number) || 200,
      height: (swimlane.style?.height as number) || 100,
    }

    const containedNodes = regularNodes
      .filter((node) => {
        const nx = node.position.x
        const ny = node.position.y
        return (
          nx >= bounds.x &&
          nx <= bounds.x + bounds.width &&
          ny >= bounds.y &&
          ny <= bounds.y + bounds.height
        )
      })
      .map((n) => n.id)

    const data = swimlane.data as SwimlaneData
    swimlanes.set(data.label || swimlane.id, containedNodes)
  }

  return swimlanes
}

// Detectar dirección predominante
function detectDirection(nodes: Node[], edges: Edge[]): 'TB' | 'LR' {
  let horizontalScore = 0
  let verticalScore = 0

  const nodePositions = new Map(nodes.map((n) => [n.id, n.position]))

  for (const edge of edges) {
    const sourcePos = nodePositions.get(edge.source)
    const targetPos = nodePositions.get(edge.target)

    if (sourcePos && targetPos) {
      const dx = Math.abs(targetPos.x - sourcePos.x)
      const dy = Math.abs(targetPos.y - sourcePos.y)

      if (dx > dy) {
        horizontalScore += 1
      } else {
        verticalScore += 1
      }
    }
  }

  return horizontalScore > verticalScore ? 'LR' : 'TB'
}

// Sanitizar labels para Mermaid
function sanitizeLabel(label: string): string {
  return label
    .replace(/"/g, "'")
    .replace(/\[/g, '(')
    .replace(/\]/g, ')')
    .replace(/\{/g, '(')
    .replace(/\}/g, ')')
    .replace(/\n/g, '<br/>')
}

// Convertir ReactFlow a Mermaid
export function reactFlowToMermaid(nodes: Node[], edges: Edge[]): string {
  const direction = detectDirection(nodes, edges)
  const swimlanes = detectSwimlanes(nodes)
  const regularNodes = nodes.filter((n) => n.type !== 'swimlane')

  const lines: string[] = [`flowchart ${direction}`]

  // Agrupar nodos en swimlanes
  const assignedNodes = new Set<string>()

  for (const [swimlaneName, nodeIds] of swimlanes) {
    if (nodeIds.length > 0) {
      lines.push('')
      lines.push(`  subgraph ${swimlaneName.replace(/\s+/g, '_')}[${swimlaneName}]`)

      for (const nodeId of nodeIds) {
        const node = regularNodes.find((n) => n.id === nodeId)
        if (node) {
          const data = node.data as BaseNodeData
          const label = sanitizeLabel(data.label || nodeId)
          const shape = data.shape || 'rectangle'
          lines.push(`    ${shapeToMermaid[shape](nodeId, label)}`)
          assignedNodes.add(nodeId)
        }
      }

      lines.push('  end')
    }
  }

  // Nodos sin swimlane
  const unassignedNodes = regularNodes.filter((n) => !assignedNodes.has(n.id))
  if (unassignedNodes.length > 0) {
    lines.push('')
    for (const node of unassignedNodes) {
      const data = node.data as BaseNodeData
      const label = sanitizeLabel(data.label || node.id)
      const shape = data.shape || 'rectangle'
      lines.push(`  ${shapeToMermaid[shape](node.id, label)}`)
    }
  }

  // Conexiones
  if (edges.length > 0) {
    lines.push('')
    for (const edge of edges) {
      const label = edge.label ? ` |${edge.label}|` : ''
      lines.push(`  ${edge.source} -->${label} ${edge.target}`)
    }
  }

  return lines.join('\n')
}
