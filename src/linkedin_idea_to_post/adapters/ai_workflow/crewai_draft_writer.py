from __future__ import annotations

from typing import Any

from linkedin_idea_to_post.adapters.ai_workflow.prompt_helpers import (
    format_knowledge_examples,
    format_voice_examples,
)
from linkedin_idea_to_post.adapters.ai_workflow.writer_crew import WriterCrew
from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftGenerationError,
    DraftRequest,
    DraftWriter,
)


class CrewaiDraftWriter(DraftWriter):
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    def write(self, request: DraftRequest) -> Draft:
        inputs: dict[str, Any] = {
            "idea": request.idea,
            "voice_examples": format_voice_examples(request),
            "knowledge_examples": format_knowledge_examples(request),
            "target_word_count": request.context.target_word_count,
        }

        try:
            crew_output = WriterCrew(self.llm).crew().kickoff(inputs=inputs)
        except Exception as exc:
            raise DraftGenerationError(f"Draft generation failed: {exc}") from exc

        content = (getattr(crew_output, "raw", "") or "").strip()
        if not content:
            raise DraftGenerationError(
                "The model returned an empty draft. Please try again."
            )

        return Draft(idea=request.idea, generated_content=content)
