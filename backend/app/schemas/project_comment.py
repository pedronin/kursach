from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut


class ProjectCommentCreate(BaseModel):
    text: str


class ProjectCommentOut(BaseModel):
    id: int
    text: str
    project_id: int
    author_id: int
    created_at: datetime
    author: UserOut

    model_config = {"from_attributes": True}
