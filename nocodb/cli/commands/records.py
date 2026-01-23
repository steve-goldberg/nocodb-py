"""Record CRUD commands for NocoDB CLI."""

import json
from typing import Optional

import typer

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_records_table,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Record operations")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_records(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    filter_str: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter expression: (field,op,value)"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort field (prefix with - for desc)"),
    fields_list: Optional[str] = typer.Option(None, "--fields", help="Comma-separated field names to return"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(25, "--page-size", "-n", help="Results per page"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List records from a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        params = {"page": page, "pageSize": page_size}
        if filter_str:
            params["where"] = filter_str
        if sort:
            params["sort"] = sort
        if fields_list:
            params["fields"] = fields_list

        result = client.records_list_v3(base_id, table_id, params=params)

        records = result.get("records", result.get("list", []))

        if output_json:
            print_json(result, meta={"page": page, "pageSize": page_size})
        else:
            field_names = fields_list.split(",") if fields_list else None
            print_records_table(records, title=f"Records (Table: {table_id})", fields=field_names)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_record(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    record_id: str = typer.Argument(..., help="Record ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a single record by ID."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.record_get_v3(base_id, table_id, record_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Record #{record_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_record(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    data: str = typer.Option(..., "--data", "-d", help='Record data as JSON: {"fields": {...}}'),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new record."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        record_data = json.loads(data)
        if "fields" not in record_data:
            record_data = {"fields": record_data}

        result = client.records_create_v3(base_id, table_id, [record_data])

        if output_json:
            print_json(result)
        else:
            created = result[0] if isinstance(result, list) else result
            print_success(f"Created record #{created.get('id', 'unknown')}")
            print_single_item(created)

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}", as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_record(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    record_id: str = typer.Argument(..., help="Record ID"),
    data: str = typer.Option(..., "--data", "-d", help='Update data as JSON: {"fields": {...}}'),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update an existing record."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        update_data = json.loads(data)
        if "fields" not in update_data:
            update_data = {"fields": update_data}
        update_data["id"] = int(record_id) if record_id.isdigit() else record_id

        result = client.records_update_v3(base_id, table_id, [update_data])

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated record #{record_id}")

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}", as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_record(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    record_id: str = typer.Argument(..., help="Record ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a record."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete record #{record_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        record_ids = [{"id": int(record_id) if record_id.isdigit() else record_id}]
        result = client.records_delete_v3(base_id, table_id, record_ids)

        if output_json:
            print_json(result)
        else:
            print_success(f"Deleted record #{record_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("count")
def count_records(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    filter_str: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter expression"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Count records in a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        params = {}
        if filter_str:
            params["where"] = filter_str

        result = client.records_count_v3(base_id, table_id, params=params)

        if output_json:
            print_json(result)
        else:
            count = result.get("count", result)
            from rich.console import Console
            Console().print(f"Count: [bold]{count}[/bold]")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
