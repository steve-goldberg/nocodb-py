"""Table management commands for NocoDB CLI."""

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

app = typer.Typer(no_args_is_help=True, help="Table management")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_tables(
    ctx: typer.Context,
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all tables in the base."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.tables_list_v3(base_id)

        tables = result.get("list", result.get("tables", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("title", "Title"),
                ("type", "Type"),
                ("meta", "Meta"),
            ]
            print_items_table(tables, title="Tables", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_table(
    ctx: typer.Context,
    table_id: str = typer.Argument(..., help="Table ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get table details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.table_read_v3(base_id, table_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Table: {result.get('title', table_id)}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_table(
    ctx: typer.Context,
    title: str = typer.Option(..., "--title", help="Table title"),
    columns_json: Optional[str] = typer.Option(None, "--columns", "-c", help="Columns as JSON array"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        body = {"title": title}
        if columns_json:
            body["columns"] = json.loads(columns_json)

        result = client.table_create_v3(base_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created table: {result.get('title', 'unknown')}")
            print_single_item(result)

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON for columns: {e}", as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_table(
    ctx: typer.Context,
    table_id: str = typer.Argument(..., help="Table ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        body = {}
        if title:
            body["title"] = title

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.table_update_v3(base_id, table_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated table {table_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_table(
    ctx: typer.Context,
    table_id: str = typer.Argument(..., help="Table ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a table."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete table {table_id}? This cannot be undone.")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.table_delete_v3(base_id, table_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted table {table_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
