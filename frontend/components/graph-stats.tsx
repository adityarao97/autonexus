"use client"
import { Grid, Card, CardContent, Typography, Box, Avatar, Skeleton } from "@mui/material"
import { Factory, Inventory, Public, TrendingUp } from "@mui/icons-material"
import type { GraphStats as GraphStatsType } from "@/types/neo4j"

interface GraphStatsProps {
  stats?: GraphStatsType | null
  loading?: boolean
}

export function GraphStats({ stats, loading = false }: GraphStatsProps) {
  const getStatValue = (key: string) => {
    if (loading || !stats) return "..."

    switch (key) {
      case "useCases":
        return stats.labelCounts["UseCase"] || 0
      case "rawMaterials":
        return stats.labelCounts["RawMaterial"] || 0
      case "countries":
        return stats.labelCounts["Country"] || 0
      case "relationships":
        return stats.relationshipCount || 0
      default:
        return 0
    }
  }

  const statsConfig = [
    {
      title: "Use Cases",
      key: "useCases",
      description: "Manufacturing processes",
      icon: Factory,
      color: "#1976d2",
    },
    {
      title: "Raw Materials",
      key: "rawMaterials",
      description: "Required ingredients",
      icon: Inventory,
      color: "#2e7d32",
    },
    {
      title: "Countries",
      key: "countries",
      description: "Supplier nations",
      icon: Public,
      color: "#9c27b0",
    },
    {
      title: "Relationships",
      key: "relationships",
      description: "Supply connections",
      icon: TrendingUp,
      color: "#ed6c02",
    },
  ]

  return (
    <Grid container spacing={2}>
      {statsConfig.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={stat.title}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                <Avatar sx={{ bgcolor: stat.color, width: 40, height: 40 }}>
                  <stat.icon />
                </Avatar>
                <Typography variant="caption" color="text.secondary">
                  #{index + 1}
                </Typography>
              </Box>
              {loading ? (
                <Skeleton variant="text" width="60%" height={40} />
              ) : (
                <Typography variant="h4" component="div" sx={{ fontWeight: "bold", mb: 0.5 }}>
                  {getStatValue(stat.key)}
                </Typography>
              )}
              <Typography variant="h6" color="text.primary" sx={{ mb: 0.5 }}>
                {stat.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stat.description}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}
