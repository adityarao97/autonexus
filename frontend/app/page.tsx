"use client"

import { useState } from "react"
import { Box, Container, Typography, Grid, Card, CardContent, AppBar, Toolbar, Chip, Avatar } from "@mui/material"
import { Storage as StorageIcon, NetworkCheck as NetworkIcon, FlashOn as FlashIcon } from "@mui/icons-material"
import { GraphVisualization } from "@/components/graph-visualization"
import { GraphControls } from "@/components/graph-controls"
import { GraphStats } from "@/components/graph-stats"
import { NodeDetails } from "@/components/node-details"
import { GraphLegend } from "@/components/graph-legend"

export default function Home() {
  const [selectedNode, setSelectedNode] = useState<any>(null)

  const handleReset = () => {
    setSelectedNode(null)
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
            <StorageIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 0.5 }}>
              Neo4j Graph Visualization
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Interactive network graph with real-time exploration
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Chip icon={<NetworkIcon />} label="Live Graph" color="primary" variant="filled" />
            <Chip icon={<FlashIcon />} label="Interactive" color="secondary" variant="outlined" />
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Stats Row */}
        <Box sx={{ mb: 4 }}>
          <GraphStats />
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
                        bgcolor: "success.main",
                        borderRadius: "50%",
                        animation: "pulse 2s infinite",
                        "@keyframes pulse": {
                          "0%": { opacity: 1 },
                          "50%": { opacity: 0.5 },
                          "100%": { opacity: 1 },
                        },
                      }}
                    />
                    <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                      Knowledge Graph
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Interactive visualization of connected data relationships
                  </Typography>
                </Box>
                <Box sx={{ position: "relative" }}>
                  <GraphVisualization onNodeSelect={setSelectedNode} />
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
