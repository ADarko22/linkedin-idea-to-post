from enum import StrEnum
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from linkedin_idea_to_post.domain.post import Post


class VoiceTuning(StrEnum):
    MATCH_STYLE = "MATCH_STYLE"
    MORE_CONCISE = "MORE_CONCISE"
    MORE_EXPANDED = "MORE_EXPANDED"
    PUNCHY_HOOK_ONLY = "PUNCHY_HOOK_ONLY"

    @property
    def instruction(self) -> str:
        match self:
            case VoiceTuning.MATCH_STYLE:
                return "Follow its tone, pacing, and structure closely."
            case VoiceTuning.MORE_CONCISE:
                return "Adopt the voice and tone, but tighten sentences and cut fluff."
            case VoiceTuning.MORE_EXPANDED:
                return (
                    "Keep the voice, but unpack points with a bit more room and detail."
                )
            case VoiceTuning.PUNCHY_HOOK_ONLY:
                return "Borrow the opening rhythm or cadence while letting the rest of the post flow naturally."


class KnowledgeStance(StrEnum):
    SUPPORTIVE = "SUPPORTIVE"
    CONTRARY = "CONTRARY"
    NEUTRAL = "NEUTRAL"
    EVOLVED_VIEW = "EVOLVED_VIEW"

    @property
    def instruction(self) -> str:
        match self:
            case KnowledgeStance.SUPPORTIVE:
                return "Build upon and reinforce the points or angle in that post."
            case KnowledgeStance.CONTRARY:
                return "Challenge, push back on, or offer a counter-perspective to that post."
            case KnowledgeStance.NEUTRAL:
                return "Treat it purely as factual or historical background or context ithout taking sides or arguing against it."
            case KnowledgeStance.EVOLVED_VIEW:
                return "Acknowledge the earlier post as a past take and show how your thinking has shifted since then."


class VoiceSelection(BaseModel):
    post_id: UUID
    tuning: VoiceTuning = VoiceTuning.MATCH_STYLE


class KnowledgeSelection(BaseModel):
    post_id: UUID
    stance: KnowledgeStance = KnowledgeStance.NEUTRAL


class DraftContext(BaseModel):
    relevant_posts: dict[UUID, Post] = Field(default_factory=dict)
    voice_selections: list[VoiceSelection] = Field(default_factory=list)
    knowledge_selections: list[KnowledgeSelection] = Field(default_factory=list)
    target_word_count: int = Field(default_factory=int)


class DraftRequest(BaseModel):
    idea: str
    context: DraftContext = Field(default_factory=DraftContext)


class Draft(BaseModel):
    idea: str
    generated_content: str

class DraftGenerationError(RuntimeError):
    """Raised when drafting fails due to LLM API, network, or output errors."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.retryable = retryable

class DraftWriter(Protocol):
    def write(self, request: DraftRequest) -> Draft: ...
