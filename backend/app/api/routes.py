from fastapi import APIRouter, Depends
from app.models.user import User, UserCreate
from app.dependencies.db import get_db
from pydantic import BaseModel
from typing import List, Dict, Any

from ..util.helper import fetch_neo4j_nodes_relationships


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


router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db=Depends(get_db)):
    # Dummy user creation
    return User(id=1, name=user.name, email=user.email)

@router.get("/neo4j/nodes", response_model=List[Node])
def get_nodes():
    filepath = "/home/rnrnattoji/hackathon/autonexus/backend/comprehensive_sourcing_analysis_chocolate_manufacturing_USA_20250621_214030.json"
    neo4jNodes, neo4jRelationships = fetch_neo4j_nodes_relationships(filepath)
    return neo4jNodes

@router.get("/neo4j/relationships", response_model=List[Relationship])
def get_relationships():
    filepath = "/home/rnrnattoji/hackathon/autonexus/backend/comprehensive_sourcing_analysis_chocolate_manufacturing_USA_20250621_214030.json"
    neo4jNodes, neo4jRelationships = fetch_neo4j_nodes_relationships(filepath)
    return neo4jRelationships
