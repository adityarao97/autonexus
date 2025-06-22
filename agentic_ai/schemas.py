from pydantic import BaseModel
from typing import List, Dict

class BusinessRequestCreate(BaseModel):
    priorities: Dict[str, float]
    product: str
    description: str
    scale: str
    budget: float
    location: str
    exclude_countries: List[str]

class BusinessRequestOut(BusinessRequestCreate):
    id: int

    class Config:
        orm_mode = True