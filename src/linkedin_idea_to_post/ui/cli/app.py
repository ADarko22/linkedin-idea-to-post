from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import click
from click.exceptions import Exit
from rich.console import Console
from rich.panel import Panel

from linkedin_idea_to_post.app_context import AppContext, build_app_context
from linkedin_idea_to_post.config import ConfigurationError
from linkedin_idea_to_post.domain.drafting import DraftRequest
from linkedin_idea_to_post.domain.post_helpers import post_from_draft
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.cli.formatting import (
    render_config,
    render_dry_run_draft,
    render_import_errors,
    render_import_summary,
    render_post_panel,
)

console = Console()


@contextmanager
def _app_context(*, offline: bool = False) -> Iterator[AppContext]:
    try:
        ctx = build_app_context(offline=offline)
    except ConfigurationError as exc:
        _handle_config_error(exc)
        raise AssertionError("unreachable") from exc

    try:
        yield ctx
    finally:
        ctx.close()


def _handle_config_error(exc: ConfigurationError) -> None:
    console.print(f"[bold red]Configuration error:[/bold red] {exc}")
    if exc.hint:
        console.print(f"[dim]Hint: {exc.hint}[/dim]")
    raise Exit(code=1) from exc


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Import LinkedIn shares and turn ideas into new posts."""


@cli.command("show-config")
def show_config() -> None:
    """Show content of AppConfig."""
    with _app_context() as app:
        render_config(console, app.config)


@cli.command("draft")
@click.argument(
    "idea",
    type=str,
    required=True,
    help="The user's prompt.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Only drafts the content of the post, without saving to storage.",
)
@click.option(
    "--offline",
    is_flag=True,
    help="No LLM is used. The draft is simply the prompt that would be sent to an LLM.",
)
def draft(idea: str, dry_run: bool, offline: bool) -> None:
    """Generate a post from the given idea and store it in the database."""
    with _app_context(offline=offline) as app:
        try:
            draft_context = app.draft_context_service.create_context(idea=idea)
            draft_request = DraftRequest(idea=idea, context=draft_context)

            draft_post = app.draft_service.compose(draft_request)

            if dry_run:
                render_dry_run_draft(console, draft_post.generated_content)
            else:
                post = post_from_draft(draft_post)
                app.post_store_manager.save_post(post)
                render_post_panel(console, post, title="Generated Post")
        except ConfigurationError as exc:
            _handle_config_error(exc)


@cli.command("import-csv")
@click.argument(
    "csv_path",
    type=click.Path(exists=True, readable=True, path_type=Path),
)
@click.option(
    "--commit",
    is_flag=True,
    help="Save parsed posts to storage, ignoring row errors.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Display details of parsing and mapping errors if any occur.",
)
def import_csv(csv_path: Path, commit: bool, verbose: bool) -> None:
    """Import posts from a LinkedIn Shares CSV export."""
    with _app_context() as app:
        with console.status("[bold green]Parsing and validating CSV...[/bold green]"):
            result = app.csv_importer.prepare(csv_path)

        render_import_summary(console, result)

        if verbose:
            render_import_errors(console, result)

        if commit:
            with console.status(
                "[bold green]Committing posts to persistence...[/bold green]"
            ):
                commit_result = app.csv_importer.commit(result)

            console.print(
                Panel(
                    f"[bold green]Successfully committed {commit_result.committed_count} posts.[/bold green]",
                    title="Success",
                    border_style="green",
                )
            )
        else:
            console.print(
                "[bold dim]Use --commit flag to import posts to storage.[/bold dim]\n"
            )


@cli.command("list-posts")
@click.option("--limit", "-n", default=10, show_default=True, help="Max posts to show.")
@click.option(
    "--interactive/--no-interactive",
    "-i/-I",
    default=True,
    help="Show posts interactively.",
)
def list_posts(limit: int, interactive: bool) -> None:
    """List recent posts from persistence with optional interactive viewing."""
    with _app_context() as app:
        posts = app.post_storage.get_all(PostGetQuery(limit=limit))

        if not posts:
            console.print("[yellow]No posts found in persistence.[/yellow]")
            return

        console.print(
            f"[bold cyan]Found {len(posts)} posts in persistence.[/bold cyan]\n"
        )

        if not interactive:
            for post in posts:
                render_post_panel(console, post)
            return

        console.print(
            "[yellow]Controls: Press [bold]ENTER[/bold] for next post, "
            "[bold]a[/bold] to show all remaining, or [bold]q[/bold] to quit.[/yellow]\n"
        )

        show_all = False
        for i, post in enumerate(posts, 1):
            render_post_panel(console, post, title=f"Post {i} of {len(posts)}")
            if show_all:
                continue

            char = click.getchar().lower()
            if char == "q":
                console.print("[yellow]Exited viewer.[/yellow]")
                break
            if char == "a":
                show_all = True


if __name__ == "__main__":
    cli()
