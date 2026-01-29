import BaseNode from './BaseNode'
import type { NodeShape, BaseNodeData } from './BaseNode'

// Nodos especializados que usan BaseNode con diferentes shapes por defecto
export const nodeTypes = {
  base: BaseNode,
  rectangle: BaseNode,
  diamond: BaseNode,
  circle: BaseNode,
  hexagon: BaseNode,
  chevron: BaseNode,
  octagon: BaseNode,
}

export type { NodeShape, BaseNodeData }
export { BaseNode }
