"""Field management commands for NocoDB CLI."""

import json
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

app = typer.Typer(no_args_is_help=True, help="Field management")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_fields(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all fields in a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.table_read_v3(base_id, table_id)
        fields = result.get("columns", result.get("fields", []))

        if output_json:
            print_json({"fields": fields})
        else:
            columns = [
                ("id", "ID"),
                ("title", "Title"),
                ("uidt", "Type"),
                ("pv", "Primary"),
            ]
            print_items_table(fields, title="Fields", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_field(
    ctx: typer.Context,
    field_id: str = typer.Argument(..., help="Field ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get field details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.field_read_v3(base_id, field_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Field: {result.get('title', field_id)}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_field(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    title: str = typer.Option(..., "--title", help="Field title"),
    field_type: str = typer.Option(..., "--type", help="Field type (SingleLineText, Number, Email, etc.)"),
    options_json: Optional[str] = typer.Option(None, "--options", "-o", help="Field options as JSON"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new field."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        body = {"title": title, "uidt": field_type}
        if options_json:
            options = json.loads(options_json)
            body.update(options)

        result = client.field_create_v3(base_id, table_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created field: {result.get('title', 'unknown')}")
            print_single_item(result)

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON for options: {e}", as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_field(
    ctx: typer.Context,
    field_id: str = typer.Argument(..., help="Field ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    options_json: Optional[str] = typer.Option(None, "--options", "-o", help="Field options as JSON"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a field."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        body = {}
        if title:
            body["title"] = title
        if options_json:
            options = json.loads(options_json)
            body.update(options)

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.field_update_v3(base_id, field_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated field {field_id}")

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON for options: {e}", as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_field(
    ctx: typer.Context,
    field_id: str = typer.Argument(..., help="Field ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a field."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete field {field_id}? This cannot be undone.")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.field_delete_v3(base_id, field_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted field {field_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
