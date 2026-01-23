"""Field management commands for NocoDB CLI."""

import json
from pathlib import Path
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
                ("type", "Type"),
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
    title: Optional[str] = typer.Option(None, "--title", help="Field title"),
    field_type: Optional[str] = typer.Option(None, "--type", help="Field type (SingleLineText, Number, Email, etc.)"),
    options_json: Optional[str] = typer.Option(None, "--options", "-o", help="Field options as JSON"),
    file: Optional[str] = typer.Option(None, "--file", help="JSON file with fields array for batch create"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create one or more fields.

    Examples:
        nocodb fields create -t tbl_xxx --title "Email" --type Email
        nocodb fields create -t tbl_xxx --file schema.json

    File format for batch create:
        [{"title": "Email", "type": "Email"}, {"title": "Name", "type": "SingleLineText"}]
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        if file:
            # Batch create from file
            file_path = Path(file)
            if not file_path.exists():
                print_error(f"File not found: {file}", as_json=output_json)
                raise typer.Exit(1)

            file_content = file_path.read_text()
            fields_to_create = json.loads(file_content)
            if not isinstance(fields_to_create, list):
                fields_to_create = [fields_to_create]

            if not fields_to_create:
                print_error("No fields to create (empty array)", as_json=output_json)
                raise typer.Exit(1)

            results = []
            errors = []
            for i, field_config in enumerate(fields_to_create, 1):
                try:
                    result = client.field_create_v3(base_id, table_id, field_config)
                    results.append(result)
                    if not output_json:
                        print_success(f"[{i}/{len(fields_to_create)}] Created: {field_config.get('title')}")
                except Exception as e:
                    errors.append({"field": field_config.get("title"), "error": str(e)})
                    if not output_json:
                        print_error(f"[{i}/{len(fields_to_create)}] Failed: {field_config.get('title')} - {e}")

            if output_json:
                print_json({"created": results, "errors": errors})
            else:
                print_success(f"Created {len(results)} field(s), {len(errors)} error(s)")
        else:
            # Single field create
            if not title or not field_type:
                print_error("--title and --type are required for single field create (or use --file)", as_json=output_json)
                raise typer.Exit(1)

            body = {"title": title, "type": field_type}
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
        print_error(f"Invalid JSON: {e}", as_json=output_json)
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
    field_id: Optional[str] = typer.Argument(None, help="Field ID (not needed with --ids)"),
    ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated field IDs for batch delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete one or more fields.

    Examples:
        nocodb fields delete fld_xxx
        nocodb fields delete --ids fld_xxx,fld_yyy,fld_zzz --force
    """
    try:
        if not field_id and not ids:
            print_error("Either field_id argument or --ids option is required", as_json=output_json)
            raise typer.Exit(1)

        if field_id and ids:
            print_error("Cannot use both field_id argument and --ids option", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        if ids:
            # Batch delete
            field_ids = [fid.strip() for fid in ids.split(",") if fid.strip()]

            if not field_ids:
                print_error("No field IDs provided", as_json=output_json)
                raise typer.Exit(1)

            if not force and not output_json:
                confirm = typer.confirm(f"Delete {len(field_ids)} field(s)? This cannot be undone.")
                if not confirm:
                    print_error("Cancelled", as_json=output_json)
                    raise typer.Exit(0)

            results = []
            errors = []
            for i, fid in enumerate(field_ids, 1):
                try:
                    client.field_delete_v3(base_id, fid)
                    results.append(fid)
                    if not output_json:
                        print_success(f"[{i}/{len(field_ids)}] Deleted: {fid}")
                except Exception as e:
                    errors.append({"field_id": fid, "error": str(e)})
                    if not output_json:
                        print_error(f"[{i}/{len(field_ids)}] Failed: {fid} - {e}")

            if output_json:
                print_json({"deleted": results, "errors": errors})
            else:
                print_success(f"Deleted {len(results)} field(s), {len(errors)} error(s)")
        else:
            # Single field delete
            if not force and not output_json:
                confirm = typer.confirm(f"Delete field {field_id}? This cannot be undone.")
                if not confirm:
                    print_error("Cancelled", as_json=output_json)
                    raise typer.Exit(0)

            result = client.field_delete_v3(base_id, field_id)

            if output_json:
                print_json(result or {"deleted": True})
            else:
                print_success(f"Deleted field {field_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
