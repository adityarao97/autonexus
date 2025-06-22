import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"


export async function GET(
  request: NextRequest, context: { params: Promise<{ id: string }> }
) {
  try {

    const { id } = await context.params
    // Fetch relationships from FastAPI backend
    const response = await fetch(`http://127.0.0.1:8000/api/neo4j/relationships/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Add any authentication headers if needed
        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      // Add cache control if needed
      next: { revalidate: 60 }, // Revalidate every 60 seconds
    })

    if (!response.ok) {
      throw new Error(`FastAPI responded with status: ${response.status}`)
    }

    const data = await response.json()

    // Assuming FastAPI returns { relationships: [...] } or just [...]
    const relationships = Array.isArray(data) ? data : data.relationships

    return NextResponse.json({ relationships })
  } catch (error) {
    console.error("Error fetching relationships from FastAPI:", error)
    return NextResponse.json({ error: "Failed to fetch relationships from backend" }, { status: 500 })
  }
}
