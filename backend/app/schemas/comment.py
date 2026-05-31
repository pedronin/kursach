from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut


class CommentCreate(BaseModel):
    text: str


class CommentOut(BaseModel):
    id: int
    text: str
    task_id: int
    author_id: int
    created_at: datetime
    author: UserOut

    model_config = {"from_attributes": True}
