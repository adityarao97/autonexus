import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// This would typically connect to your actual Neo4j database
// For now, I'll return the data you provided
export async function GET(
  request: NextRequest, context: { params: Promise<{ id: string }> }
) {

  try {
    const { id } = await context.params
    // Fetch nodes from FastAPI backend
    const response = await fetch(`http://127.0.0.1:8000/api/neo4j/nodes/${id}`, {
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

    // Assuming FastAPI returns { nodes: [...] } or just [...]
    const nodes = Array.isArray(data) ? data : data.nodes

    return NextResponse.json({ nodes })
  } catch (error) {
    console.error("Error fetching nodes from FastAPI:", error)
    return NextResponse.json({ error: "Failed to fetch nodes from backend" }, { status: 500 })
  }
}
