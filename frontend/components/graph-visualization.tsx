"use client"

import { useEffect, useRef } from "react"
import { Network } from "vis-network/standalone/esm/vis-network"
import type { Data, Options, Node, Edge } from "vis-network/standalone/esm/vis-network"
import type { Neo4jNode, Neo4jRelationship } from "@/types/neo4j"
import { Box } from "@mui/material"

interface GraphVisualizationProps {
  onNodeSelect?: (node: any) => void
}

export function GraphVisualization({ onNodeSelect }: GraphVisualizationProps) {
  const networkRef = useRef<HTMLDivElement>(null)
  const networkInstance = useRef<Network | null>(null)

  useEffect(() => {
    if (!networkRef.current) return

    try {
      // Neo4j-style sample data
      const neo4jNodes: Neo4jNode[] = [
        {
          id: "1",
          labels: ["Person"],
          properties: {
            name: "Alice Johnson",
            role: "Software Engineer",
            experience: "5 years",
            location: "San Francisco",
          },
        },
        {
          id: "2",
          labels: ["Person"],
          properties: {
            name: "Bob Smith",
            role: "Data Scientist",
            experience: "7 years",
            location: "New York",
          },
        },
        {
          id: "3",
          labels: ["Company"],
          properties: {
            name: "TechCorp",
            industry: "Technology",
            founded: "2010",
            employees: "500+",
          },
        },
        {
          id: "4",
          labels: ["Company"],
          properties: {
            name: "DataFlow Inc",
            industry: "Data Analytics",
            founded: "2015",
            employees: "200+",
          },
        },
        {
          id: "5",
          labels: ["Technology"],
          properties: {
            name: "React",
            type: "JavaScript Library",
            category: "Frontend",
            version: "18.x",
          },
        },
        {
          id: "6",
          labels: ["Technology"],
          properties: {
            name: "Python",
            type: "Programming Language",
            category: "Backend",
            version: "3.11",
          },
        },
        {
          id: "7",
          labels: ["Technology"],
          properties: {
            name: "Neo4j",
            type: "Graph Database",
            category: "Database",
            version: "5.x",
          },
        },
        {
          id: "8",
          labels: ["Skill"],
          properties: {
            name: "Machine Learning",
            level: "Expert",
            category: "Data Science",
          },
        },
      ]

      const neo4jRelationships: Neo4jRelationship[] = [
        {
          id: "r1",
          startNodeId: "1",
          endNodeId: "3",
          type: "WORKS_AT",
          properties: {
            since: "2020",
            position: "Senior Engineer",
          },
        },
        {
          id: "r2",
          startNodeId: "2",
          endNodeId: "4",
          type: "WORKS_AT",
          properties: {
            since: "2019",
            position: "Lead Data Scientist",
          },
        },
        {
          id: "r3",
          startNodeId: "1",
          endNodeId: "5",
          type: "USES",
          properties: {
            proficiency: "Expert",
            years: "4",
          },
        },
        {
          id: "r4",
          startNodeId: "2",
          endNodeId: "6",
          type: "USES",
          properties: {
            proficiency: "Expert",
            years: "6",
          },
        },
        {
          id: "r5",
          startNodeId: "2",
          endNodeId: "7",
          type: "USES",
          properties: {
            proficiency: "Advanced",
            years: "3",
          },
        },
        {
          id: "r6",
          startNodeId: "1",
          endNodeId: "8",
          type: "HAS_SKILL",
          properties: {
            level: "Senior",
          },
        },
        {
          id: "r7",
          startNodeId: "1",
          endNodeId: "2",
          type: "COLLABORATES_WITH",
          properties: {
            project: "Data Visualization Platform",
          },
        },
      ]

      // Convert Neo4j data to vis-network format
      const getNodeColor = (labels: string[]) => {
        if (labels.includes("Person")) return { background: "#1976d2", border: "#1565c0" }
        if (labels.includes("Company")) return { background: "#2e7d32", border: "#1b5e20" }
        if (labels.includes("Technology")) return { background: "#9c27b0", border: "#7b1fa2" }
        if (labels.includes("Skill")) return { background: "#ed6c02", border: "#e65100" }
        return { background: "#757575", border: "#424242" }
      }

      const getNodeShape = (labels: string[]) => {
        if (labels.includes("Person")) return "dot"
        if (labels.includes("Company")) return "box"
        if (labels.includes("Technology")) return "diamond"
        if (labels.includes("Skill")) return "triangle"
        return "dot"
      }

      const visNodes: Node[] = neo4jNodes.map((node) => ({
        id: node.id,
        label: node.properties.name || `Node ${node.id}`,
        title: `<b>${node.labels.join(", ")}</b><br/>${Object.entries(node.properties)
          .map(([key, value]) => `${key}: ${value}`)
          .join("<br/>")}`,
        color: getNodeColor(node.labels),
        shape: getNodeShape(node.labels),
        size: 25,
        font: { size: 14, color: "#333333" },
        borderWidth: 2,
        shadow: true,
      }))

      const visEdges: Edge[] = neo4jRelationships.map((rel) => ({
        id: rel.id,
        from: rel.startNodeId,
        to: rel.endNodeId,
        label: rel.type,
        title: `<b>${rel.type}</b><br/>${Object.entries(rel.properties)
          .map(([key, value]) => `${key}: ${value}`)
          .join("<br/>")}`,
        arrows: { to: { enabled: true, scaleFactor: 1 } },
        color: { color: "#848484", highlight: "#2B7CE9" },
        font: { size: 12, color: "#666666" },
        smooth: { type: "continuous" },
        width: 2,
      }))

      const data: Data = {
        nodes: visNodes,
        edges: visEdges,
      }

      const options: Options = {
        physics: {
          enabled: true,
          stabilization: { iterations: 100 },
          barnesHut: {
            gravitationalConstant: -2000,
            centralGravity: 0.3,
            springLength: 120,
            springConstant: 0.04,
            damping: 0.09,
          },
        },
        interaction: {
          hover: true,
          tooltipDelay: 200,
          hideEdgesOnDrag: false,
          hideNodesOnDrag: false,
        },
        layout: {
          improvedLayout: true,
          clusterThreshold: 150,
        },
        nodes: {
          borderWidth: 2,
          shadow: true,
          font: {
            size: 14,
            color: "#333333",
          },
        },
        edges: {
          width: 2,
          shadow: true,
          smooth: {
            type: "continuous",
          },
        },
        height: "600px",
        width: "100%",
      }

      // Create network
      networkInstance.current = new Network(networkRef.current, data, options)

      // Add event listeners
      networkInstance.current.on("click", (params) => {
        if (params.nodes.length > 0) {
          const nodeId = params.nodes[0].toString()
          const selectedNode = neo4jNodes.find((n) => n.id === nodeId)
          if (selectedNode && onNodeSelect) {
            onNodeSelect(selectedNode)
          }
        }
      })

      networkInstance.current.on("hoverNode", () => {
        if (networkRef.current) {
          networkRef.current.style.cursor = "pointer"
        }
      })

      networkInstance.current.on("blurNode", () => {
        if (networkRef.current) {
          networkRef.current.style.cursor = "default"
        }
      })

      // Store network instance for controls
      ;(window as any).networkInstance = networkInstance.current
    } catch (error) {
      console.error("Error initializing graph visualization:", error)
    }

    // Cleanup
    return () => {
      if (networkInstance.current) {
        try {
          networkInstance.current.destroy()
          networkInstance.current = null
        } catch (error) {
          console.error("Error destroying network instance:", error)
        }
      }
    }
  }, [onNodeSelect])

  return (
    <Box
      ref={networkRef}
      sx={{
        width: "100%",
        height: 600,
        border: 1,
        borderColor: "divider",
        borderRadius: 2,
        bgcolor: "background.paper",
        overflow: "hidden",
      }}
    />
  )
}
