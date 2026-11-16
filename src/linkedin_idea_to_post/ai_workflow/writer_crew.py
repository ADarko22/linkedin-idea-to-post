from typing import Any, ClassVar, cast

from crewai import Agent, BaseLLM, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class WriterCrew:
    """A crew designed to load agents and tasks from YAML files."""

    # Explicitly type class-level config paths / injected dictionaries for Mypy
    agents_config: ClassVar[str | dict[str, Any]] = "config/agents.yaml"
    tasks_config: ClassVar[str | dict[str, Any]] = "config/tasks.yaml"

    def __init__(self, llm: BaseLLM) -> None:
        self._llm = llm

    @agent
    def writer(self) -> Agent:
        config = cast(dict[str, Any], self.agents_config)
        return Agent(config=config["writer"], verbose=True, llm=self._llm)

    @task
    def write_post(self) -> Task:
        config = cast(dict[str, Any], self.tasks_config)
        return Task(config=config["write_post"])  # type: ignore[call-arg]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.writer()],  # type: ignore[call-arg]
            tasks=[self.write_post()],  # type: ignore[call-arg]
            process=Process.sequential,
            verbose=True,
        )
