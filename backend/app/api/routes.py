from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User, UserCreate
from app.dependencies.db import get_db
from pydantic import BaseModel
from typing import List, Dict, Any

from ..db.mongodb import data_collection
from ..util.helper import fetch_neo4j_nodes_relationships
from ..util.workflow_orchestrator import analyze_industry_sourcing

router = APIRouter()

class SourcingRequest(BaseModel):
    industry_context: str
    destination_country: str = "USA"
    priority: str = "balanced"  # "profitability", "stability", "eco-friendly", "balanced"

class Node(BaseModel):
    id: str
    labels: List[str]
    properties: Dict[str, Any]

class Relationship(BaseModel):
    id: str
    startNodeId: str
    endNodeId: str
    type: str
    properties: Dict[str, Any]

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db=Depends(get_db)):
    # Dummy user creation
    return User(id=1, name=user.name, email=user.email)

@router.get("/proposals")
def proposals():
    data = []
    rec_cursor = data_collection.find({})
    for rec in rec_cursor:
        rec["_id"] = str(rec["_id"])
        data.append(rec)

    return data

@router.post("/analyze")
async def analyze(request: SourcingRequest):
    config = {"priority": request.priority}
    try:
        data = await analyze_industry_sourcing(
            industry_context=request.industry_context,
            destination_country=request.destination_country,
            config=config
        )
        data["priority"] = request.priority
        data["created"] = datetime.utcnow()

        rec = data_collection.insert_one(data)
        data["_id"] = str(rec.inserted_id)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/neo4j/nodes/{id}", response_model=List[Node])
def get_nodes(id: str):

    rec = data_collection.find_one({"_id": ObjectId(id)})
    neo4jNodes, neo4jRelationships = fetch_neo4j_nodes_relationships(rec)

    return neo4jNodes

@router.get("/neo4j/relationships/{id}", response_model=List[Relationship])
def get_relationships(id: str):

    rec = data_collection.find_one({"_id": ObjectId(id)})
    neo4jNodes, neo4jRelationships = fetch_neo4j_nodes_relationships(rec)

    return neo4jRelationships
