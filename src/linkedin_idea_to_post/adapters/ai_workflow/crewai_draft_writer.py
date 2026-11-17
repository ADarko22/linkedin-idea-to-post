from typing import cast

from crewai import CrewOutput

from linkedin_idea_to_post.adapters.ai_workflow.prompt_helpers import (
    format_voice_examples,
)
from linkedin_idea_to_post.adapters.ai_workflow.writer_crew import WriterCrew
from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class CrewaiDraftWriter(DraftWriter):
    def __init__(self, llm):
        self.llm = llm

    def write(self, request: DraftRequest) -> Draft:
        output = (
            WriterCrew(self.llm)
            .crew()
            .kickoff(
                inputs={
                    "idea": request.idea,
                    "voice_examples": format_voice_examples(request.voice_examples),
                }
            )
        )
        crew_output = cast(CrewOutput, output)
        return Draft(body=crew_output.raw)
