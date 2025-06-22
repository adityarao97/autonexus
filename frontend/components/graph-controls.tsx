"use client"

import { useState } from "react"
import { Card, CardContent, Typography, Button, Box, Chip, Grid, Divider } from "@mui/material"
import { ZoomIn, ZoomOut, Refresh, Download, PlayArrow, Pause, Settings } from "@mui/icons-material"

interface GraphControlsProps {
  onZoomIn?: () => void
  onZoomOut?: () => void
  onReset?: () => void
  onExport?: () => void
}

export function GraphControls({ onZoomIn, onZoomOut, onReset, onExport }: GraphControlsProps) {
  const [isPhysicsEnabled, setIsPhysicsEnabled] = useState(true)

  const handleZoomIn = () => {
    const network = (window as any).networkInstance
    if (network) {
      const scale = network.getScale()
      network.moveTo({ scale: scale * 1.2 })
    }
    onZoomIn?.()
  }

  const handleZoomOut = () => {
    const network = (window as any).networkInstance
    if (network) {
      const scale = network.getScale()
      network.moveTo({ scale: scale * 0.8 })
    }
    onZoomOut?.()
  }

  const handleReset = () => {
    const network = (window as any).networkInstance
    if (network) {
      network.fit()
    }
    onReset?.()
  }

  const handleTogglePhysics = () => {
    const network = (window as any).networkInstance
    if (network) {
      network.setOptions({ physics: { enabled: !isPhysicsEnabled } })
      setIsPhysicsEnabled(!isPhysicsEnabled)
    }
  }

  const handleExport = () => {
    const network = (window as any).networkInstance
    if (network) {
      const canvas = network.canvas.frame.canvas
      const link = document.createElement("a")
      link.download = "neo4j-graph.png"
      link.href = canvas.toDataURL()
      link.click()
    }
    onExport?.()
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Settings color="primary" />
            <Typography variant="h6" component="h3">
              Graph Controls
            </Typography>
          </Box>
          <Chip
            label={isPhysicsEnabled ? "Dynamic" : "Static"}
            color={isPhysicsEnabled ? "primary" : "default"}
            size="small"
          />
        </Box>

        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Button variant="outlined" fullWidth startIcon={<ZoomIn />} onClick={handleZoomIn} size="small">
              Zoom In
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button variant="outlined" fullWidth startIcon={<ZoomOut />} onClick={handleZoomOut} size="small">
              Zoom Out
            </Button>
          </Grid>
        </Grid>

        <Button variant="outlined" fullWidth startIcon={<Refresh />} onClick={handleReset} sx={{ mb: 2 }} size="small">
          Fit to Screen
        </Button>

        <Button
          variant={isPhysicsEnabled ? "contained" : "outlined"}
          fullWidth
          startIcon={isPhysicsEnabled ? <Pause /> : <PlayArrow />}
          onClick={handleTogglePhysics}
          sx={{ mb: 2 }}
          size="small"
        >
          {isPhysicsEnabled ? "Stop Physics" : "Start Physics"}
        </Button>

        <Divider sx={{ my: 2 }} />

        <Button
          variant="outlined"
          fullWidth
          startIcon={<Download />}
          onClick={handleExport}
          color="success"
          size="small"
        >
          Export PNG
        </Button>
      </CardContent>
    </Card>
  )
}
