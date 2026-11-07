from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class PostStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"


class PostOrigin(StrEnum):
    HUMAN = "HUMAN"
    AI_DRAFT = "AI_DRAFT"
    AI_EDIT = "AI_EDIT"


class Post(BaseModel):
    id: UUID
    title: str
    body: str
    topics: set[str]
    origin: PostOrigin
    status: PostStatus
    created_at: datetime
    updated_at: datetime
