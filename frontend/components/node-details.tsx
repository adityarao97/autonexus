"use client"
import { Card, CardContent, Typography, Box, Chip, Paper } from "@mui/material"
import { Storage as StorageIcon } from "@mui/icons-material"

interface NodeDetailsProps {
  selectedNode: any
}

export function NodeDetails({ selectedNode }: NodeDetailsProps) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <StorageIcon color="primary" />
          <Typography variant="h6" component="h3">
            Node Inspector
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {selectedNode ? "Exploring node properties and relationships" : "Click on a node to inspect its details"}
        </Typography>

        {selectedNode ? (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <Paper sx={{ p: 2, bgcolor: "grey.50" }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Node ID
              </Typography>
              <Typography
                variant="body2"
                sx={{ fontFamily: "monospace", bgcolor: "background.paper", p: 1, borderRadius: 1 }}
              >
                {selectedNode.id}
              </Typography>
            </Paper>

            <Paper sx={{ p: 2, bgcolor: "primary.50" }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Labels
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {selectedNode.labels?.map((label: string, index: number) => (
                  <Chip key={index} label={`:${label}`} color="primary" size="small" sx={{ fontFamily: "monospace" }} />
                ))}
              </Box>
            </Paper>

            <Paper sx={{ p: 2, bgcolor: "success.50" }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Properties
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {Object.entries(selectedNode.properties || {}).map(([key, value]) => (
                  <Box key={key}>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ textTransform: "uppercase", letterSpacing: 1 }}
                    >
                      {key}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ fontFamily: "monospace", bgcolor: "background.paper", p: 1, borderRadius: 1, mt: 0.5 }}
                    >
                      {String(value)}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Box>
        ) : (
          <Box sx={{ textAlign: "center", py: 6 }}>
            <StorageIcon sx={{ fontSize: 64, color: "text.disabled", mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Select a node to view its details
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
