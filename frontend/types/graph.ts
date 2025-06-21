export interface Neo4jNode {
  id: string
  labels: string[]
  properties: Record<string, any>
}

export interface Neo4jRelationship {
  id: string
  type: string
  startNodeId: string
  endNodeId: string
  properties: Record<string, any>
}

export interface GraphData {
  nodes: Neo4jNode[]
  relationships: Neo4jRelationship[]
}

export interface VisNode {
  id: string
  label: string
  group: string
  title?: string
  color?: {
    background: string
    border: string
  }
  shape?: string
  size?: number
}

export interface VisEdge {
  id: string
  from: string
  to: string
  label: string
  title?: string
  color?: {
    color: string
    highlight: string
  }
}
