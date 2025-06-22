export interface Neo4jNode {
  id: string
  labels: string[]
  properties: Record<string, any>
}

export interface Neo4jRelationship {
  id: string
  startNodeId: string
  endNodeId: string
  type: string
  properties: Record<string, any>
}

export interface GraphData {
  nodes: Neo4jNode[]
  relationships: Neo4jRelationship[]
}

export interface GraphStats {
  nodeCount: number
  relationshipCount: number
  labelCounts: Record<string, number>
  relationshipTypeCounts: Record<string, number>
}
