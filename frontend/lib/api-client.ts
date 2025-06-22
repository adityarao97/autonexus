// Optional: Create a centralized API client for FastAPI calls

interface ApiClientConfig {
  baseUrl: string
  timeout?: number
  headers?: Record<string, string>
}

class ApiClient {
  private baseUrl: string
  private timeout: number
  private defaultHeaders: Record<string, string>

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl
    this.timeout = config.timeout || 10000
    this.defaultHeaders = {
      "Content-Type": "application/json",
      ...config.headers,
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.defaultHeaders,
          ...options.headers,
        },
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      clearTimeout(timeoutId)

      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("Request timeout")
      }

      throw error
    }
  }

  async getNodes() {
    return this.request("/api/neo4j/nodes")
  }

  async getRelationships() {
    return this.request("/api/neo4j/relationships")
  }

  async getGraph() {
    return this.request("/api/neo4j/graph")
  }
}

// Create singleton instance
export const fastApiClient = new ApiClient({
  baseUrl: process.env.FASTAPI_BASE_URL || "http://localhost:8000",
  timeout: 15000,
  headers: {
    // Add authentication headers if needed
    // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
  },
})
