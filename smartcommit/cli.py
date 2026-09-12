"""
SmartCommit CLI entry point.

Usage:
    smartcommit            -> generate message, ask for confirmation, commit
    smartcommit --yes      -> auto-accept, no prompt
    smartcommit --dry-run  -> just print the message, don't commit
"""

import typer
from rich import print
from rich.panel import Panel

from smartcommit.config import load_config
from smartcommit.git_utils import (
    get_repo,
    get_staged_diff,
    commit,
    NotAGitRepoError,
    NoStagedChangesError,
)
from smartcommit.llm import generate_commit_message

app = typer.Typer(help="Generate Conventional Commit messages from your staged diff using AI.")


@app.command()
def main(
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-accept the generated message, skip confirmation."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the message but do not commit."),
):
    """Generate a commit message from staged changes and commit."""
    try:
        config = load_config()
    except ValueError as e:
        print(f"[bold red]Config error:[/bold red] {e}")
        raise typer.Exit(code=1)

    try:
        repo = get_repo(".")
        diff = get_staged_diff(repo)
    except NotAGitRepoError as e:
        print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except NoStagedChangesError as e:
        print(f"[bold yellow]Nothing to commit:[/bold yellow] {e}")
        raise typer.Exit(code=1)

    print("[dim]Analyzing staged diff...[/dim]")

    try:
        message = generate_commit_message(diff, config)
    except RuntimeError as e:
        print(f"[bold red]LLM error:[/bold red] {e}")
        raise typer.Exit(code=1)

    print(Panel(message, title="Suggested commit message", border_style="green"))

    if dry_run:
        print("[dim](dry run -- not committing)[/dim]")
        raise typer.Exit(code=0)

    if not yes:
        choice = typer.prompt(
            "[Y]es / [E]dit / [N]o", default="Y", show_default=False
        ).strip().lower()

        if choice.startswith("n"):
            print("[yellow]Aborted. Nothing committed.[/yellow]")
            raise typer.Exit(code=0)
        elif choice.startswith("e"):
            message = typer.prompt("Edit message", default=message)

    sha = commit(repo, message)
    print(f"[bold green]Committed[/bold green] ({sha}): {message}")


if __name__ == "__main__":
    app()
