"use client"

import { useState, useEffect } from "react"
import type { Neo4jNode, Neo4jRelationship, GraphStats } from "@/types/neo4j"

interface GraphData {
  nodes: Neo4jNode[]
  relationships: Neo4jRelationship[]
  stats: GraphStats
}

interface UseGraphDataReturn {
  data: GraphData | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useGraphData(): UseGraphDataReturn {
  const [data, setData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch both nodes and relationships from API
      const [nodesResponse, relationshipsResponse] = await Promise.all([
        fetch("/api/neo4j/nodes"),
        fetch("/api/neo4j/relationships"),
      ])

      if (!nodesResponse.ok) {
        throw new Error(`Failed to fetch nodes: ${nodesResponse.status}`)
      }

      if (!relationshipsResponse.ok) {
        throw new Error(`Failed to fetch relationships: ${relationshipsResponse.status}`)
      }

      const nodesData = await nodesResponse.json()
      const relationshipsData = await relationshipsResponse.json()

      // Extract nodes and relationships from API response
      const nodes = Array.isArray(nodesData) ? nodesData : nodesData.nodes || []
      const relationships = Array.isArray(relationshipsData) ? relationshipsData : relationshipsData.relationships || []

      // Calculate statistics from the fetched data
      const stats: GraphStats = {
        nodeCount: nodes.length,
        relationshipCount: relationships.length,
        labelCounts: nodes.reduce((acc: Record<string, number>, node: Neo4jNode) => {
          node.labels.forEach((label: string) => {
            acc[label] = (acc[label] || 0) + 1
          })
          return acc
        }, {}),
        relationshipTypeCounts: relationships.reduce((acc: Record<string, number>, rel: Neo4jRelationship) => {
          acc[rel.type] = (acc[rel.type] || 0) + 1
          return acc
        }, {}),
      }

      setData({
        nodes,
        relationships,
        stats,
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred"
      setError(errorMessage)
      console.error("Error fetching graph data:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const refetch = async () => {
    await fetchData()
  }

  return { data, loading, error, refetch }
}
