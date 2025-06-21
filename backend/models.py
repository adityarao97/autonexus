from sqlalchemy import Column, Integer, String, Text, Float, JSON
from database import Base

class BusinessRequest(Base):
    __tablename__ = "business_requests"

    id = Column(Integer, primary_key=True, index=True)
    priorities = Column(JSON)  # e.g., {"profitability": 0.6, "eco_friendly": 0.4}
    description = Column(Text)
    product = Column(String(100))
    scale = Column(String(50))
    budget = Column(Float)
    location = Column(String(100))
    exclude_countries = Column(JSON)  # list of strings
    