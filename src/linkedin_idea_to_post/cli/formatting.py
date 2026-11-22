from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from linkedin_idea_to_post.config import AppConfig
from linkedin_idea_to_post.domain.post import Post


def _build_errors_table(
    title: str,
    border_style: str,
    rows: list[tuple[str, str, str, str]],
) -> Table:
    table = Table(
        title=f"[{border_style}]{title}[/{border_style}]",
        show_header=True,
        header_style=border_style,
    )
    table.add_column("Row", style="cyan", width=8, justify="right")
    table.add_column("Field", style="yellow", width=15)
    table.add_column("Error Code", style="magenta", width=22)
    table.add_column("Message", style="white")

    for row in rows:
        table.add_row(*row)
    return table


def render_config(console: Console, config: AppConfig) -> None:
    table = Table(
        title="[bold cyan]Application Configuration[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Section / Key", style="dim", width=20)
    table.add_column("Property", style="green")
    table.add_column("Value", style="yellow")

    for section_name, section_model in vars(config).items():
        items: Any = (
            section_model.model_dump().items()
            if hasattr(section_model, "model_dump")
            else vars(section_model).items()
        )
        for key, value in items:
            table.add_row(section_name, key, str(value))

    console.print(table)


def render_post_panel(
    console: Console,
    post: Post,
    *,
    title: str | None = None,
    border_style: str = "cyan",
) -> None:
    content = (
        f"[dim]ID: {post.id} | Origin: {post.origin} | Status: {post.status}[/dim]\n"
        f"[dim]Created: {post.created_at} | Updated: {post.updated_at}[/dim]\n\n"
        f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}"
    )
    console.print(Panel(content, title=title, border_style=border_style))


def render_dry_run_draft(console: Console, generated_content: str) -> None:
    content = f"[dim]{Text(generated_content)}[/dim]\n"
    console.print(Panel(content, title="Generated Draft", border_style="dim"))


def render_import_summary(console: Console, result: Any) -> None:
    summary_text = (
        f"[bold]Valid posts:[/bold] [green]{len(result.posts)}[/green]\n"
        f"[bold]Parsing errors:[/bold] [red]{len(result.parsing_errors)}[/red]\n"
        f"[bold]Mapping errors:[/bold] [red]{len(result.mapping_errors)}[/red]"
    )
    console.print(Panel(summary_text, title="Import Summary", border_style="blue"))


def render_import_errors(console: Console, result: Any) -> None:
    if result.parsing_errors:
        console.print()
        parsing_rows = [err.to_str_tuple() for err in result.parsing_errors]
        console.print(
            _build_errors_table("Parsing Errors", "bold yellow", parsing_rows)
        )

    if result.mapping_errors:
        console.print()
        mapping_rows = [
            (str(map_err.raw_post.row), *field_err.to_str_tuple())
            for map_err in result.mapping_errors
            for field_err in map_err.errors
        ]
        console.print(_build_errors_table("Mapping Errors", "bold red", mapping_rows))
