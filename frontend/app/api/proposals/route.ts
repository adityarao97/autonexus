import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

interface CreateProposalRequest {
  industry_context: string
  destination_country: string
  priority: string
}

export async function GET() {
  try {

    // Fetch proposals from FastAPI backend
    const response = await fetch(`http://127.0.0.1:8000/api/proposals`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Add any authentication headers if needed
        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      // next: { revalidate: 30 }, // Revalidate every 30 seconds
    })

    if (!response.ok) {
      throw new Error(`FastAPI responded with status: ${response.status}`)
    }

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("FastAPI did not return JSON response")
    }

    const data = await response.json()

    // Assuming FastAPI returns array of proposals or { proposals: [...] }
    const proposals = Array.isArray(data) ? data : data.proposals || []

    return NextResponse.json(proposals)
  } catch (error) {
    console.error("Error fetching proposals from FastAPI:", error)
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: CreateProposalRequest = await request.json()

    // Validate required fields
    if (!body.industry_context || !body.destination_country || !body.priority) {
      return NextResponse.json(
        { error: "Missing required fields: industry_context, destination_country, priority" },
        { status: 400 },
      )
    }

    // Check if FastAPI base URL is configured
    if (!process.env.FASTAPI_BASE_URL) {
      // Return mock response for development
      const mockProposal = {
        id: `${body.industry_context}-${body.destination_country}-${body.priority}-${Date.now()}`,
        industry: body.industry_context,
        destination: body.destination_country,
        priority: body.priority,
        status: "processing",
        created: new Date().toISOString().split("T")[0],
      }

      console.warn("FASTAPI_BASE_URL not configured, returning mock proposal")
      return NextResponse.json(mockProposal, { status: 201 })
    }

    // Send to FastAPI backend for processing
    const response = await fetch(`http://127.0.0.1:8000/api/proposals`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Add any authentication headers if needed
        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`FastAPI responded with status: ${response.status}`)
    }

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("FastAPI did not return JSON response")
    }

    const data = await response.json()
    return NextResponse.json(data, { status: 201 })
  } catch (error) {
    console.error("Error creating proposal:", error)

    // Return mock response as fallback
    const body: CreateProposalRequest = await request.json()
    const mockProposal = {
      id: `${body.industry_context}-${body.destination_country}-${body.priority}-${Date.now()}`,
      industry: body.industry_context,
      destination: body.destination_country,
      priority: body.priority,
      status: "processing",
      created: new Date().toISOString().split("T")[0],
    }

    console.warn("Falling back to mock proposal due to FastAPI connection error")
    return NextResponse.json(mockProposal, { status: 201 })
  }
}
