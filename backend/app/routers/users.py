from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()
