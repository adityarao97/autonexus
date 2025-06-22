"use client"

import { use, useState } from "react"
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Chip,
  Avatar,
  Alert,
  Button,
} from "@mui/material"
import { Factory as FactoryIcon, NetworkCheck as NetworkIcon, FlashOn as FlashIcon, Refresh } from "@mui/icons-material"
import { GraphVisualization } from "@/components/graph-visualization"
import { GraphControls } from "@/components/graph-controls"
import { GraphStats } from "@/components/graph-stats"
import { NodeDetails } from "@/components/node-details"
import { GraphLegend } from "@/components/graph-legend"
import { useGraphData } from "@/hooks/use-graph-data"

interface PageProps {
  params: {
    id: string
  }
}

export default function GraphVisualizePage({ params }: PageProps) {
  const { id } = use(params) // Use React.use() to unwrap the Promise
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const { data, loading, error, refetch } = useGraphData(id) // Pass id to hook

  const handleReset = () => {
    setSelectedNode(null)
  }

  const handleRefresh = async () => {
    setSelectedNode(null)
    await refetch()
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Header */}
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: "background.paper", color: "text.primary" }}>
        <Toolbar sx={{ py: 2 }}>
          <Avatar
            sx={{
              bgcolor: "primary.main",
              mr: 2,
              width: 48,
              height: 48,
            }}
          >
            <FactoryIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 0.5 }}>
              Supply Chain Visualization - {id.toUpperCase()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Interactive visualization of raw material sourcing and supplier relationships
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Chip
              icon={<NetworkIcon />}
              label={loading ? "Loading..." : "Supply Network"}
              color="primary"
              variant="filled"
            />
            <Chip icon={<FlashIcon />} label="Interactive" color="secondary" variant="outlined" />
            <Button variant="outlined" size="small" startIcon={<Refresh />} onClick={handleRefresh} disabled={loading}>
              Refresh
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Global Error Alert */}
        {error && (
          <Alert
            severity="error"
            sx={{ mb: 4 }}
            action={
              <Button color="inherit" size="small" onClick={handleRefresh} startIcon={<Refresh />}>
                Retry
              </Button>
            }
          >
            Failed to load supply chain data: {error}
          </Alert>
        )}

        {/* Stats Row */}
        <Box sx={{ mb: 4 }}>
          <GraphStats stats={data?.stats} loading={loading} />
        </Box>

        {/* Main Content */}
        <Grid container spacing={3}>
          {/* Graph Visualization */}
          <Grid item xs={12} lg={8}>
            <Card sx={{ height: "100%" }}>
              <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                <Box sx={{ p: 3, borderBottom: 1, borderColor: "divider" }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        bgcolor: loading ? "grey.400" : "success.main",
                        borderRadius: "50%",
                        animation: loading ? "none" : "pulse 2s infinite",
                        "@keyframes pulse": {
                          "0%": { opacity: 1 },
                          "50%": { opacity: 0.5 },
                          "100%": { opacity: 1 },
                        },
                      }}
                    />
                    <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                      Supply Chain Network
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {loading
                      ? "Loading chocolate manufacturing supply chain data..."
                      : "Chocolate manufacturing raw material sourcing and supplier scoring visualization"}
                  </Typography>
                </Box>
                <Box sx={{ position: "relative" }}>
                  <GraphVisualization
                    nodes={data?.nodes || []}
                    relationships={data?.relationships || []}
                    loading={loading}
                    error={error}
                    onNodeSelect={setSelectedNode}
                    onRefresh={handleRefresh}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} lg={4}>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {/* Controls */}
              <GraphControls onReset={handleReset} />

              {/* Node Details */}
              <NodeDetails selectedNode={selectedNode} />

              {/* Legend */}
              <GraphLegend />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}
