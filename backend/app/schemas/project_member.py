from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut


class MemberAdd(BaseModel):
    user_id: int


class MemberOut(BaseModel):
    id: int
    user_id: int
    project_id: int
    added_at: datetime
    user: UserOut

    model_config = {"from_attributes": True}
