"use client"

import { useState, useEffect } from "react"
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert,
  IconButton,
} from "@mui/material"
import {
  Factory as FactoryIcon,
  Visibility,
  Add,
  Close,
  PlayArrow,
  CheckCircle,
  Schedule,
  Error as ErrorIcon,
} from "@mui/icons-material"
import Link from "next/link"

interface BusinessProposal {
  id: string
  industry_context: string
  destination_country: string
  priority: string
  status: "COMPLETED" | "processing" | "failed"
  created_at: string
  processed_at?: string
  node_count?: number
  relationship_count?: number
}

interface CreateProposalForm {
  industry_context: string
  destination_country: string
  priority: string
}

export default function HomePage() {
  const [proposals, setProposals] = useState<BusinessProposal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [formData, setFormData] = useState<CreateProposalForm>({
    industry_context: "",
    destination_country: "",
    priority: "",
  })

  useEffect(() => {
    // Simulate API call
    const fetchProposals = async () => {
      try {
        setLoading(true)
        // Replace with actual API call
        const response = await fetch("/api/proposals")
        const data = await response.json()

        // Simulate delay
        await new Promise((resolve) => setTimeout(resolve, 1000))
        setProposals(data)
      } catch (err) {
        setError("Failed to fetch proposals")
      } finally {
        setLoading(false)
      }
    }

    fetchProposals()
  }, [])

  const handleCreateProposal = async () => {
    try {
      setProcessing(true)

      // Create proposal API call
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error("Failed to create proposal")
      }

      const newProposal = await response.json()

      // Add to proposals list
      setProposals((prev) => [newProposal, ...prev])

      // Reset form and close dialog
      setFormData({
        industry_context: "",
        destination_country: "",
        priority: "",
      })
      setCreateDialogOpen(false)
    } catch (err) {
      setError("Failed to create proposal")
    } finally {
      setProcessing(false)
    }
  }

  const getStatusIcon = (status: BusinessProposal["status"]) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle color="success" />
      case "processing":
        return <Schedule color="warning" />
      case "failed":
        return <ErrorIcon color="error" />
    }
  }

  const getStatusColor = (status: BusinessProposal["status"]) => {
    switch (status) {
      case "COMPLETED":
        return "success"
      case "processing":
        return "warning"
      case "failed":
        return "error"
      default:
        return "default"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: "100vh", bgcolor: "background.default" }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <FactoryIcon sx={{ fontSize: 48, color: "primary.main" }} />
            <Box>
              <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
                Supply Chain Analyzer
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Business proposal processing and supply chain visualization
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            size="large"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ px: 4, py: 1.5 }}
          >
            Create Proposal
          </Button>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "success.main" }}>
                  {proposals.filter((p) => p.status === "COMPLETED").length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed Proposals
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "warning.main" }}>
                  {proposals.filter((p) => p.status === "processing").length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Processing
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "error.main" }}>
                  {proposals.filter((p) => p.status === "failed").length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "primary.main" }}>
                  {proposals.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Proposals
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Proposals Table */}
        <Card>
          <CardContent>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
              Business Proposals
            </Typography>

            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Industry</TableCell>
                      <TableCell>Destination</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {proposals.length === 0 ? (
                      <TableRow key="no-proposals">
                        <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                          <Typography variant="body2" color="text.secondary">
                            No proposals found. Create your first proposal to get started.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      proposals.map((proposal, index) => (
                        <TableRow key={`${proposal.id}-${index}`} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 600, textTransform: "capitalize" }}>
                              {proposal.industry_context}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{proposal.destination_country}</Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={proposal.priority.replace("_", " ")}
                              size="small"
                              variant="outlined"
                              sx={{ textTransform: "capitalize" }}
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              {getStatusIcon(proposal.status)}
                              <Chip
                                label={proposal.status}
                                size="small"
                                color={getStatusColor(proposal.status)}
                                sx={{ textTransform: "capitalize" }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(proposal.created)}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            {proposal.status === "COMPLETED" ? (
                              <Link href={`/${proposal._id}/graph_vizualize`} passHref>
                                <Button variant="outlined" size="small" startIcon={<Visibility />}>
                                  View
                                </Button>
                              </Link>
                            ) : (
                              <Button variant="outlined" size="small" disabled color="inherit">
                                {proposal.status === "processing" ? "Processing..." : "Failed"}
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Create Proposal Dialog */}
        <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            Create New Business Proposal
            <IconButton onClick={() => setCreateDialogOpen(false)}>
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 3, pt: 2 }}>
              <TextField
                label="Industry Context"
                value={formData.industry_context}
                onChange={(e) => setFormData((prev) => ({ ...prev, industry_context: e.target.value }))}
                placeholder="e.g., chocolate, automotive, electronics"
                fullWidth
                required
              />

              <FormControl fullWidth required>
                <InputLabel>Destination Country</InputLabel>
                <Select
                  value={formData.destination_country}
                  label="Destination Country"
                  onChange={(e) => setFormData((prev) => ({ ...prev, destination_country: e.target.value }))}
                >
                  <MenuItem value="USA">United States</MenuItem>
                  <MenuItem value="Germany">Germany</MenuItem>
                  <MenuItem value="Japan">Japan</MenuItem>
                  <MenuItem value="China">China</MenuItem>
                  <MenuItem value="India">India</MenuItem>
                  <MenuItem value="Brazil">Brazil</MenuItem>
                  <MenuItem value="UK">United Kingdom</MenuItem>
                  <MenuItem value="France">France</MenuItem>
                  <MenuItem value="Canada">Canada</MenuItem>
                  <MenuItem value="Australia">Australia</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth required>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  label="Priority"
                  onChange={(e) => setFormData((prev) => ({ ...prev, priority: e.target.value }))}
                >
                  <MenuItem value="profitability">Profitability</MenuItem>
                  <MenuItem value="stability">Supply Stability</MenuItem>
                  <MenuItem value="eco-friendly">Eco-Friendly</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setCreateDialogOpen(false)} disabled={processing}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleCreateProposal}
              disabled={processing || !formData.industry_context || !formData.destination_country || !formData.priority}
              startIcon={processing ? <CircularProgress size={16} /> : <PlayArrow />}
            >
              {processing ? "Processing..." : "Process"}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  )
}
