"""Webhook management commands for NocoDB CLI.

Note: Only list and delete operations are supported via the v2 API.
Create, read, update, and test operations are not available in self-hosted NocoDB.

However, webhook filters, logs, and sample payload endpoints are available.
"""

from typing import Optional

import typer

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_items_table,
    print_json,
    print_single_item,
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


@app.command("logs")
def list_webhook_logs(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List execution logs for a webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_logs(hook_id)

        logs = result.get("list", result.get("logs", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("type", "Type"),
                ("event", "Event"),
                ("created_at", "Created"),
                ("response", "Response"),
            ]
            print_items_table(logs, title="Webhook Logs", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("sample")
def get_webhook_sample(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    event: str = typer.Option("records", "--event", "-e", help="Event type (e.g., records)"),
    operation: str = typer.Option("insert", "--operation", "-o", help="Operation: insert, update, delete"),
    version: str = typer.Option("v2", "--version", "-v", help="Payload version (v1 or v2)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a sample webhook payload for preview.

    Examples:
        nocodb webhooks sample -t tbl_xxx
        nocodb webhooks sample -t tbl_xxx --event records --operation update
        nocodb webhooks sample -t tbl_xxx -e records -o delete
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_sample_payload(table_id, event, operation, version)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Sample Payload ({event}.{operation})")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


# Webhook Filters subcommands
filters_app = typer.Typer(no_args_is_help=True, help="Webhook filter operations")
app.add_typer(filters_app, name="filters")


@filters_app.command("list")
def list_webhook_filters(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List filters for a webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_filters_list(hook_id)

        filters = result.get("list", result.get("filters", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_column_id", "Column"),
                ("comparison_op", "Operator"),
                ("value", "Value"),
            ]
            print_items_table(filters, title="Webhook Filters", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("create")
def create_webhook_filter(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    column_id: str = typer.Option(..., "--column", "-c", help="Column/field ID"),
    operator: str = typer.Option(..., "--op", "-o", help="Comparison operator (eq, neq, like, etc.)"),
    value: str = typer.Option(..., "--value", help="Filter value"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a filter for a webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {
            "fk_column_id": column_id,
            "comparison_op": operator,
            "value": value,
        }

        result = client.webhook_filter_create(hook_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created filter on webhook {hook_id}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
