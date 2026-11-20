from enum import StrEnum
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from linkedin_idea_to_post.domain.post import Post


class VoiceTuning(StrEnum):
    # follow its tone, pacing, and structure closely
    MATCH_STYLE = "MATCH_STYLE"
    # adopt the voice/tone, but tighten sentences and cut fluff
    MORE_CONCISE = "MORE_CONCISE"
    # keep the voice, but unpack points with a bit more room/detail
    MORE_EXPANDED = "MORE_EXPANDED"
    # borrow the opening rhythm/cadence while letting the rest of the post flow naturally.
    PUNCHY_HOOK_ONLY = "PUNCHY_HOOK_ONLY"


class KnowledgeStance(StrEnum):
    # build upon and reinforce the points/angle in that post
    SUPPORTIVE = "SUPPORTIVE"
    # challenge, push back on, or offer a counter-perspective to that post
    CONTRARY = "CONTRARY"
    # treat it purely as factual/historical background or context without taking sides or arguing against it
    NEUTRAL = "NEUTRAL"
    # acknowledge the earlier post as a past take and show how your thinking has shifted since then
    EVOLVED_VIEW = "EVOLVED_VIEW"


class VoiceSelection(BaseModel):
    post_id: UUID
    tuning: VoiceTuning = VoiceTuning.MATCH_STYLE


class KnowledgeSelection(BaseModel):
    post_id: UUID
    stance: KnowledgeStance = KnowledgeStance.NEUTRAL


class DraftContext(BaseModel):
    voice_selections: list[VoiceSelection] = Field(default_factory=list)
    knowledge_selections: list[KnowledgeSelection] = Field(default_factory=list)


class DraftRequest(BaseModel):
    idea: str
    relevant_posts: dict[UUID, Post] = Field(default_factory=dict)
    context: DraftContext = Field(default_factory=DraftContext)


class Draft(BaseModel):
    idea: str
    generated_content: str


class DraftWriter(Protocol):
    def write(self, request: DraftRequest) -> Draft: ...
