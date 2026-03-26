from pydantic import BaseModel, ConfigDict, Field
from fastapi_users import schemas
import uuid
from datetime import datetime


# ------------------ COMMENT ------------------
class CommentResponse(BaseModel):
    content: str

    model_config = ConfigDict(from_attributes=True)


# ------------------ POST ------------------
class PostCreate(BaseModel):
    caption: str = Field(min_length=1, max_length=200)


class PostResponse(BaseModel):
    id: str
    user_id: str
    caption: str | None
    url: str
    file_type: str
    file_name: str
    created_at: datetime
    comments: list[CommentResponse] = []
    likes: int = 0

    model_config = ConfigDict(from_attributes=True)


# ------------------ USER ------------------
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass