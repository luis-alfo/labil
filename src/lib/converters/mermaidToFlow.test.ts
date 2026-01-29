import { describe, it, expect } from 'vitest'
import { mermaidToReactFlow } from './mermaidToFlow'

describe('mermaidToReactFlow', () => {
  describe('basic parsing', () => {
    it('parses simple flowchart with rectangles', () => {
      const mermaid = `flowchart LR
        A[Inicio] --> B[Proceso] --> C[Fin]`

      const { nodes, edges } = mermaidToReactFlow(mermaid)

      expect(nodes).toHaveLength(3)
      expect(nodes[0].data.label).toBe('Inicio')
      expect(nodes[0].data.shape).toBe('rectangle')
      expect(nodes[1].data.label).toBe('Proceso')
      expect(nodes[2].data.label).toBe('Fin')

      expect(edges).toHaveLength(2)
      expect(edges[0].source).toBe('A')
      expect(edges[0].target).toBe('B')
    })

    it('detects circle shape from (( )) syntax', () => {
      const mermaid = `flowchart TB
        A((Start)) --> B[Process]`

      const { nodes } = mermaidToReactFlow(mermaid)

      expect(nodes.find(n => n.id === 'A')?.data.shape).toBe('circle')
      expect(nodes.find(n => n.id === 'B')?.data.shape).toBe('rectangle')
    })

    it('detects diamond shape from { } syntax', () => {
      const mermaid = `flowchart TB
        A[Start] --> B{Decision}
        B --> C[Yes]
        B --> D[No]`

      const { nodes } = mermaidToReactFlow(mermaid)

      expect(nodes.find(n => n.id === 'B')?.data.shape).toBe('diamond')
    })

    it('detects hexagon shape from {{ }} syntax', () => {
      const mermaid = `flowchart LR
        A[Manual] --> B{{Automated}}`

      const { nodes } = mermaidToReactFlow(mermaid)

      expect(nodes.find(n => n.id === 'B')?.data.shape).toBe('hexagon')
    })
  })

  describe('subgraphs / swimlanes', () => {
    it('parses subgraphs as swimlane nodes', () => {
      const mermaid = `flowchart LR
        subgraph Cliente
          A[Solicita] --> B[Espera]
        end
        subgraph Sistema
          C[Procesa] --> D[Responde]
        end
        B --> C`

      const { nodes, edges } = mermaidToReactFlow(mermaid)

      // Should have swimlane nodes
      const swimlanes = nodes.filter(n => n.type === 'swimlane')
      expect(swimlanes.length).toBeGreaterThanOrEqual(1)

      // Should have regular nodes
      const regularNodes = nodes.filter(n => n.type === 'base')
      expect(regularNodes).toHaveLength(4)

      // Should have connection between subgraphs
      expect(edges.some(e => e.source === 'B' && e.target === 'C')).toBe(true)
    })
  })

  describe('direction detection', () => {
    it('detects LR direction', () => {
      const mermaid = `flowchart LR
        A --> B`

      const { nodes } = mermaidToReactFlow(mermaid)

      // In LR, node B should be to the right of A
      const nodeA = nodes.find(n => n.id === 'A')
      const nodeB = nodes.find(n => n.id === 'B')

      expect(nodeB!.position.x).toBeGreaterThan(nodeA!.position.x)
    })

    it('detects TB direction', () => {
      const mermaid = `flowchart TB
        A --> B`

      const { nodes } = mermaidToReactFlow(mermaid)

      // In TB, node B should be below A
      const nodeA = nodes.find(n => n.id === 'A')
      const nodeB = nodes.find(n => n.id === 'B')

      expect(nodeB!.position.y).toBeGreaterThan(nodeA!.position.y)
    })
  })

  describe('edge labels', () => {
    it('parses edge labels', () => {
      const mermaid = `flowchart LR
        A --> |yes| B
        A --> |no| C`

      const { edges } = mermaidToReactFlow(mermaid)

      expect(edges.find(e => e.target === 'B')?.label).toBe('yes')
      expect(edges.find(e => e.target === 'C')?.label).toBe('no')
    })
  })

  describe('complex diagrams', () => {
    it('handles multi-line labels', () => {
      const mermaid = `flowchart LR
        A[Step One] --> B[Step Two]`

      const { nodes } = mermaidToReactFlow(mermaid)

      expect(nodes.find(n => n.id === 'A')?.data.label).toBe('Step One')
      expect(nodes.find(n => n.id === 'B')?.data.label).toBe('Step Two')
    })

    it('handles nodes with numbers in IDs', () => {
      const mermaid = `flowchart LR
        step1[First] --> step2[Second]`

      const { nodes, edges } = mermaidToReactFlow(mermaid)

      expect(nodes).toHaveLength(2)
      expect(edges[0].source).toBe('step1')
      expect(edges[0].target).toBe('step2')
    })
  })

  describe('error handling', () => {
    it('returns empty arrays for invalid input', () => {
      const { nodes, edges } = mermaidToReactFlow('')

      expect(nodes).toHaveLength(0)
      expect(edges).toHaveLength(0)
    })

    it('handles malformed mermaid gracefully', () => {
      const mermaid = `not valid mermaid at all`

      // Should not throw
      expect(() => mermaidToReactFlow(mermaid)).not.toThrow()
    })
  })
})
