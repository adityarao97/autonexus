from fastapi import APIRouter, Depends
from app.models.user import User, UserCreate
from app.dependencies.db import get_db

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db=Depends(get_db)):
    # Dummy user creation
    return User(id=1, name=user.name, email=user.email)
