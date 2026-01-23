"""Webhook management commands for NocoDB CLI.

Note: Only list and delete operations are supported via the v2 API.
Create, read, update, and test operations are not available in self-hosted NocoDB.
"""

import typer

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_items_table,
    print_json,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Webhook management (list, delete only)")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_webhooks(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all webhooks for a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhooks_list(table_id)

        webhooks = result.get("list", result.get("hooks", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("title", "Title"),
                ("event", "Event"),
                ("active", "Active"),
            ]
            print_items_table(webhooks, title="Webhooks", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_webhook(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a webhook."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete webhook {hook_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_delete(hook_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted webhook {hook_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
