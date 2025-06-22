"use client"
import { Card, CardContent, Typography, Box, Chip, Paper } from "@mui/material"

export function GraphLegend() {
  const legendItems = [
    {
      label: ":UseCase",
      color: "#1976d2",
      shape: "star",
      description: "Manufacturing",
    },
    {
      label: ":RawMaterial",
      color: "#2e7d32",
      shape: "square",
      description: "Ingredients",
    },
    {
      label: ":Country (High Score)",
      color: "#4caf50",
      shape: "circle",
      description: "Score ≥ 7.5",
    },
    {
      label: ":Country (Medium Score)",
      color: "#ff9800",
      shape: "circle",
      description: "Score 7.0-7.5",
    },
    {
      label: ":Country (Low Score)",
      color: "#f44336",
      shape: "circle",
      description: "Score < 7.0",
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
      case "star":
        return {
          width: 0,
          height: 0,
          borderLeft: "10px solid transparent",
          borderRight: "10px solid transparent",
          borderBottom: `15px solid ${color}`,
          backgroundColor: "transparent",
          position: "relative" as const,
        }
      default:
        return baseStyle
    }
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
          Supply Chain Legend
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Node types and scoring system
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
              <Typography variant="body2" sx={{ fontWeight: 600, flexGrow: 1, fontSize: "0.8rem" }}>
                {item.label}
              </Typography>
              <Chip label={item.description} size="small" variant="outlined" />
            </Paper>
          ))}
        </Box>

        <Box sx={{ mt: 3, p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Relationship Types:
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Box sx={{ width: 20, height: 3, bgcolor: "#1976d2" }} />
              <Typography variant="body2">RAW MATERIALS</Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Box sx={{ width: 20, height: 3, bgcolor: "#2e7d32" }} />
              <Typography variant="body2">COUNTRY</Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}
