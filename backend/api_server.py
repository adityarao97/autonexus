from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn

from workflow_orchestrator import analyze_industry_sourcing

app = FastAPI(title="Raw Material Sourcing API")

# Optional: For running directly
if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)