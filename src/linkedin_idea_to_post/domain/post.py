from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class PostStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"


class PostOrigin(StrEnum):
    HUMAN = "human"
    AI_DRAFT = "ai_draft"
    AI_EDIT = "ai_edit"


class Post(BaseModel):
    created_at: datetime
    title: str
    body: str
    topics: list[str]
    origin: PostOrigin
    status: PostStatus
    
