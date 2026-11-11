from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, field_validator


class PostStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class PostOrigin(StrEnum):
    HUMAN = "HUMAN"
    AI_DRAFT = "AI_DRAFT"
    AI_EDIT = "AI_EDIT"


class Post(BaseModel):
    id: UUID
    url: str
    title: str
    body: str
    topics: set[str]
    origin: PostOrigin
    status: PostStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def convert_all_to_utc(cls, value: datetime) -> datetime:
        # This runs sequentially for each field listed above
        return value.astimezone(UTC)

    # todo add a distinction of urls:
    #  - urn:li:share ->  legacy and simple share object: typically light updates on personal profile
    #  - urn:li:ugcPost -> user-generated-content, modern POST API: typically rich media & company posts
    #  REGEX to extract them re.compile(r"(?::|%3A)([a-zA-Z]+)(?::|%3A)")
