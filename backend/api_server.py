from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn

from workflow_orchestrator import analyze_industry_sourcing

app = FastAPI(title="Raw Material Sourcing API")

class SourcingRequest(BaseModel):
    industry_context: str
    destination_country: str = "USA"
    priority: str = "balanced"  # "profitability", "stability", "eco-friendly", "balanced"

@app.post("/analyze")
async def analyze(request: SourcingRequest):
    config = {"priority": request.priority}
    try:
        results = await analyze_industry_sourcing(
            industry_context=request.industry_context,
            destination_country=request.destination_country,
            config=config
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: For running directly
if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)