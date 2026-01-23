"""Webhook management commands for NocoDB CLI."""

import json
from typing import Optional

import typer

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_items_table,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Webhook management")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


WEBHOOK_EVENTS = [
    "after.insert",
    "after.update",
    "after.delete",
    "after.bulkInsert",
    "after.bulkUpdate",
    "after.bulkDelete",
]


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


@app.command("get")
def get_webhook(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get webhook details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_read(hook_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Webhook: {result.get('title', hook_id)}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_webhook(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    title: str = typer.Option(..., "--title", help="Webhook title"),
    event: str = typer.Option(..., "--event", "-e", help="Event: after.insert, after.update, after.delete, etc."),
    url: str = typer.Option(..., "--url", help="Webhook URL"),
    active: bool = typer.Option(True, "--active/--inactive", help="Whether webhook is active"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        if event not in WEBHOOK_EVENTS:
            print_error(f"Invalid event: {event}. Must be one of: {', '.join(WEBHOOK_EVENTS)}", as_json=output_json)
            raise typer.Exit(1)

        body = {
            "title": title,
            "event": event,
            "notification": {
                "type": "URL",
                "payload": {
                    "method": "POST",
                    "body": "{{ json data }}",
                    "headers": [{"name": "Content-Type", "value": "application/json"}],
                    "path": url,
                },
            },
            "active": active,
        }

        result = client.webhook_create(table_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created webhook: {result.get('title', 'unknown')}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_webhook(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    url: Optional[str] = typer.Option(None, "--url", help="New URL"),
    active: Optional[bool] = typer.Option(None, "--active/--inactive", help="Enable/disable webhook"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if title:
            body["title"] = title
        if url:
            body["notification"] = {
                "type": "URL",
                "payload": {
                    "method": "POST",
                    "body": "{{ json data }}",
                    "headers": [{"name": "Content-Type", "value": "application/json"}],
                    "path": url,
                },
            }
        if active is not None:
            body["active"] = active

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.webhook_update(hook_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated webhook {hook_id}")

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


@app.command("test")
def test_webhook(
    ctx: typer.Context,
    hook_id: str = typer.Argument(..., help="Webhook ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Test a webhook."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.webhook_test(hook_id)

        if output_json:
            print_json(result)
        else:
            print_success(f"Webhook {hook_id} test sent")
            if result:
                print_single_item(result, title="Test Result")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
