import { describe, it, expect } from 'vitest'
import { reactFlowToMermaid } from './flowToMermaid'
import { Node, Edge } from 'reactflow'

describe('reactFlowToMermaid', () => {
  describe('basic conversion', () => {
    it('converts simple nodes to mermaid', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Start', shape: 'rectangle' } },
        { id: 'B', type: 'base', position: { x: 200, y: 0 }, data: { label: 'End', shape: 'rectangle' } },
      ]
      const edges: Edge[] = [
        { id: 'e1', source: 'A', target: 'B' },
      ]

      const result = reactFlowToMermaid(nodes, edges)

      expect(result).toContain('flowchart')
      expect(result).toContain('A[Start]')
      expect(result).toContain('B[End]')
      expect(result).toContain('A --> B')
    })

    it('handles empty diagram', () => {
      const result = reactFlowToMermaid([], [])

      expect(result).toContain('flowchart')
      expect(result).not.toContain('-->')
    })
  })

  describe('shape conversion', () => {
    it('converts circle shape to (( )) syntax', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Circle', shape: 'circle' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      expect(result).toContain('A((Circle))')
    })

    it('converts diamond shape to { } syntax', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Decision', shape: 'diamond' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      expect(result).toContain('A{Decision}')
    })

    it('converts hexagon shape to {{ }} syntax', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Automated', shape: 'hexagon' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      expect(result).toContain('A{{Automated}}')
    })

    it('converts chevron shape to [/ /] syntax', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Input', shape: 'chevron' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      expect(result).toContain('A[/Input/]')
    })

    it('converts octagon shape to [[ ]] syntax', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Process', shape: 'octagon' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      expect(result).toContain('A[[Process]]')
    })
  })

  describe('direction detection', () => {
    it('detects LR direction for horizontal layouts', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 100 }, data: { label: 'A', shape: 'rectangle' } },
        { id: 'B', type: 'base', position: { x: 200, y: 100 }, data: { label: 'B', shape: 'rectangle' } },
        { id: 'C', type: 'base', position: { x: 400, y: 100 }, data: { label: 'C', shape: 'rectangle' } },
      ]
      const edges: Edge[] = [
        { id: 'e1', source: 'A', target: 'B' },
        { id: 'e2', source: 'B', target: 'C' },
      ]

      const result = reactFlowToMermaid(nodes, edges)

      expect(result).toContain('flowchart LR')
    })

    it('detects TB direction for vertical layouts', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 100, y: 0 }, data: { label: 'A', shape: 'rectangle' } },
        { id: 'B', type: 'base', position: { x: 100, y: 100 }, data: { label: 'B', shape: 'rectangle' } },
        { id: 'C', type: 'base', position: { x: 100, y: 200 }, data: { label: 'C', shape: 'rectangle' } },
      ]
      const edges: Edge[] = [
        { id: 'e1', source: 'A', target: 'B' },
        { id: 'e2', source: 'B', target: 'C' },
      ]

      const result = reactFlowToMermaid(nodes, edges)

      expect(result).toContain('flowchart TB')
    })
  })

  describe('edge labels', () => {
    it('includes edge labels in output', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Start', shape: 'rectangle' } },
        { id: 'B', type: 'base', position: { x: 200, y: 0 }, data: { label: 'Yes', shape: 'rectangle' } },
        { id: 'C', type: 'base', position: { x: 200, y: 100 }, data: { label: 'No', shape: 'rectangle' } },
      ]
      const edges: Edge[] = [
        { id: 'e1', source: 'A', target: 'B', label: 'yes' },
        { id: 'e2', source: 'A', target: 'C', label: 'no' },
      ]

      const result = reactFlowToMermaid(nodes, edges)

      expect(result).toContain('|yes|')
      expect(result).toContain('|no|')
    })
  })

  describe('swimlanes', () => {
    it('groups nodes in swimlanes based on position', () => {
      const nodes: Node[] = [
        {
          id: 'swimlane-client',
          type: 'swimlane',
          position: { x: 0, y: 0 },
          data: { label: 'Client' },
          style: { width: 300, height: 200 }
        },
        { id: 'A', type: 'base', position: { x: 50, y: 50 }, data: { label: 'Request', shape: 'rectangle' } },
        { id: 'B', type: 'base', position: { x: 150, y: 50 }, data: { label: 'Wait', shape: 'rectangle' } },
      ]
      const edges: Edge[] = [
        { id: 'e1', source: 'A', target: 'B' },
      ]

      const result = reactFlowToMermaid(nodes, edges)

      expect(result).toContain('subgraph Client')
      expect(result).toContain('end')
    })
  })

  describe('label sanitization', () => {
    it('escapes special characters in labels', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Test "quoted"', shape: 'rectangle' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      // Double quotes should be converted to single quotes
      expect(result).toContain("Test 'quoted'")
    })

    it('handles brackets in labels', () => {
      const nodes: Node[] = [
        { id: 'A', type: 'base', position: { x: 0, y: 0 }, data: { label: 'Array[0]', shape: 'rectangle' } },
      ]

      const result = reactFlowToMermaid(nodes, [])

      // Brackets should be converted to parentheses
      expect(result).toContain('Array(0)')
    })
  })
})
