from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, BusinessRequest
from schemas import BusinessRequestCreate, BusinessRequestOut

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/business_request/", response_model=BusinessRequestOut)
def create_business_request(req: BusinessRequestCreate, db: Session = Depends(get_db)):
    db_req = BusinessRequest(**req.dict())
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req