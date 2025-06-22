"use client"

import { useEffect, useRef, useState } from "react"
import { Network } from "vis-network/standalone/esm/vis-network"
import type { Data, Options, Node, Edge } from "vis-network/standalone/esm/vis-network"
import type { Neo4jNode, Neo4jRelationship } from "@/types/neo4j"
import { Box, CircularProgress, Alert, Button } from "@mui/material"
import { Refresh } from "@mui/icons-material"

interface GraphVisualizationProps {
  nodes: Neo4jNode[]
  relationships: Neo4jRelationship[]
  loading?: boolean
  error?: string | null
  onNodeSelect?: (node: any) => void
  onRefresh?: () => void
}

export function GraphVisualization({
  nodes,
  relationships,
  loading = false,
  error = null,
  onNodeSelect,
  onRefresh,
}: GraphVisualizationProps) {
  const networkRef = useRef<HTMLDivElement>(null)
  const networkInstance = useRef<Network | null>(null)
  const [isInitializing, setIsInitializing] = useState(false)

  useEffect(() => {
    if (!networkRef.current || loading || error || !nodes.length || !relationships.length) return

    const initializeGraph = () => {
      try {
        setIsInitializing(true)

        // Convert Neo4j data to vis-network format with supply chain specific styling
        function getNodeShape(labels: string[]) {
          if (labels.includes("UseCase")) return "star"
          if (labels.includes("RawMaterial")) return "box"
          if (labels.includes("Country")) return "dot"
          return "dot"
        }

        function getNodeSize(labels: string[], properties: any) {
          if (labels.includes("UseCase")) return 40
          if (labels.includes("RawMaterial")) return 30
          if (labels.includes("Country")) {
            const score = properties.composite_score || 0
            return 20 + score * 2 // Scale from 20 to 35
          }
          return 25
        }

        // Group nodes by type
        const useCaseNodes = nodes.filter(n => n.labels.includes("UseCase"))
        const rawMaterialNodes = nodes.filter(n => n.labels.includes("RawMaterial"))
        const countryNodes = nodes.filter(n => n.labels.includes("Country"))

        // Build a map: rawMaterialId -> countryIds[]
        const rawMaterialToCountries = new Map<string, string[]>()
        relationships.forEach(rel => {
          if (rel.type === 'COUNTRY') {
            // rel.startNodeId: raw material, rel.endNodeId: country
            if (!rawMaterialToCountries.has(rel.startNodeId)) {
              rawMaterialToCountries.set(rel.startNodeId, [])
            }
            rawMaterialToCountries.get(rel.startNodeId)!.push(rel.endNodeId)
          }
        })

        // Assign unique colors to country nodes per raw material
        // Map: countryId+rawMaterialId -> colorRank
        const countryColorMap = new Map<string, string>()
        rawMaterialToCountries.forEach((countryIds, rawMaterialId) => {
          // Get country node objects for this raw material
          const groupCountries = countryIds.map(cid => countryNodes.find(n => n.id === cid)).filter(Boolean) as typeof countryNodes
          if (groupCountries.length >= 1) {
            // Find the highest composite score
            const maxScore = Math.max(...groupCountries.map(n => n.properties.composite_score || 0))
            // Assign green to the first node with max score, yellow to the rest
            let greenAssigned = false
            groupCountries.forEach(n => {
              const key = `${rawMaterialId}|${n.id}`
              if (!greenAssigned && (n.properties.composite_score || 0) === maxScore) {
                countryColorMap.set(key, 'green')
                greenAssigned = true
              } else {
                countryColorMap.set(key, 'yellow')
              }
            })
          }
        })

        // Helper to space nodes horizontally
        function spacedX(total: number, idx: number, spread = 600) {
          if (total === 1) return 0
          return -spread / 2 + (spread / (total - 1)) * idx
        }

        const visNodes: Node[] = [
          ...useCaseNodes.map((node, idx) => ({
            id: node.id,
            label: node.properties.name || `Node ${node.id}`,
            title: `<b>${node.labels.join(", ")}</b><br/>${Object.entries(node.properties)
              .map(([key, value]) => `${key}: ${value}`)
              .join("<br/>")}`,
            color: getNodeColor(node.labels, node.properties),
            shape: getNodeShape(node.labels),
            size: getNodeSize(node.labels, node.properties),
            font: { size: 14, color: "#333333" },
            borderWidth: 2,
            shadow: true,
            x: spacedX(useCaseNodes.length, idx, 300),
            y: -300,
            fixed: false, // allow moving after initial layout
          })),
          ...rawMaterialNodes.map((node, idx) => ({
            id: node.id,
            label: node.properties.name || `Node ${node.id}`,
            title: `<b>${node.labels.join(", ")}</b><br/>${Object.entries(node.properties)
              .map(([key, value]) => `${key}: ${value}`)
              .join("<br/>")}`,
            color: getNodeColor(node.labels, node.properties),
            shape: getNodeShape(node.labels),
            size: getNodeSize(node.labels, node.properties),
            font: { size: 14, color: "#333333" },
            borderWidth: 2,
            shadow: true,
            x: spacedX(rawMaterialNodes.length, idx, 500),
            y: 0,
            fixed: false, // allow moving after initial layout
          })),
          ...countryNodes.map((node, idx) => {
            // Find the raw material parent for this country (first one if multiple)
            const rel = relationships.find(r => r.type === 'COUNTRY' && r.endNodeId === node.id)
            const rawMaterialId = rel ? rel.startNodeId : undefined
            const colorRank = rawMaterialId ? countryColorMap.get(`${rawMaterialId}|${node.id}`) : undefined
            return {
              id: node.id,
              label: node.properties.name || `Node ${node.id}`,
              title: `<b>${node.labels.join(", ")}</b><br/>${Object.entries(node.properties)
                .map(([key, value]) => `${key}: ${value}`)
                .join("<br/>")}`,
              color: getNodeColor(node.labels, node.properties, colorRank),
              shape: getNodeShape(node.labels),
              size: getNodeSize(node.labels, node.properties),
              font: { size: 14, color: "#333333" },
              borderWidth: 2,
              shadow: true,
              x: spacedX(countryNodes.length, idx, 800),
              y: 250,
              fixed: false, // allow moving after initial layout
            }
          }),
        ]

        const getEdgeColor = (type: string) => {
          if (type === "RAW MATERIALS") return { color: "#1976d2", highlight: "#1565c0" }
          if (type === "COUNTRY") return { color: "#2e7d32", highlight: "#1b5e20" }
          return { color: "#848484", highlight: "#2B7CE9" }
        }

        const visEdges: Edge[] = relationships.map((rel) => ({
          id: rel.id,
          from: rel.startNodeId,
          to: rel.endNodeId,
          label: rel.type,
          title: `<b>${rel.type}</b>`,
          arrows: { to: { enabled: true, scaleFactor: 1.2 } },
          color: getEdgeColor(rel.type),
          font: { size: 12, color: "#666666" },
          smooth: { enabled: true, type: "continuous", roundness: 0.5 },
          width: 3,
        }))

        const data: Data = {
          nodes: visNodes,
          edges: visEdges,
        }

        const options: Options = {
          physics: {
            enabled: true,
            stabilization: { iterations: 150 },
            barnesHut: {
              gravitationalConstant: -3000,
              centralGravity: 0.4,
              springLength: 150,
              springConstant: 0.05,
              damping: 0.1,
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
            width: 3,
            shadow: true,
            smooth: {
              enabled: true,
              type: "continuous",
              roundness: 0.5,
            },
          },
          height: "600px",
          width: "100%",
        }

        // Destroy existing network if it exists
        if (networkInstance.current) {
          networkInstance.current.destroy()
        }

        // Create network
        networkInstance.current = new Network(networkRef.current!, data, options)

        // Add event listeners
        networkInstance.current.on("click", (params) => {
          if (params.nodes.length > 0) {
            const nodeId = params.nodes[0].toString()
            const selectedNode = nodes.find((n) => n.id === nodeId)
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

        networkInstance.current.on("stabilizationIterationsDone", () => {
          setIsInitializing(false)
        })

        // Store network instance for controls
        ;(window as any).networkInstance = networkInstance.current
      } catch (error) {
        console.error("Error initializing graph visualization:", error)
        setIsInitializing(false)
      }
    }

    // Delay initialization to ensure DOM is ready
    const timer = setTimeout(initializeGraph, 100)

    // Cleanup
    return () => {
      clearTimeout(timer)
      if (networkInstance.current) {
        try {
          networkInstance.current.destroy()
          networkInstance.current = null
        } catch (error) {
          console.error("Error destroying network instance:", error)
        }
      }
    }
  }, [nodes, relationships, loading, error, onNodeSelect])

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert
          severity="error"
          action={
            onRefresh && (
              <Button color="inherit" size="small" onClick={onRefresh} startIcon={<Refresh />}>
                Retry
              </Button>
            )
          }
        >
          Error loading graph data: {error}
        </Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ position: "relative" }}>
      {(loading || isInitializing) && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: "background.paper",
            zIndex: 1,
            borderRadius: 2,
          }}
        >
          <CircularProgress />
        </Box>
      )}
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
          opacity: loading || isInitializing ? 0.3 : 1,
          transition: "opacity 0.3s ease-in-out",
        }}
      />
    </Box>
  )
}

// Update getNodeColor to accept colorRank
function getNodeColor(labels: string[], properties: any, colorRank?: string) {
  if (labels.includes("UseCase")) return { background: "#1976d2", border: "#1565c0" }
  if (labels.includes("RawMaterial")) return { background: "#2e7d32", border: "#1b5e20" }
  if (labels.includes("Country")) {
    if (colorRank === 'green') return { background: "#4caf50", border: "#388e3c" }
    if (colorRank === 'yellow') return { background: "#ff9800", border: "#f57c00" }
    if (colorRank === 'red') return { background: "#f44336", border: "#d32f2f" }
    // fallback to score-based
    const score = properties.composite_score || 0
    if (score >= 7.5) return { background: "#4caf50", border: "#388e3c" }
    if (score >= 7.0) return { background: "#ff9800", border: "#f57c00" }
    return { background: "#f44336", border: "#d32f2f" }
  }
  return { background: "#757575", border: "#424242" }
}
