from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, field_validator


class UtcAwareBaseModel(BaseModel):
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def convert_all_to_utc(cls, value: datetime) -> datetime:
        # This runs sequentially for each field listed above
        return value.astimezone(UTC)


class PostStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class PostOrigin(StrEnum):
    HUMAN = "HUMAN"
    AI_DRAFT = "AI_DRAFT"
    AI_EDIT = "AI_EDIT"


class Post(UtcAwareBaseModel):
    id: UUID
    url: str | None
    title: str
    body: str
    topics: set[str]
    origin: PostOrigin
    status: PostStatus


class PostEmbedding(UtcAwareBaseModel):
    post_id: UUID
    embedding_model: str
    dimensions: int
    vector: list[float]


class ScoredPost(BaseModel):
    post: Post
    score: float
