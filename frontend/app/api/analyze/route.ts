import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

interface CreateProposalRequest {
  industry_context: string
  destination_country: string
  priority: string
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

    // Send to FastAPI /analyze endpoint
    const response = await fetch(`http://127.0.0.1:8000/api/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Add any authentication headers if needed
        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      body: JSON.stringify({
        industry_context: body.industry_context,
        destination_country: body.destination_country,
        priority: body.priority,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("FastAPI analyze error:", errorText)
      throw new Error(`FastAPI analyze failed with status: ${response.status}`)
    }

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("FastAPI did not return JSON response")
    }

    const data = await response.json()

    // Transform the response to match our frontend expectations
    const transformedData = {
      id: data._id || `${body.industry_context}-${body.destination_country}-${body.priority}-${Date.now()}`,
      industry: body.industry_context,
      destination: body.destination_country,
      priority: body.priority,
      status: "COMPLETED", // Since analyze endpoint processes immediately
      created: data.created ? new Date(data.created).toISOString().split("T")[0] : new Date().toISOString().split("T")[0],
      // Include the full analysis data for potential future use
      analysis_data: data,
    }

    return NextResponse.json(transformedData, { status: 201 })
  } catch (error) {
    console.error("Error calling FastAPI analyze endpoint:", error)

    // Return error response
    return NextResponse.json(
      {
        error: "Failed to analyze proposal",
        details: error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 },
    )
  }
}
