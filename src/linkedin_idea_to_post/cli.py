from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from linkedin_idea_to_post.ai_workflow.dry_run_draft_writer import DryRunDraftWriter
from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.config import AppConfig
from linkedin_idea_to_post.drafting.draft_service import DraftService
from linkedin_idea_to_post.linkedin.csv_importer import CsvImporter
from linkedin_idea_to_post.linkedin.csv_parser import CsvParser

console = Console()


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Import LinkedIn shares and turn ideas into new posts."""
    pass


@cli.command("show-config")
def show_config() -> None:
    """Show content of AppConfig."""
    config = AppConfig()

    table = Table(
        title="[bold cyan]Application Configuration[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Section / Key", style="dim", width=20)
    table.add_column("Property", style="green")
    table.add_column("Value", style="yellow")

    for config_key, values in vars(config).items():
        for key, value in values:
            table.add_row(config_key, key, str(value))

    console.print(table)


@cli.command("draft")
@click.argument(
    "idea",
    type=str,
    required=True,
    help="The user's prompt.",
)
def draft(idea: str) -> None:
    """Generates a post from the given idea and stores it in the database."""
    config = AppConfig()
    archive = SqliteArchive(settings=config.archive)
    writer = (
        DryRunDraftWriter()
        if config.drafting.writer == "dry-run"
        else DryRunDraftWriter()
    )
    draft_service = DraftService(
        settings=config.drafting, writer=writer, archive=archive
    )
    post = draft_service.draft(idea)

    content = (
        f"[dim]ID: {post.id} | Origin: {post.origin} | Status: {post.status}[/dim]\n"
        f"[dim]Created: {post.created_at} | Updated: {post.updated_at}[/dim]\n\n"
        f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}"
    )
    console.print(Panel(content, title="Generated Post", border_style="cyan"))


@cli.command("import-csv")
@click.argument(
    "csv_path",
    type=click.Path(exists=True, readable=True, path_type=Path),
)
@click.option(
    "--commit",
    is_flag=True,
    help="Saves the parsed posts to the storage ignoring errors.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Display details of parsing and mapping errors if any occur.",
)
def import_csv(csv_path: Path, commit: bool, verbose: bool) -> None:
    """Import posts from a LinkedIn Shares CSV export.
    By default, it only parses the posts from the file.
    The --commit flag imports the parsed posts to the storage, ignoring parsing and mapping errors.
    """
    config = AppConfig()
    archive = SqliteArchive(settings=config.archive)
    importer = CsvImporter(parser=CsvParser(), archive=archive)

    with console.status("[bold green]Parsing and validating CSV...[/bold green]"):
        result = importer.prepare(csv_path)

    # Summary Panel
    summary_text = (
        f"[bold]Valid posts:[/bold] [green]{len(result.posts)}[/green]\n"
        f"[bold]Parsing errors:[/bold] [red]{len(result.parsing_errors)}[/red]\n"
        f"[bold]Mapping errors:[/bold] [red]{len(result.mapping_errors)}[/red]"
    )
    console.print(Panel(summary_text, title="Import Summary", border_style="blue"))

    if verbose:
        console.print()

        # 1. Render Parsing Errors
        if result.parsing_errors:
            parsing_table = Table(
                title="[bold yellow]Parsing Errors[/bold yellow]",
                show_header=True,
                header_style="bold yellow",
            )
            parsing_table.add_column("Row", style="cyan", width=8, justify="right")
            parsing_table.add_column("Field", style="yellow", width=15)
            parsing_table.add_column("Error Code", style="magenta", width=22)
            parsing_table.add_column("Message", style="white")

            for err in result.parsing_errors:
                parsing_table.add_row(*err.to_str_tuple())
            console.print(parsing_table)
            console.print()

        # 2. Render Mapping Errors
        if result.mapping_errors:
            mapping_table = Table(
                title="[bold red]Mapping Errors[/bold red]",
                show_header=True,
                header_style="bold red",
            )
            mapping_table.add_column("Row", style="cyan", width=8, justify="right")
            mapping_table.add_column("Field", style="yellow", width=15)
            mapping_table.add_column("Error Code", style="magenta", width=22)
            mapping_table.add_column("Message", style="white")

            for map_err in result.mapping_errors:
                row_num = map_err.raw_post.row

                for field_err in map_err.errors:
                    mapping_table.add_row(str(row_num), *field_err.to_str_tuple())

            console.print(mapping_table)
            console.print()

    if commit:
        with console.status("[bold green]Committing posts to archive...[/bold green]"):
            commit_result = importer.commit(result)

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
    """List recent posts from the archive with interactive viewing."""
    config = AppConfig()
    archive = SqliteArchive(settings=config.archive)
    posts = archive.get_all(limit=limit)

    if not posts:
        console.print("[yellow]No posts found in the archive.[/yellow]")
        return

    console.print(f"[bold cyan]Found {len(posts)} posts in archive.[/bold cyan]\n")

    if interactive:
        console.print(
            "[yellow]Controls: Press [bold]ENTER[/bold] for next post, [bold]a[/bold] to show all remaining, or [bold]q[/bold] to quit.[/yellow]\n"
        )

        show_all = False
        for i, post in enumerate(posts, 1):
            if not show_all:
                content = (
                    f"[dim]ID: {post.id} | {post.origin} | Status: {post.status}[/dim]\n"
                    f"[dim]Created: {post.created_at}\nUpdated: {post.updated_at}[/dim]\n\n"
                    f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}\n"
                )
                console.print(
                    Panel(
                        content, title=f"Post {i} of {len(posts)}", border_style="cyan"
                    )
                )

                char = click.getchar().lower()
                if char == "q":
                    console.print("[yellow]Exited viewer.[/yellow]")
                    break
                elif char == "a":
                    show_all = True

            if show_all:
                content = (
                    f"[dim]ID: {post.id} | Origin: {post.origin} | Status: {post.status}[/dim]\n"
                    f"[dim]Created: {post.created_at} | Updated: {post.updated_at}[/dim]\n\n"
                    f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}"
                )
                console.print(
                    Panel(
                        content, title=f"Post {i} of {len(posts)}", border_style="cyan"
                    )
                )
    else:
        for post in posts:
            content = (
                f"[dim]ID: {post.id} | Origin: {post.origin} | Status: {post.status}[/dim]\n"
                f"[dim]Created: {post.created_at} | Updated: {post.updated_at}[/dim]\n\n"
                f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}"
            )
            console.print(Panel(content, border_style="cyan"))


if __name__ == "__main__":
    cli()
