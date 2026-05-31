from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    deadline: Optional[datetime] = None
    project_id: int
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    deadline: Optional[datetime]
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
    assignee: Optional[UserOut]

    model_config = {"from_attributes": True}
