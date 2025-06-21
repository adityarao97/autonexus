"use client"
import { Grid, Card, CardContent, Typography, Box, Avatar } from "@mui/material"
import { AccountTree, People, Business, Computer, StarRate } from "@mui/icons-material"

export function GraphStats() {
  const stats = [
    {
      title: "Nodes",
      value: "8",
      description: "Total entities",
      icon: AccountTree,
      color: "#1976d2",
    },
    {
      title: "People",
      value: "2",
      description: "Individual profiles",
      icon: People,
      color: "#2e7d32",
    },
    {
      title: "Companies",
      value: "2",
      description: "Organizations",
      icon: Business,
      color: "#9c27b0",
    },
    {
      title: "Technologies",
      value: "3",
      description: "Tools & platforms",
      icon: Computer,
      color: "#ed6c02",
    },
    {
      title: "Relationships",
      value: "7",
      description: "Total connections",
      icon: StarRate,
      color: "#d32f2f",
    },
  ]

  return (
    <Grid container spacing={2}>
      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={2.4} key={stat.title}>
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
              <Typography variant="h4" component="div" sx={{ fontWeight: "bold", mb: 0.5 }}>
                {stat.value}
              </Typography>
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
