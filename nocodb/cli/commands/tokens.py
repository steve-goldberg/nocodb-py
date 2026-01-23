"""API token commands for NocoDB CLI."""

import typer
from rich.console import Console
from rich.table import Table

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="API token management")
console = Console()


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_tokens(
    ctx: typer.Context,
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all API tokens."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.tokens_list()
        tokens = result.get("tokens", result.get("list", []))

        if output_json:
            print_json(result)
        else:
            if not tokens:
                console.print("[dim]No API tokens found[/dim]")
                return

            table = Table(title="API Tokens")
            table.add_column("ID", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Token", style="dim")

            for token in tokens:
                token_id = str(token.get("id", ""))
                description = token.get("description", "")
                # Show only first/last few chars of token for security
                token_value = token.get("token", "")
                if token_value and len(token_value) > 12:
                    masked_token = f"{token_value[:6]}...{token_value[-4:]}"
                else:
                    masked_token = token_value

                table.add_row(token_id, description, masked_token)

            console.print(table)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_token(
    ctx: typer.Context,
    description: str = typer.Option(..., "--description", "-d", help="Token description"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new API token.

    Example:
        nocodb tokens create -d "CI/CD Pipeline Token"
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.token_create({"description": description})

        if output_json:
            print_json(result)
        else:
            print_success("Created API token")
            # Show full token on creation (only time it's visible)
            console.print(f"\n[bold yellow]Token:[/bold yellow] {result.get('token', 'N/A')}")
            console.print("[dim]Save this token - it won't be shown again![/dim]\n")
            print_single_item(result, title="Token Details")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_token(
    ctx: typer.Context,
    token_id: str = typer.Argument(..., help="Token ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete an API token.

    Example:
        nocodb tokens delete tok_xxx
        nocodb tokens delete tok_xxx --force
    """
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete token {token_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.token_delete(token_id)

        if output_json:
            print_json({"deleted": token_id, "success": True})
        else:
            print_success(f"Deleted token {token_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
