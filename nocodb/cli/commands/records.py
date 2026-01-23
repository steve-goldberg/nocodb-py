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
    view_id: Optional[str] = typer.Option(None, "--view-id", "-v", help="Filter records by view ID"),
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
        if view_id:
            params["viewId"] = view_id

        result = client.records_list_v3(base_id, table_id, params=params)

        records = result.get("records", result.get("list", []))

        if output_json:
            print_json(result, meta={"page": page, "pageSize": page_size})
        else:
            field_names = fields_list.split(",") if fields_list else None
            title = f"Records (Table: {table_id})"
            if view_id:
                title += f" [View: {view_id}]"
            print_records_table(records, title=title, fields=field_names)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_record(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    record_id: str = typer.Argument(..., help="Record ID"),
    fields_list: Optional[str] = typer.Option(None, "--fields", help="Comma-separated field names to return"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a single record by ID."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        # Note: record_get_v3 doesn't support fields param in current SDK
        # but we include it for future compatibility
        result = client.record_get_v3(base_id, table_id, record_id)

        # Filter fields client-side if requested
        if fields_list and result.get("fields"):
            requested_fields = [f.strip() for f in fields_list.split(",")]
            result["fields"] = {k: v for k, v in result["fields"].items() if k in requested_fields}

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
    data: Optional[str] = typer.Option(None, "--data", "-d", help='Record data as JSON: {"fields": {...}}'),
    file: Optional[str] = typer.Option(None, "--file", help="JSON file with records array for batch create"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create one or more records.

    Examples:
        nocodb records create -t tbl_xxx -d '{"Name": "John"}'
        nocodb records create -t tbl_xxx --file records.json
    """
    try:
        if not data and not file:
            print_error("Either --data or --file is required", as_json=output_json)
            raise typer.Exit(1)

        if data and file:
            print_error("Cannot use both --data and --file", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        records_to_create = []

        if file:
            from pathlib import Path
            file_path = Path(file)
            if not file_path.exists():
                print_error(f"File not found: {file}", as_json=output_json)
                raise typer.Exit(1)
            file_content = file_path.read_text()
            parsed = json.loads(file_content)
            # Support both array and single object
            if isinstance(parsed, list):
                records_to_create = parsed
            else:
                records_to_create = [parsed]
        else:
            record_data = json.loads(data)
            records_to_create = [record_data]

        # Normalize records to have "fields" wrapper
        normalized = []
        for rec in records_to_create:
            if "fields" not in rec:
                normalized.append({"fields": rec})
            else:
                normalized.append(rec)

        result = client.records_create_v3(base_id, table_id, normalized)

        if output_json:
            print_json(result)
        else:
            created_list = result if isinstance(result, list) else [result]
            print_success(f"Created {len(created_list)} record(s)")
            if len(created_list) == 1:
                print_single_item(created_list[0])
            else:
                from nocodb.cli.formatters import print_records_table
                print_records_table(created_list, title="Created Records")

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
    record_id: Optional[str] = typer.Argument(None, help="Record ID (not needed with --file)"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help='Update data as JSON: {"fields": {...}}'),
    file: Optional[str] = typer.Option(None, "--file", help="JSON file with records array for batch update"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update one or more records.

    Examples:
        nocodb records update -t tbl_xxx 1 -d '{"Name": "Updated"}'
        nocodb records update -t tbl_xxx --file updates.json

    File format for batch update:
        [{"id": 1, "fields": {"Name": "A"}}, {"id": 2, "fields": {"Name": "B"}}]
    """
    try:
        if not data and not file:
            print_error("Either --data or --file is required", as_json=output_json)
            raise typer.Exit(1)

        if data and file:
            print_error("Cannot use both --data and --file", as_json=output_json)
            raise typer.Exit(1)

        if data and not record_id:
            print_error("Record ID is required when using --data", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        records_to_update = []

        if file:
            from pathlib import Path
            file_path = Path(file)
            if not file_path.exists():
                print_error(f"File not found: {file}", as_json=output_json)
                raise typer.Exit(1)
            file_content = file_path.read_text()
            parsed = json.loads(file_content)
            # Support both array and single object
            if isinstance(parsed, list):
                records_to_update = parsed
            else:
                records_to_update = [parsed]
            # Validate each record has an id
            for rec in records_to_update:
                if "id" not in rec:
                    print_error("Each record in file must have an 'id' field", as_json=output_json)
                    raise typer.Exit(1)
        else:
            update_data = json.loads(data)
            if "fields" not in update_data:
                update_data = {"fields": update_data}
            update_data["id"] = int(record_id) if record_id.isdigit() else record_id
            records_to_update = [update_data]

        # Normalize records to have "fields" wrapper
        normalized = []
        for rec in records_to_update:
            if "fields" not in rec:
                rec_id = rec.pop("id")
                normalized.append({"id": rec_id, "fields": rec})
            else:
                normalized.append(rec)

        result = client.records_update_v3(base_id, table_id, normalized)

        if output_json:
            print_json(result)
        else:
            updated_list = result if isinstance(result, list) else [result]
            print_success(f"Updated {len(updated_list)} record(s)")

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
    record_id: Optional[str] = typer.Argument(None, help="Record ID (not needed with --ids)"),
    ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated record IDs for batch delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete one or more records.

    Examples:
        nocodb records delete -t tbl_xxx 1
        nocodb records delete -t tbl_xxx --ids 1,2,3,4,5
    """
    try:
        if not record_id and not ids:
            print_error("Either record_id argument or --ids option is required", as_json=output_json)
            raise typer.Exit(1)

        if record_id and ids:
            print_error("Cannot use both record_id argument and --ids option", as_json=output_json)
            raise typer.Exit(1)

        # Parse record IDs
        if ids:
            record_ids = []
            for part in ids.split(","):
                part = part.strip()
                if part:
                    record_ids.append(int(part) if part.isdigit() else part)
        else:
            record_ids = [int(record_id) if record_id.isdigit() else record_id]

        if not force and not output_json:
            if len(record_ids) == 1:
                confirm = typer.confirm(f"Delete record #{record_ids[0]}?")
            else:
                confirm = typer.confirm(f"Delete {len(record_ids)} records?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.records_delete_v3(base_id, table_id, record_ids)

        if output_json:
            print_json(result)
        else:
            print_success(f"Deleted {len(record_ids)} record(s)")

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
