from pathlib import Path
from typing import Annotated

import click
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.config import AppConfig
from linkedin_idea_to_post.linkedin.csv_importer import CsvImporter
from linkedin_idea_to_post.linkedin.csv_parser import CsvParser

cli = typer.Typer(
    name="linkedin-post",
    help="Import LinkedIn shares and turn ideas into new posts.",
    no_args_is_help=True,
)
console = Console()


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


@cli.command("import-csv")
def import_csv(
    csv_path: Annotated[
        Path,
        typer.Argument(exists=True, readable=True, help="Path to LinkedIn Shares CSV."),
    ],
    commit: Annotated[
        bool,
        typer.Option(
            "--commit", help="Saves the parsed posts to the storage ignoring errors."
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Display details of parsing and mapping errors if any occur.",
        ),
    ] = False,
) -> None:
    """Import posts from a LinkedIn Shares CSV export.
    By default, it only parses the posts from the file.
    The --commit flag imports the parsed posts to the storage, ignoring the parsing and mapping errors.
    """
    config = AppConfig()
    archive = SqliteArchive(db_path=config.archive.db_path)
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

        # 1. Render Parsing Errors (Row-based)
        if result.parsing_errors:
            parsing_table = Table(
                title="[bold yellow]Parsing Errors[/bold yellow]",
                show_header=True,
                header_style="bold yellow",
            )
            parsing_table.add_column("Row", style="cyan", width=8, justify="right")
            parsing_table.add_column("Error Code", style="magenta", width=22)
            parsing_table.add_column("Message", style="white")

            for err in result.parsing_errors:
                parsing_table.add_row(
                    str(err.row),
                    str(err.code.value if hasattr(err.code, "value") else err.code),
                    err.message,
                )
            console.print(parsing_table)
            console.print()

        # 2. Render Mapping Errors (Raw Post + Field Errors)
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
                    mapping_table.add_row(
                        str(row_num),
                        str(field_err.field),
                        str(
                            field_err.code.value
                            if hasattr(field_err.code, "value")
                            else field_err.code
                        ),
                        field_err.message,
                    )
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
def list_posts(
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="Max posts to show.")
    ] = 10,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive/--no-interactive",
            "-i/-I",
            help="Show posts one by one interactively (default: enabled). Use --no-interactive (or -I) to print all at once.",
        ),
    ] = True,
) -> None:
    """List recent posts from the archive with interactive viewing."""
    config = AppConfig()
    archive = SqliteArchive(db_path=config.archive.db_path)
    posts = archive.get_all(limit=limit)

    if not posts:
        console.print("[yellow]No posts found in the archive.[/yellow]")
        raise typer.Exit()

    console.print(f"[bold cyan]Found {len(posts)} posts in archive.[/bold cyan]\n")

    if interactive:
        console.print(
            "[yellow]Controls: Press [bold]ENTER[/bold] for next post, [bold]a[/bold] to show all remaining, or [bold]q[/bold] to quit.[/yellow]\n"
        )

        show_all = False
        for i, post in enumerate(posts, 1):
            if not show_all:
                # Render post inside a rich panel
                content = (
                    f"[dim]ID: {post.id} | {post.origin} - {post.status} [/dim]\n"
                    f"[dim]Created: {post.created_at}\nUpdated: {post.updated_at}[/dim]\n\n"
                    f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}\n"
                )
                console.print(
                    Panel(
                        content, title=f"Post {i} of {len(posts)}", border_style="cyan"
                    )
                )

                # Wait for user input
                char = click.getchar().lower()
                if char == "q":
                    console.print("[yellow]Exited viewer.[/yellow]")
                    break
                elif char == "a":
                    show_all = True
                    # Fall through to print the rest without prompting

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
        # Standard non-interactive view using a loop or typer's pager
        for post in posts:
            content = (
                f"[dim]ID: {post.id} | Origin: {post.origin} | Status: {post.status}[/dim]\n"
                f"[dim]Created: {post.created_at} | Updated: {post.updated_at}[/dim]\n\n"
                f"[bold yellow]{post.title}[/bold yellow]\n\n{post.body}"
            )
            console.print(Panel(content, border_style="cyan"))


if __name__ == "__main__":
    cli()
