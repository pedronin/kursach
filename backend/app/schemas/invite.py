from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut


class InviteCreate(BaseModel):
    username: str


class InviteOut(BaseModel):
    id: int
    project_id: int
    status: str
    created_at: datetime
    inviter: UserOut
    invitee: UserOut
    project_title: str = ""

    model_config = {"from_attributes": True}
