from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    owner: UserOut

    model_config = {"from_attributes": True}
