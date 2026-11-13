from typing import Protocol

from pydantic import BaseModel


class DraftRequest(BaseModel):
    """
    The user request for drafting a LinkedIn post from an idea.
    """

    idea: str
    voice_examples: list[str]


class Draft(BaseModel):
    """
    The generated draft of a LinkedIn post from an idea.
    """

    body: str


class DraftWriter(Protocol):
    """
    The drafting writer interface.
    """

    def write(self, request: DraftRequest) -> Draft: ...
