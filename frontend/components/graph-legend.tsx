"use client"
import { Card, CardContent, Typography, Box, Chip, Paper } from "@mui/material"

export function GraphLegend() {
  const legendItems = [
    {
      label: ":Person",
      color: "#1976d2",
      shape: "circle",
      description: "Individual",
    },
    {
      label: ":Company",
      color: "#2e7d32",
      shape: "square",
      description: "Organization",
    },
    {
      label: ":Technology",
      color: "#9c27b0",
      shape: "diamond",
      description: "Tool",
    },
    {
      label: ":Skill",
      color: "#ed6c02",
      shape: "triangle",
      description: "Capability",
    },
  ]

  const getShapeStyle = (shape: string, color: string) => {
    const baseStyle = {
      width: 20,
      height: 20,
      backgroundColor: color,
    }

    switch (shape) {
      case "circle":
        return { ...baseStyle, borderRadius: "50%" }
      case "square":
        return { ...baseStyle, borderRadius: 2 }
      case "diamond":
        return { ...baseStyle, transform: "rotate(45deg)", borderRadius: 2 }
      case "triangle":
        return {
          width: 0,
          height: 0,
          borderLeft: "10px solid transparent",
          borderRight: "10px solid transparent",
          borderBottom: `15px solid ${color}`,
          backgroundColor: "transparent",
        }
      default:
        return baseStyle
    }
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
          Graph Legend
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Node types and their visual representations
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {legendItems.map((item) => (
            <Paper
              key={item.label}
              sx={{
                p: 2,
                display: "flex",
                alignItems: "center",
                gap: 2,
                transition: "all 0.2s ease-in-out",
                "&:hover": {
                  transform: "translateY(-1px)",
                  boxShadow: 2,
                },
              }}
            >
              <Box
                sx={{
                  ...getShapeStyle(item.shape, item.color),
                  flexShrink: 0,
                }}
              />
              <Typography variant="body2" sx={{ fontWeight: 600, flexGrow: 1 }}>
                {item.label}
              </Typography>
              <Chip label={item.description} size="small" variant="outlined" />
            </Paper>
          ))}
        </Box>
      </CardContent>
    </Card>
  )
}
